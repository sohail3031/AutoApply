import re
import time
import sys
import pycountry
import os
import pyperclip
import pyautogui
import phonenumbers
import random

from colorama import init, Fore
from phonenumbers.phonenumberutil import NumberParseException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from getpass import getpass
from selenium.common.exceptions import TimeoutException
from plyer import notification
from selenium.webdriver.support.ui import Select
from dataclasses import dataclass, field
from typing import Optional, AnyStr
from pathlib import Path


@dataclass
class Config:
    """ configuration data """
    EMAIL_PATTERN: str = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    WEB_DRIVER_TIMEOUT: int = 10
    GLASSDOOR_LANDING_PAGE: str = str()
    FIREFOX_PROFILE_PATH: str = str()
    FIREFOX_PROFILE_PATH_PATTERN: str = r"^C:\\Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+$"
    SLEEP_TIMEOUT: (int | float) = random.uniform(2, 6)
    RESUME_PATH: str = str()
    POSTAL_CODE_PATTERN: str = r"^(?!.*\s.*\s)[A-Za-z0-9\s]{4,7}$"
    FIREFOX_DRIVER_PATH = "geckodriver-v0.36.0-win64/geckodriver.exe"
    WEBDRIVER_SCROLL_BEHAVIOUR: str = "arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});"
    COMMUTE_OPTIONS: dict = field(default_factory=lambda : {
        1: "Yes, I can make the commute",
        2: "Yes, I am planning to relocate",
        3: "Yes, but I need relocation assistance",
        4: "No"
    })

@dataclass
class JobHistory:
    """ previous job data """
    title: str = str()
    company: str = str()
    experience: int = int()
    commute: str = str()

@dataclass
class Address:
    """ user address """
    street_address: str = str()
    state: str = str()
    city: str = str()
    postal_code: str = str()
    country: str = str()

@dataclass
class User:
    """ user data """
    first_name: str = str()
    last_name: str = str()
    phone_number: str = str()
    address: Address = field(default_factory=Address)
    past_job: JobHistory = field(default_factory=JobHistory)

