import re
import time
import sys
import pycountry
import os
import pyperclip
import pyautogui
import phonenumbers
import random
import json

from colorama import init, Fore
from phonenumbers.phonenumberutil import NumberParseException
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from plyer import notification
from selenium.webdriver.support.ui import Select
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer, util


@dataclass
class Config:
    """ Configuration Data """
    EMAIL_PATTERN: str = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    WEB_DRIVER_TIMEOUT: int = 10
    GLASSDOOR_LANDING_PAGE: str = str()
    FIREFOX_PROFILE_PATH: str = str()
    FIREFOX_PROFILE_PATH_PATTERN: str = r"^C:\\Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+$"
    SLEEP_TIMEOUT: (int | float) = random.uniform(1, 4)
    RESUME_PATH: str = str()
    POSTAL_CODE_PATTERN: str = r"^(?!.*\s.*\s)[A-Za-z0-9\s]{4,7}$"
    FIREFOX_DRIVER_PATH = "geckodriver-v0.36.0-win64/geckodriver.exe"
    WEB_DRIVER_SCROLL_BEHAVIOUR: str = "arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});"
    SAVE_JOB_PREFERENCE: str = str()
    COMMUTE_OPTIONS: dict = field(default_factory=lambda : {
        1: "Yes, I can make the commute",
        2: "Yes, I am planning to relocate",
        3: "Yes, but I need relocation assistance",
        4: "No"
    })

@dataclass
class ScreenerQuestions:
    """ Data Class For Screener Questions """
    ELIGIBLE_TO_WORK: str = str()
    COMMUTE_TO_WORK: str = str()
    BACHELORS_OR_DIPLOMA: str = str()
    MAJOR_OR_PROGRAM: str = str()

@dataclass
class JobHistory:
    """ Previous Job Data """
    title: str = str()
    company: str = str()
    experience: int = int()
    commute: str = str()

@dataclass
class Address:
    """ User Address """
    street_address: str = str()
    state: str = str()
    city: str = str()
    postal_code: str = str()
    country: str = str()

@dataclass
class User:
    """ User Data """
    first_name: str = str()
    last_name: str = str()
    phone_number: str = str()
    address: Address = field(default_factory=Address)
    past_job: JobHistory = field(default_factory=JobHistory)
    screener_questions: ScreenerQuestions = field(default_factory=ScreenerQuestions)

class GlassDoor:
    def __init__(self) -> None:
        init(autoreset=True)

        self.web_driver: Optional[Firefox] = None
        self.config: Config = Config()
        self.user: User = User()
        self.glassdoor_input_data = None
        self.model: Optional[SentenceTransformer] = None

    @staticmethod
    def _show_options() -> None:
        """ Display different options to Apply for a Job """
        print(Fore.GREEN + "\n***** GlassDoor Job Application *****")

        options: list[str] = ["Exit", "Apply Using URL", "Apply with Job Search"]

        for index, value in enumerate(options):
            print(Fore.MAGENTA + f"{index}. {value}")

    def _initialize_web_driver(self) -> None:
        """ Initialize Firefox Web Driver """
        if self._read_firefox_profile_path():
            filefox_profile_path = self.glassdoor_input_data["config"]["firefox profile path"]

            # Configure Firefox options
            options: Options = Options()
            options.set_preference("profile", filefox_profile_path)
            options.add_argument("-profile")
            options.add_argument(filefox_profile_path)

            # Setup Geckodriver Service
            if not Path(self.config.FIREFOX_DRIVER_PATH).exists():
                raise FileNotFoundError(Fore.RED + "Geckodriver not Found!")

            service: Service =Service(executable_path=self.config.FIREFOX_DRIVER_PATH)

            # Initialize web driver
            self.web_driver = Firefox(service=service, options=options)
        else:
            self._display_notification(title="Validation Failed!", message="Invalid Firefox Profile Path!")
            sys.exit(1)

    @staticmethod
    def _display_notification(title:str ="", message: str="", timeout: int=10) -> None:
        """ Displays Custom Notifications to the User """
        try:
            notification.notify(title=title, message=message, app_name="AutoApply", timeout=timeout)
        except Exception as e:
            print(Fore.RED + f"Unable to show notifications. {e}")

    def _fill_address_form(self) -> None:
        """ Fill in or Update the User Address """
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Select Country
        if self._read_country():
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Change']]"))).click()
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-country-list")))

            select = Select(self.web_driver.find_element(By.ID, "location-fields-country-list"))
            select.select_by_visible_text(self.glassdoor_input_data["user"]["address"]["country"].title())

        # Enter Postal Code
        if self._read_postal_code():
            self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-postal-code-input"))
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-postal-code-input"))).send_keys(self.glassdoor_input_data["user"]["address"]["postal code"].upper())

        # Enter City & State
        if self._read_city() or self._read_state():
            self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-locality-input"))
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-locality-input"))).send_keys(self.glassdoor_input_data["user"]["address"]["city"].title() + ", " + self.glassdoor_input_data["user"]["address"]["state"].title())

        # Enter Street Address
        if self._read_street_address():
            self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-address-input"))
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-address-input"))).send_keys(self.glassdoor_input_data["user"]["address"]["street address"].title())

        # Click Continue button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

    def _upload_resume(self) -> None:
        """
            Upload the Resume for the current Job
            The Upload Resume option will open file explorer to upload a file and Selenium doesn't have that functionality
            To bypass this issue, 'PyAutoGUI' has been used
         """
        time.sleep(self.config.SLEEP_TIMEOUT)

        if self._read_resume_path():
            # Click on the existing Resume
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[@data-testid='FileResumeCardHeader-title']"))).click()

            # Scroll to "Resume Option" button
            self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='ResumeOptionsMenu-btn']"))
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='ResumeOptionsMenu-btn']"))).click()

            # Click on "Upload a Different File" option
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Upload a different file']"))).click()

            # Copy & Paste the Resume path
            time.sleep(self.config.SLEEP_TIMEOUT)
            pyperclip.copy(self.config.RESUME_PATH)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")

            # Click on "Continue" buton
            time.sleep(self.config.SLEEP_TIMEOUT)
            continue_buttons = WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//button[.//span[normalize-space()='Continue']]")))

            for index, button in enumerate(continue_buttons, start=1):
                try:
                    if button.is_enabled():
                        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, button)
                        self.web_driver.find_element(By.XPATH, f"(//button[.//span[normalize-space()='Continue']])[{index}]").click()

                        break
                except ElementNotInteractableException:
                    print(Fore.RED + f"Failed to click button #{index}")
        else:
            self._display_notification(title="Validation Failed!", message="File Not Found!")
            sys.exit(1)

    def _fill_work_experience(self) -> None:
        """ Fill the relevant past Job Experience """
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Enter Past Job Title
        if self._read_past_job_title():
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "job-title-input"))).send_keys(self.glassdoor_input_data["user"]["job history"]["title"].title())
            pyautogui.moveTo(300, 300)
            pyautogui.click()

        # Enter Past Company Name
        if self._read_past_job_company():
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "company-name-input"))).send_keys(self.glassdoor_input_data["user"]["job history"]["company"].title())
            pyautogui.moveTo(300, 300)
            pyautogui.click()

        # Click on the "Continue" button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

    def _validate_required_question_1(self, index: int) -> None:
        """ Validate the 'Required' question 'Do you speak English?' """
        text = self.glassdoor_input_data["screener questions"]["required questions"]["Do you speak English?"].title()

        if text.__eq__("Yes") or text.__eq__("No"):
            print(Fore.YELLOW + "Do you speak English? is valid.")

            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//label[.//span[text()='{text}']]/input"))).click()
        else:
            print(Fore.RED + "Invalid 'Required Question 1'!")

            self.web_driver.quit()
            self._display_notification(title="Validation Failed!", message="Required questions are mandatory.")
            sys.exit(1)

    def _fill_required_questions(self, original_emb, index) -> None:
        """ Fill Mandatory Screener questions """
        for question, answer in self.glassdoor_input_data["screener questions"]["required questions"].items():
            q_emb = self.model.encode(question, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

            if similarity * 100 > 75:
                match question:
                    case "Do you speak English?":
                        self._validate_required_question_1(index=index)
                    case _:
                        print(Fore.RED + "Invalid Option!")

    def _validate_other_question_1(self, index: int) -> None:
        """ Validate the 'Other' question 'Please list 2-3 dates and time ranges that you could do an interview.' """
        text = self.glassdoor_input_data["screener questions"]["other questions"]["Please list 2-3 dates and time ranges that you could do an interview."]

        if text:
            interview_dates = "\n".join(text)

            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//textarea"))).clear()
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//textarea"))).send_keys(interview_dates)

            print(Fore.YELLOW + "Please list 2-3 dates and time ranges that you could do an interview. is valid.")
        else:
            print(Fore.RED + "Invalid Data Format for question 'Please list 2-3 dates and time ranges that you could do an interview.'")

    def _fill_other_questions(self, original_emb, index) -> None:
        """ Fill Non-Mandatory questions """
        for question, answer in self.glassdoor_input_data["screener questions"]["other questions"].items():
            q_emb = self.model.encode(question, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

            if similarity * 100 > 75:
                match question:
                    case "Please list 2-3 dates and time ranges that you could do an interview.":
                        self._validate_other_question_1(index=index)
                    case _:
                        print(Fore.RED + "Invalid Option!")

    def _fill_screener_questions(self) -> None:
        """ Answer Screener Questions during an Application process """
        # Get all Questions
        time.sleep(self.config.SLEEP_TIMEOUT)

        all_questions = WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT * 3).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[starts-with(@id, 'q_')]")))

        # Get all the Questions, Validate, & Enter the appropriate Answers
        for index in range(len(all_questions)):
            time.sleep(self.config.SLEEP_TIMEOUT)

            try:
                self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span[@data-testid='rich-text']/span"))

                label_text = self.web_driver.find_element(By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span[@data-testid='rich-text']/span").text
                original_emb = self.model.encode(label_text, convert_to_tensor=True)

                for question_type, questions in self.glassdoor_input_data["screener questions"].items():
                    if question_type.__eq__("required questions"):
                        self._fill_required_questions(original_emb=original_emb, index=index)
                    else:
                        self._fill_other_questions(original_emb=original_emb, index=index)
            except Exception as e:
                print(Fore.RED + f"Error: {e}")

        # Click 'Continue' button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button/span[text()='Continue']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Continue']"))).click()

    def _submit_job_application(self) -> None:
        """ Review & Submit the Job Application """
        # Click on the Submit button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button/span[text()='Submit your application']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Submit your application']")))

    def _fill_contact_information(self) -> None:
        """ Fill the Contact Information form """
        # Enter First Name
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//input[@data-testid='name-fields-first-name-input'"))).send_keys(self.user.first_name)

        # Enter Last Name
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//input[@data-testid='name-fields-last-name-input']"))).send_keys(self.user.last_name)

        # Click the Country dropdown
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.find_element(By.XPATH, "//button[@aria-haspopup='listbox']").click()

        # Find & elect the Country
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//li[@role='option']//span[contains(text(),'{self.user.address.country}')]"))).click()

        # Enter Phone Number
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='tel']"))).send_keys(self.user.phone_number)

        # Click on the Continue button
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[data-testid='continue-button']"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[data-testid='continue-button']"))).click()

    def _process_easy_apply(self) -> None:
        """ Automate the Job with 'Easy Apply' button """
        # Click on the "Easy Apply" button
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test='easyApply']"))).click()
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Switch to a new tab
        self.web_driver.switch_to.window(self.web_driver.window_handles[1])
        time.sleep(self.config.SLEEP_TIMEOUT)

        while True:
            page_title: str = self.web_driver.title

            if "Just a moment" in page_title:
                self._display_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
                self.web_driver.quit()
                sys.exit()
            elif "Add or update your address" in page_title:
                self._fill_address_form()
            elif "Upload a resume for this application" in page_title:
                self._upload_resume()
            elif "Add relevant work experience information" in page_title:
                self._fill_work_experience()
            elif "Answer Screener Questions from the employer" in page_title:
                self._fill_screener_questions()
            elif "Add or update your contact information" in page_title:
                self._fill_contact_information()
            elif "Review the contents of this job application" in page_title:
                self._submit_job_application()
                self._display_notification(title="Success", message="Applied to Job Successfully")

                break
            elif "Just a moment" in self.web_driver.title:
                self._display_notification(title="Unable to Apply for Job",
                                           message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
                self.web_driver.quit()
                sys.exit()

            time.sleep(self.config.SLEEP_TIMEOUT * 2)

    @staticmethod
    def _read_job_url(number: int) -> str:
        """
            Reads Job URL
            :return: Job URL
        """
        while True:
            url: str = input(Fore.BLUE + f"\nEnter the URL for Job {number + 1}: ").strip()

            if bool(url) and url.startswith("http") and url.__contains__("glassdoor"):
                return url

            print(Fore.RED + "Invalid Job URL! Please try again.")

    @staticmethod
    def _number_of_jobs_to_apply() -> int:
        """
            Read a number to apply for Jobs
        :return: Number of Jobs to apply
        """
        while True:
            try:
                number_of_jobs: int = int(input(Fore.BLUE + "\nHow many jobs you want to apply?: "))

                if number_of_jobs > 0:
                    return number_of_jobs

                print(Fore.RED + "Invalid Input! Number should eb greater than 0.")
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a number.")

    def _handle_application_button(self) -> None:
        """ Detects the Job Application button available on the page """
        button_selectors: dict[str: str] = {
            "Applied": "(//button[.//span[normalize-space()='Applied']])[1]",
            "Easy Apply": "//button[@data-test='easyApply']",
            "Apply on employer site": "//button[@data-test='applyButton']"
        }

        for text, xpath in button_selectors.items():
            try:
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, xpath)))

                if text.__eq__("Applied"):
                    self._display_notification(title="Can't Apply to this Job!", message="You have already applied to this Job.")
                    self.web_driver.quit()
                elif text.__eq__("Easy Apply"):
                    self._process_easy_apply()
                    self._save_job()
                else:
                    pass

                return
            except TimeoutException as e:
                print(e.stacktrace)

        self._display_notification(title="Unable to Apply for Job", message="Unable to find the Button text to apply for the Job.")
        self.web_driver.quit()
        sys.exit()

    def _check_user_login(self) -> bool:
        """ Checks if the user is Logged """
        print(Fore.YELLOW + "\nChecking if the User is Logged In")

        try:
            self.web_driver.find_element(By.XPATH, "//button[@aria-label='sign in']")

            return False
        except NoSuchElementException:
            return True

    def _read_job_details(self) -> list[str]:
        """
            Fetch all the required data to save Job at CareerFlow
            :return: Return a 'List' of 'String' of Job Data
        """
        # Switch to the Job Posing page & copy the Data
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.switch_to.window(self.web_driver.window_handles[0])

        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Show more']"))).click()

        return [self.web_driver.find_element(By.TAG_NAME, "h1").text,
                               self.web_driver.find_element(By.TAG_NAME, "h4").text,
                               self.web_driver.current_url,
                               self.web_driver.find_element(By.XPATH, "//div[@data-test='detailSalary']").text,
                               self.web_driver.find_element(By.XPATH, "//div[@data-test='location']").text,
                               self.web_driver.find_element(By.CSS_SELECTOR, ".Section_sectionComponent__nRsB2.Section_bottomMargin__Fka0J").text]

    def _fill_career_flow_job_form(self, job_data: list[str]) -> None:
        """ Fills the Job Details at CareerFlow """
        # Click on "Job Tracker"
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Job Tracker']"))).click()

        # Click on "Add Job"
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Add Job']"))).click()

        # Enter Job title
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_jobtitle"))).send_keys(job_data[0])

        # Enter Company name
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_companyName"))).send_keys(job_data[1])

        # Enter Job URL
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_joburl"))).send_keys(job_data[2])

        # Click on Status
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ant-select-selector"))).click()
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'ant-select-item-option-content') and text()='Applied']"))).click()
        # WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "rc_select_0"))).send_keys("Applied")

        # Change Status to "Applied"
        # time.sleep(self.config.SLEEP_TIMEOUT)
        # WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'ant-select-item-option')][.='Applied']"))).click()

        # Enter Salary
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_salary"))).send_keys(job_data[3])

        # Enter Job Location
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "basic_location"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_location"))).send_keys(job_data[4])

        # Enter Job Description
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "basic_description"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "basic_description"))).send_keys(job_data[5])

        # Click on Save button
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//span[text()='Submit']"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Submit']"))).click()

    def _save_to_career_flow(self) -> None:
        """ Save Job on CareerFlow """
        # Open CareerFlow Page
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script("window.open('https://app.careerflow.ai/board');")

        # Get the Title of the Page
        time.sleep(self.config.SLEEP_TIMEOUT)
        if "Login" in self.web_driver.title:
            self._display_notification(title="Unable to Save Job to CareerFlow", message="Please Login at CareerFlow to save the Job.")

            return

        job_data: list[str] = self._read_job_details()

        # Switch to CareerFlow page
        self.web_driver.switch_to.window(self.web_driver.window_handles[2])

        self._fill_career_flow_job_form(job_data)

    def _save_job(self) -> None:
        """ Save's Job as per user preference """
        match self.config.SAVE_JOB_PREFERENCE:
            case "Save to CareerFlow":
                self._save_to_career_flow()
            case "Don't Save":
                print(Fore.YELLOW + "Uer chose not to save Job.")
            case _:
                print(Fore.RED + "Invalid Save Option!")

    def _is_job_active(self) -> bool:
        """
            Checks whether the Job posting is Active
            :return: Returns 'True" if available else 'False'
        """
        print(Fore.YELLOW + "\nChecking if the Job is Active")

        try:
            self.web_driver.find_element(By.ID, "expired-job-notice_Heading")

            return False
        except NoSuchElementException:
            return True

    def _validate_job_url(self) -> list[str]:
        """
            Reads all the Jobs URL & Validate
            :return:  Returns List of Strings
        """
        jobs_url: list[str] = []
        number_of_jobs_to_apply: int = len(self.glassdoor_input_data["jobs url"])

        for index in range(number_of_jobs_to_apply):
            url: str = self.glassdoor_input_data["jobs url"][index]

            if url.startswith("http") and url.__contains__("glassdoor"):
                jobs_url.append(url)

        return jobs_url

    def _apply_to_job_via_url(self) -> None:
        """ Apply to Jobs using GlassDoor URL """
        jobs_url: list[str] = self._validate_job_url()

        # Apply to Job's
        for i in range(len(jobs_url)):
            self._initialize_web_driver()
            self.web_driver.get(jobs_url[i])
            time.sleep(self.config.SLEEP_TIMEOUT)

            # Check if the Job is Active
            if self._is_job_active():
                print(Fore.YELLOW + "Job is Active")

                # Check if the user is Logged in
                if self._check_user_login():
                    # if self._check_user_login():
                    print(Fore.YELLOW + "User is logged In")

                    # Check if a Security message appears
                    if "Just a moment" in self.web_driver.title:
                        self._display_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
                        self.web_driver.quit()
                        sys.exit()

                    self._handle_application_button()
                else:
                    print(Fore.RED + "User is Not Logged In!")

                    self._display_notification(title="Unable to Apply for Job", message="User is not Logged In. Please Login and try again.")
                    sys.exit()
            else:
                print(Fore.RED + "Job has expired!")

                self._display_notification(title="Unable to Apply for Job", message="This Job has been expired!")

    def _read_firefox_profile_path(self) -> bool:
        """ Read Firefox Profile Path & Validate """
        firefox_profile_path = self.glassdoor_input_data["config"]["firefox profile path"]
        pattern: re = re.compile(self.config.FIREFOX_PROFILE_PATH_PATTERN, re.IGNORECASE)

        if pattern.match(firefox_profile_path):
            print(Fore.YELLOW + "Firefox Profile Path is valid.")

            return True

        print(Fore.RED + "Invalid Profile Path! Please try again.")

        return False

    def _read_resume_path(self) -> bool:
        """ Read Resume Path & Validate """
        self.config.RESUME_PATH = self.glassdoor_input_data["config"]["resume path"]

        if os.path.isfile(self.config.RESUME_PATH):
            if ".pdf" in self.config.RESUME_PATH or ".docx" in self.config.RESUME_PATH:
                print(Fore.YELLOW + "Resume Path is valid.")

                return True

            print(Fore.RED + "Incorrect File Format! File must exist and be .pdf or .docx")

            return False

        print(Fore.RED + "File Not Found! Please try again.")

        return False

    def _read_country(self) -> bool:
        """ Read Country & Validate """
        country: str = self.glassdoor_input_data["user"]["address"]["country"].title()

        try:
            if pycountry.countries.lookup(country) is not None:
                print(Fore.YELLOW + "Country is valid.")

                return True

            print(Fore.RED + "Can't Validate Country! Please try Again")
            self._display_notification(title="Validation Failed!", message="Invalid Country! Please try again.")
            
            return False
            
        except LookupError:
            print(Fore.RED + "Can't Validate Country! Please try Again")
            self._display_notification(title="Validation Failed!", message="Invalid Country! Please try again.")

            return False

    def _read_postal_code(self) -> bool:
        """ Read Postal Code & Validate """
        postal_code = self.glassdoor_input_data["user"]["address"]["postal code"].upper()
        pattern: re = re.compile(self.config.POSTAL_CODE_PATTERN, re.IGNORECASE)

        if pattern.match(postal_code):
            print(Fore.YELLOW + "Postal Code is valid.")

            return True

        print(Fore.RED + "Invalid Postal Code! Please try again.")

        return False

    def _read_city(self) -> bool:
        """ Read City & Validate """
        city = self.glassdoor_input_data["user"]["address"]["city"].title()

        if bool(city.strip()) and city.replace(" ", "").isalpha():
            print(Fore.YELLOW + "City is valid.")

            return True

        print(Fore.RED + "Invalid City Name! Please try again.")

        return False

    def _read_state(self) -> bool:
        """ Read State & Validate """
        state = self.glassdoor_input_data["user"]["address"]["state"]

        if bool(state) and state.replace(" ", "").isalpha():
            print(Fore.YELLOW + "State is Valid")

            return True

        print(Fore.RED + "Invalid State Name!")

        return False

    def _read_street_address(self) -> bool:
        """ Read Street Address & validate """
        street_address = self.glassdoor_input_data["user"]["address"]["street address"]

        if bool(street_address) and any(i.isdigit() for i in street_address) and any(i.isalpha() for i in street_address):
            print(Fore.YELLOW + "Postal Code is valid.")

            return True

        print(Fore.RED + "Invalid Street Address! Please try again.")

        return False

    def _read_past_job_title(self) -> bool:
        """ Read previous Job Title & Validate """
        job_title = self.glassdoor_input_data["user"]["job history"]["title"]

        if bool(job_title.strip()):
            print(Fore.YELLOW + "Past Job Title is valid.")

            return True

        print(Fore.RED + "Invalid Previous Job Title! Please try again.")

        return False

    def _read_past_job_company(self) -> bool:
        """ Read previous Company & Validate """
        company = self.glassdoor_input_data["user"]["job history"]["company"]

        if bool(company):
            print(Fore.YELLOW + "Past Company is valid.")

            return True

        print(Fore.RED + "Invalid Previous Company Name! Please try again.")

        return False

    def _read_past_experience(self) -> None:
        """ Read past Work Experience & Validate """
        while True:
            try:
                self.user.past_job.experience = int(input(Fore.BLUE + "Enter Experience: "))

                if self.user.past_job.experience >= 0:
                    break

                print(Fore.RED + "Invalid Input! Experience should be greater than 0.")
            except ValueError:
                print(Fore.RED + "Invalid Input! PLease try again.")

    def _show_commute_options(self) -> None:
        """ Display Commute to Work or Relocation options for the Job """
        print(Fore.MAGENTA + "Will you be able to reliably commute or relocate to Waterloo, ON for this job?")

        for key, value in self.config.COMMUTE_OPTIONS.items():
            print(Fore.MAGENTA + f"{key}. {value}")

    def _read_commute_to_work(self) -> None:
        """ Prompt user Commute to Work options """
        while True:
            self._show_commute_options()

            try:
                choice: int = int(input(Fore.BLUE + "\nSelect Commute to Work Option: "))

                if choice in self.config.COMMUTE_OPTIONS:
                    self.user.past_job.commute = self.config.COMMUTE_OPTIONS[choice]

                    break

                print(Fore.RED + "Invalid Input! Please select a number between 1 & 4.")
            except ValueError:
                print(Fore.RED + "Invalid Option! Please try again.")

    def _read_first_name(self) -> None:
        """ Read First Name & Validate """
        while True:
            self.user.first_name = input(Fore.BLUE + "Enter First Name: ").title()

            if bool(self.user.first_name) and self.user.first_name.replace(" ", "").isalpha():
                break

            print(Fore.RED + "Invalid First Name! Plase try again.")

    def _read_last_name(self) -> None:
        """ Read Last Name & Validate """
        while True:
            self.user.last_name = input(Fore.BLUE + "Enter Last Name: ").title()

            if bool(self.user.last_name) and self.user.last_name.replace(" ", "").isalpha():
                break

            print(Fore.RED + "Invalid Last Name! Plase try again.")

    def _read_phone_number(self) -> None:
        """ Reads Phone Number & Validate """
        while True:
            self.user.phone_number = input(Fore.BLUE + "Enter Phone Number: ")
            region = pycountry.countries.lookup(self.user.address.country).alpha_2

            try:
                if phonenumbers.is_valid_number(phonenumbers.parse(self.user.phone_number, region)):
                    break
            except NumberParseException:
                pass

            print(Fore.RED + "Invalid Phone Number! Plase try again.")

    def _save_job_preferences(self) -> None:
        """ Read the Save Preference """
        print(Fore.MAGENTA + "Where do want to save the Job?")

        save_option: dict[int: str] = {
            1: "Save to CareerFlow",
            2: "Don't Save"
        }

        for index, option in save_option.items():
            print(Fore.MAGENTA + f"{index}. {option}")

        while True:
            try:
                option: int = int(input(Fore.BLUE + "\nSelect your Preference to Save teh Job: "))

                if option in range(1, 3):
                    self.config.SAVE_JOB_PREFERENCE = save_option[option]

                    break
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a number.")

    def _load_glassdoor_input_data(self) -> None:
        """ Loads input data from data file """
        try:
            with open("glassdoor_input_data.json", "r") as file:
                self.glassdoor_input_data = json.load(file)
        except FileNotFoundError:
            print(Fore.RED + "Unable to load data from 'glassdoor_input_data.json' file.")

            sys.exit()

    @staticmethod
    def _read_user_choice() -> int:
        """ Read user choice for Menu options """
        try:
            return int(input(Fore.BLUE + "\nEnter your option: "))
        except ValueError:
            print(Fore.RED + "Invalid Input! Please enter a valid number!")

            return -1

    def _handle_choice(self, choice) -> None:
        """ Handle Menu Choice """
        match choice:
            case 1:
                self._apply_to_job_via_url()
            case _:
                print(Fore.RED + "Invalid Input! Please enter a valid number.")

    def _load_pre_train_model(self) -> None:
        """ Loads the pre-train Model """
        print(Fore.YELLOW + "Loading Pre Train Model ...")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def main(self) -> None:
        """ Main Method """
        self._save_job_preferences()
        self._load_pre_train_model()
        self._load_glassdoor_input_data()

        while True:
            self._show_options()

            choice: int = self._read_user_choice()

            if choice == 0:
                print(Fore.YELLOW + "\nExited from GlassDoor Job Applications")

                break

            self._handle_choice(choice=choice)