class GlassDoor:
    def __init__(self) -> None:
        init(autoreset=True)

        self.web_driver: Optional[Firefox] = None
        self.config: Config = Config()
        self.user: User = User()

    @staticmethod
    def _show_options() -> None:
        """ Display different options to apply a Job """
        print(Fore.GREEN + "\n***** GlassDoor Job Application *****")

        options: list[str] = ["Exit", "Apply Using URL", "Apply with Job Search"]

        for index, value in enumerate(options):
            print(Fore.MAGENTA + f"{index}. {value}")

    def _initialize_web_driver(self) -> None:
        """ Initialize Firefox web driver """
        # Configure Firefox options
        options: Options = Options()
        options.set_preference("profile", self.config.FIREFOX_PROFILE_PATH)
        options.add_argument("-profile")
        options.add_argument(self.config.FIREFOX_PROFILE_PATH)

        # Setup Geckodriver Service
        if not Path(self.config.FIREFOX_DRIVER_PATH).exists():
            raise FileNotFoundError(Fore.RED + "Geckodriver not Found!")

        service: Service =Service(executable_path=self.config.FIREFOX_DRIVER_PATH)

        # Initialize web driver
        self.web_driver = Firefox(service=service, options=options)

    def _get_email(self) -> str:
        while True:
            _email: str = input(Fore.BLUE + "\nEnter Email Address: ")

            if re.match(self._email_pattern, _email):
                return _email
            else:
                print(Fore.RED + "Invalid Input! Please Provide a Valid Email Address")

    @staticmethod
    def _get_password() -> str:
        while True:
            _password: str = input(Fore.BLUE + "\nEnter Password: ")

            if _password:
                return _password

            print(Fore.RED + "Invalid Password!")

    def _log_user_in(self) -> None:
        _email: str = self._get_email()
        # _password: str = getpass(Fore.BLUE + "\nEnter Password: ")
        _password: str = self._get_password()

        self._initialize_web_driver()
        self.web_driver.get(self._glassdoor_url)

        time.sleep(self._sleep_timeout)

        WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "inlineUserEmail"))).send_keys(_email)
        WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Continue with email']]"))).click()
        WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "inlineUserPassword"))).send_keys(_password)

        time.sleep(self._sleep_timeout)

        WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Sign in']]"))).click()

        try:
            WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-display-variant='full-bleed']")))
            WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "modalUserEmail"))).send_keys(_email)
            WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Continue with email']]"))).click()
            WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "modalUserPassword"))).send_keys(_password)

            time.sleep(self._sleep_timeout)

            WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div/div/div/dialog/div[2]/div[1]/div/div[2]/div/div/div/div/div/div/form/div[2]/div/button"))).click()
        except TimeoutException:
            print(Fore.RED + "\nSomething went Wrong! Please try Again!")

        time.sleep(5)

        if self.web_driver.title.__eq__("Community | Glassdoor"):
            print(Fore.YELLOW + "\nYou are Logged In!")
        else:
            print(Fore.RED + "\nUnable to Login! Something went Wrong! Please try Again!")

        self.web_driver.quit()

    @staticmethod
    def _display_notification(title:str ="", message: str="", timeout: int=10) -> None:
        """ Displays Custom Notifications to the user """
        try:
            notification.notify(title=title, message=message, app_name="AutoApply", timeout=timeout)
        except Exception as e:
            print(Fore.RED + f"Unable to show notifications. {e}")

    def _check_if_user_is_logged_in(self) -> None:
        self._initialize_web_driver()
        self.web_driver.get(self._glassdoor_url)

        time.sleep(self._sleep_timeout)

        if self.web_driver.title.__eq__("Security | Glassdoor"):
            self._display_notification(title="Unable to LogIn", message="\nA security window has popup. Please open the firefox, go to the home page of 'GlassDoor', and close and finally re-run the application again.")
            self.web_driver.quit()
            sys.exit()

            # self._is_security_message_appeared = True
        else:
            self._check_user_login = True if self.web_driver.title.__eq__("Community | Glassdoor") else False

            self.web_driver.quit()

            if self._check_user_login:
                print(Fore.YELLOW + "User is Logged In!")
            else:
                print(Fore.YELLOW + "User is not Logged In!")

                _response: str = input(Fore.YELLOW + "\nDo You Want to LogIn? [Y | N]: ").lower()

                if _response.__eq__("y"):
                    self._log_user_in()
                else:
                    print(Fore.RED + "\nTo Apply for a Job You Must be Logged In")

                    return

    def _fill_address_form(self) -> None:
        """ Fill in or update the user address """
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Select Country
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Change']]"))).click()
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-country-list")))

        select = Select(self.web_driver.find_element(By.ID, "location-fields-country-list"))
        print("Country: " + self.user.address.country)
        select.select_by_visible_text(self.user.address.country)
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Enter Postal Code
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-postal-code-input"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-postal-code-input"))).send_keys(self.user.address.postal_code)
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Enter City & State
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-locality-input"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-locality-input"))).send_keys(self.user.address.city + ", " + self.user.address.state)
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Enter Street Address
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-address-input"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-address-input"))).send_keys(self.user.address.street_address)
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Click Continue button
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

    def _upload_resume(self) -> None:
        """
            Upload the Resume for the current Job
            The Upload Resume option will open file explorer to upload a file and Selenium doesn't have that functionality
            To bypass this issue, 'PyAutoGUI' has been used
         """
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Click on the existing Resume
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[@data-testid='FileResumeCardHeader-title']"))).click()

        # Scroll to "Resume Option" button
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='ResumeOptionsMenu-btn']"))
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
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "(//button/span[text()='Continue'])[3]"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "(//button/span[text()='Continue'])[3]"))).click()

    def _fill_work_experience(self) -> None:
        """ Fill the relevant past Job experience """
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Fill Past Job Title
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "job-title-input"))).send_keys(self.user.past_job.title)
        pyautogui.moveTo(300, 300)
        pyautogui.click()
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "company-name-input"))).send_keys(self.user.past_job.company)
        pyautogui.moveTo(300, 300)
        pyautogui.click()

        # Click on the "Continue" button
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

    def _fill_screener_questions(self) -> None:
        """ Answer Screener Questions during an Application process """
        # Get all the text fields
        time.sleep(self.config.SLEEP_TIMEOUT)

        text_inputs = self.web_driver.find_elements(By.XPATH, "//input[@type='text']")

        for input_field in text_inputs:
            # Get the "ID" of the text field and answer
            field_id = input_field.get_attribute("id")

            self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, field_id))
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, field_id))).send_keys(str(self.user.past_job.experience))
            time.sleep(self.config.SLEEP_TIMEOUT)

        # AAnswer "Commute" to work question
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, f"//span[text()='{self.user.past_job.commute}']"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{self.user.past_job.commute}']"))).click()

        # Click on "Continue" button
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button/span[text()='Continue']"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Continue']"))).click()

    def _submit_job_application(self) -> None:
        """ Review & Submit the Job Application """
        # Click on the Submit button
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button/span[text()='Submit your application']"))
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
        self.web_driver.execute_script(self.config.WEBDRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[data-testid='continue-button']"))
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[data-testid='continue-button']"))).click()

    def _process_easy_apply(self) -> None:
        """ Automate the Job with 'Easy Apply' button """
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Click on the "Easy Apply" button
        WebDriverWait(self.web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test='easyApply']"))).click()
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
            else:
                self._display_notification(title="Something Went Wrong!", message="We are unable to apply for the job. Please try again later!")
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

    def _get_apply_button_text(self) -> (str | None):
        """ Detects the Job Application button available on the page """
        button_selectors: dict[str: str] = {
            "Easy Apply": "//button[@data-test='easyApply']",
            "Apply on employer site": "//button[@data-test='applyButton']"
        }

        for text, xpath in button_selectors.items():
            try:
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, xpath)))

                return text
            except TimeoutException:
                print(Fore.YELLOW + "Easy Apply Button is Missing")

        return None

    def _apply_to_job_via_url(self) -> None:
        """ Apply to Jobs using GlassDoor URL """
        # print(Fore.YELLOW + "\nChecking if the User is Already Logged In")

        # if not self._check_user_login:
        #     self._check_if_user_is_logged_in()

        jobs_url: list[str] = []
        number_of_jobs_to_apply: int = self._number_of_jobs_to_apply()

        # Get Job URL'S
        for index in range(number_of_jobs_to_apply):
            jobs_url.append(self._read_job_url(index))

        # Apply to Job's
        for i in range(number_of_jobs_to_apply):
            self._initialize_web_driver()
            self.web_driver.get(jobs_url[i])

            time.sleep(self.config.SLEEP_TIMEOUT)

            # Check if a Security message appears
            if "Just a moment" in self.web_driver.title:
                self._display_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
                self.web_driver.quit()
                sys.exit()

            # Apply button text
            apply_button_text: (str | None) = self._get_apply_button_text()

            if apply_button_text is None:
                self._display_notification(title="Unable to Apply for Job", message="Unable to find the Button text to apply for the Job.")
                self.web_driver.quit()
                sys.exit()

            if apply_button_text.__eq__("Easy Apply"):
                self._process_easy_apply()
            else:
                print("Other Job Application")

    def _read_glassdoor_url(self) -> None:
        """ Read the GlassDoor URL & Validate """
        while True:
            self.config.GLASSDOOR_LANDING_PAGE = input(Fore.BLUE + "Enter the GlassDoor URL: ")

            if self.config.GLASSDOOR_LANDING_PAGE.startswith("http") and self.config.GLASSDOOR_LANDING_PAGE.__contains__("glassdoor"):
                break
            
            print(Fore.RED + "Invalid URL! Please try again.")

    def _read_firefox_profile_path(self) -> None:
        """ Read Firefox Profile Path & Validate """
        while True:
            self.config.FIREFOX_PROFILE_PATH = input(Fore.BLUE + "Enter the Profile Path of Firefox: ")
            pattern: re = re.compile(self.config.FIREFOX_PROFILE_PATH_PATTERN, re.IGNORECASE)

            if pattern.match(self.config.FIREFOX_PROFILE_PATH):
                break

            print(Fore.RED + "Invalid Profile Path! Please try again.")

    def _read_resume_path(self) -> None:
        """ reads resume path and validate """
        while True:
            self.config.RESUME_PATH = input(Fore.BLUE + "Enter the Resume Path: ")

            if os.path.isfile(self.config.RESUME_PATH):
                if ".pdf" in self.config.RESUME_PATH or ".docx" in self.config.RESUME_PATH:
                    break

                print(Fore.RED + "Incorrect File Format! File must exist and be .pdf or .docx")

            print(Fore.RED + "File Not Found! Please try again.")

    def _read_country(self) -> None:
        """ Read Country & Validate """
        while True:
            self.user.address.country = input(Fore.BLUE + "Enter Country: ").title()

            try:
                if pycountry.countries.lookup(self.user.address.country) is not None:
                    break

                print(Fore.RED + "Can't Validate Country! Please try Again")
            except LookupError:
                print(Fore.RED + "Can't Validate Country! Please try Again")

            print(Fore.RED + "Invalid Country! Please try again!")

    def _read_postal_code(self) -> None:
        """ read Postal Code & validate it
        'Note: Need to implement a better way to validate postal codes'
         """
        while True:
            self.user.address.postal_code = input(Fore.BLUE + "Enter Postal Code: ").title()
            pattern: re = re.compile(self.config.POSTAL_CODE_PATTERN, re.IGNORECASE)

            if pattern.match(self.user.address.postal_code):
                self.user.address.postal_code.upper()

                break

            print(Fore.RED + "Invalid Postal Code! Please try again.")

    def _read_city(self) -> None:
        """ read city and validate """
        while True:
            self.user.address.city = input(Fore.BLUE + "Enter City: ").title()

            if bool(self.user.address.city.strip()) and self.user.address.city.replace(" ", "").isalpha():
                self.user.address.city.title()

                break

            print(Fore.RED + "Invalid City Name! Please try again.")

    def _read_state(self) -> None:
        """ read state and validate """
        while True:
            self.user.address.state = input(Fore.BLUE + "Enter State: ").title()

            if bool(self.user.address.state) and self.user.address.state.replace(" ", "").isalpha():
                self.user.address.state.title()

                break

            print(Fore.RED + "Invalid State Name! Please try again!")

    def _read_street_address(self) -> None:
        """ read street address & validate """
        while True:
            self.user.address.street_address = input(Fore.BLUE + "Enter Street Address: ").title()

            if bool(self.user.address.street_address) and any(i.isdigit() for i in self.user.address.street_address) and any(i.isalpha() for i in self.user.address.street_address):
                self.user.address.street_address.title()

                break

            print(Fore.RED + "Invalid Street Address! Please try again.")

    def _read_past_job_title(self) -> None:
        """ read previous job title & validate """
        while True:
            self.user.past_job.title = input(Fore.BLUE + "Enter Previous Job Title: ").title()

            if bool(self.user.past_job.title.strip()):
                self.user.past_job.title.title()

                break

            print(Fore.RED + "Invalid Previous Job Title! Please try again.")

    def _read_past_job_company(self) -> None:
        """ read previous company and validate """
        while True:
            self.user.past_job.company = input(Fore.BLUE + "Enter Previous Company: ").title()

            if bool(self.user.past_job.company):
                self.user.past_job.company.title()

                break

            print(Fore.RED + "Invalid Previous Company Name! Please try again.")

    def _read_past_experience(self) -> None:
        """ read past work experience and validate """
        while True:
            try:
                self.user.past_job.experience = int(input(Fore.BLUE + "Enter Experience: "))

                if self.user.past_job.experience >= 0:
                    break

                print(Fore.RED + "Invalid Input! Experience should be greater than 0.")
            except ValueError:
                print(Fore.RED + "Invalid Input! PLease Enter a Number!")

    def _show_commute_options(self) -> None:
        """ Display Commute to Work or Relocation options for the Job """
        print(Fore.MAGENTA + "Will you be able to reliably commute or relocate to Waterloo, ON for this job?")

        for key, value in self.config.COMMUTE_OPTIONS.items():
            print(Fore.MAGENTA + f"{key}. {value}")

    def _read_commute_to_work(self) -> None:
        """ prompt user commute to work options """
        while True:
            self._show_commute_options()

            try:
                choice: int = int(input(Fore.BLUE + "\nSelect Commute to Work Option: "))

                if choice in self.config.COMMUTE_OPTIONS:
                    self.user.past_job.commute = self.config.COMMUTE_OPTIONS[choice]

                    break

                print(Fore.RED + "Invalid Input! Please select a number between 1 & 4.")
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a number.")

    def _read_first_name(self) -> None:
        """ read first name and validate """
        while True:
            self.user.first_name = input(Fore.BLUE + "Enter First Name: ").title()

            if bool(self.user.first_name) and self.user.first_name.replace(" ", "").isalpha():
                break

            print(Fore.RED + "Invalid Input! Plase enter a valid first name!")

    def _read_last_name(self) -> None:
        """ read last name and validate """
        while True:
            self.user.last_name = input(Fore.BLUE + "Enter Last Name: ").title()

            if bool(self.user.last_name) and self.user.last_name.replace(" ", "").isalpha():
                break

            print(Fore.RED + "Invalid Input! Plase enter a valid last name!")

    def _read_phone_number(self) -> None:
        """ reads phone number and validate """
        while True:
            self.user.phone_number = input(Fore.BLUE + "Enter Phone Number: ")
            region = pycountry.countries.lookup(self.user.address.country).alpha_2

            try:
                if phonenumbers.is_valid_number(phonenumbers.parse(self.user.phone_number, region)):
                    break
            except NumberParseException:
                pass

            print(Fore.RED + "Invalid Input! Plase enter a valid phone number!")

    def _collect_user_inputs(self) -> None:
        """ collect all user inputs """
        input_methods: dict = {
            "GlasDoor URL": self._read_glassdoor_url,
            "Firefox Profile Path": self._read_firefox_profile_path,
            "Resume Path": self._read_resume_path,
            "First Name": self._read_first_name,
            "Last Name": self._read_last_name,
            "Address": self._read_street_address,
            "City": self._read_city,
            "State": self._read_state,
            "Country": self._read_country,
            "Postal Code": self._read_postal_code,
            "Phone Number": self._read_phone_number,
            "Past Job Title": self._read_past_job_title,
            "Past Job Company": self._read_past_job_company,
            "Past Experience": self._read_past_experience,
            "Commute Preferences": self._read_commute_to_work
        }

        for label, method in input_methods.items():
            print(Fore.YELLOW + f"\nSetting {label} ...")

            method()

    @staticmethod
    def _read_user_choice() -> int:
        """ read user choice for menu options """
        try:
            return int(input(Fore.BLUE + "\nEnter your option: "))
        except ValueError:
            print(Fore.RED + "Invalid Input! Please enter a valid number!")

            return -1

    def _handle_choice(self, choice) -> None:
        """ handle menu choice """
        match choice:
            case 1:
                self._apply_to_job_via_url()
            case _:
                print(Fore.RED + "Invalid Input! Please enter a valid number.")

    def main(self) -> None:
        """ main method """
        self._collect_user_inputs()

        while True:
            self._show_options()

            choice: int = self._read_user_choice()

            if choice == 0:
                print(Fore.YELLOW + "\nExited from GlassDoor Job Applications")

                break

            self._handle_choice(choice=choice)
