import re
import time
import sys
import pycountry
import os
import pyperclip
import pyautogui
import json

from colorama import init, Fore
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
from typing import Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from autoapply.config import Config
from autoapply.careerflow import CareerFlow
from selenium.webdriver.common.keys import Keys

class GlassDoor:
    def __init__(self) -> None:
        init(autoreset=True)

        self.web_driver: Optional[Firefox] = None
        self.config: Config = Config()
        self.input_data = None
        self.model: Optional[SentenceTransformer] = None

    @staticmethod
    def _show_options() -> None:
        """ Display different options to Apply for a Job """
        options: list[str] = ["Exit", "Apply Using URL", "Apply with Job Search"]

        for index, value in enumerate(options):
            print(Fore.MAGENTA + f"{index}. {value}")

    def _initialize_web_driver(self) -> None:
        """ Initialize Firefox Web Driver """
        if self._read_firefox_profile_path():
            filefox_profile_path = self.input_data["config"]["firefox profile path"]

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
        print(Fore.YELLOW + "Filling Address Form")

        time.sleep(self.config.SLEEP_TIMEOUT)

        # Select Country
        if self._read_country():
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Change']]"))).click()
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-country-list")))

            select = Select(self.web_driver.find_element(By.ID, "location-fields-country-list"))
            select.select_by_visible_text(self.input_data["user"]["address"]["country"].title())

        # Enter Postal Code
        if self._read_postal_code():
            self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-postal-code-input"))
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-postal-code-input"))).send_keys(self.input_data["user"]["address"]["postal code"].upper())

        # Enter City & State
        if self._read_city() or self._read_state():
            self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-locality-input"))
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-locality-input"))).send_keys(self.input_data["user"]["address"]["city"].title() + ", " + self.input_data["user"]["address"]["state"].title())

        # Enter Street Address
        if self._read_street_address():
            self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.ID, "location-fields-address-input"))
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "location-fields-address-input"))).send_keys(self.input_data["user"]["address"]["street address"].title())

        # Click Continue button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

        print(Fore.YELLOW + "Filled Address Form")

    def _upload_resume(self) -> None:
        """
            Upload the Resume for the current Job
            The Upload Resume option will open file explorer to upload a file, and Selenium doesn't have that functionality
            To bypass this issue 'PyAutoGUI' has been used
         """
        print(Fore.YELLOW + "Filling Resume Form")

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

                        print(Fore.YELLOW + "Filled Resume Form")

                        break
                except ElementNotInteractableException:
                    print(Fore.RED + f"Failed to click button #{index}")
        else:
            self._display_notification(title="Validation Failed!", message="File Not Found!")
            sys.exit(1)

    def _fill_work_experience(self) -> None:
        """ Fill the relevant past Job Experience """
        print(Fore.YELLOW + "Filling Work Experience Form")

        time.sleep(self.config.SLEEP_TIMEOUT)

        # Enter Past Job Title
        if self._read_past_job_title():
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "job-title-input"))).send_keys(self.input_data["user"]["job history"]["title"].title())
            pyautogui.moveTo(300, 300)
            pyautogui.click()

        # Enter Past Company Name
        if self._read_past_job_company():
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "company-name-input"))).send_keys(self.input_data["user"]["job history"]["company"].title())
            pyautogui.moveTo(300, 300)
            pyautogui.click()

        # Click on the "Continue" button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.execute_script("arguments[0].click();", WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))))

        print(Fore.YELLOW + "Filled Work Experience Form")

    @staticmethod
    def _validate_radio_button_questions(answer) -> bool:
        """ Validate 'Yes' & 'No' questions """
        return True if isinstance(answer, str) and answer.__eq__("yes") or answer.__eq__("no") else False

    @staticmethod
    def _validate_textarea_questions(answer) -> bool:
        """ Validate 'TextArea' questions """
        return True if isinstance(answer, (list, str)) and bool(answer) else False

    @staticmethod
    def _validate_text_field_questions(answer) -> bool:
        """ Validate 'Text Field' questions """
        return True if isinstance(answer, str) and bool(answer) else False

    def _fill_required_radio_button_questions(self, original_emb, index) -> None:
        """ Fill Mandatory Screener questions """
        for question, answer in self.input_data["screener questions"]["required questions"]["radio button"].items():
            if question.__eq__("_comment"):
                continue

            if bool(answer) and isinstance(answer, str):
                q_emb = self.model.encode(question, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

                if similarity * 100 > 70:
                    WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//label[.//span[contains(text()='{answer.title()}')]]/input"))).click()
            else:
                print(Fore.RED + "'Required Yes or No Question'!")

                self._display_notification(title="Validation Failed!", message="Required 'Yes' or 'No' questions are mandatory. And value be either 'Yes' or 'No'.")
                self.web_driver.quit()
                sys.exit(1)

    def _fill_required_textarea_questions(self, original_emb, index) -> None:
        """ Fill Mandatory Screener questions """
        for question, answer in self.input_data["screener questions"]["required questions"]["textarea"].items():
            if question.__eq__("_comment"):
                continue

            if isinstance(answer, (list, str)) and bool(answer):
                print(Fore.YELLOW + f"{question}: {answer}")

                q_emb = self.model.encode(question, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

                if similarity * 100 > 70:
                    WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span/textarea"))).send_keys(answer.title())
            else:
                print(Fore.RED + "'Required TextArea Question'!")

                self._display_notification(title="Validation Failed!", message="Required 'TestArea' questions are mandatory. And value be either 'String' or 'List of String'.")
                self.web_driver.quit()
                sys.exit(1)

    def _fill_required_text_field_questions(self, original_emb, index) -> None:
        """ Fill Mandatory Screener questions """
        for question, answer in self.input_data["screener questions"]["required questions"]["text field"].items():
            if question.__eq__("_comment"):
                continue

            if bool(answer) and isinstance(answer, str):
                print(Fore.YELLOW + f"{question}: {answer}")

                q_emb = self.model.encode(question, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

                if similarity * 100 > 70:
                    WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span/input"))).send_keys(answer if question.__eq__("LinkedIn URL") else answer.title())
            else:
                print(Fore.RED + "'Required Text Field Question'!")

                self._display_notification(title="Validation Failed!", message="Required 'Text Field' questions are mandatory. And value be either 'String'.")
                self.web_driver.quit()
                sys.exit(1)

    def _fill_required_dropdown_questions(self, original_emb, index) -> None:
        """ Fill Mandatory Screener questions """
        for question, answer in self.input_data["screener questions"]["required questions"]["text field"].items():
            if question.__eq__("_comment"):
                continue

            if bool(answer) and isinstance(answer, str):
                print(Fore.YELLOW + f"{question}: {answer}")

                q_emb = self.model.encode(question, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

                if similarity * 100 > 70:
                    Select(self.web_driver.find_element(By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//select")).select_by_visible_text(answer.title())
            else:
                print(Fore.RED + "'Required Text Field Question'!")

                self._display_notification(title="Validation Failed!", message="Required 'Text Field' questions are mandatory. And value be either 'String'.")
                self.web_driver.quit()
                sys.exit(1)

    def _fill_other_radio_button_questions(self, original_emb, index) -> None:
        """ Fill Non-Mandatory questions """
        for question, answer in self.input_data["screener questions"]["other questions"]["radio button"].items():
            if question.__eq__("_comment"):
                continue

            if self._validate_radio_button_questions(answer=answer):
                print(Fore.YELLOW + f"{question}: {answer}")

                q_emb = self.model.encode(question, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

                if similarity * 100 > 70:
                    WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//label[.//span[text()='{answer.title()}']]/input"))).click()

    def _fill_other_textarea_questions(self, original_emb, index) -> None:
        """ Fill Mandatory Screener questions """
        for question, answer in self.input_data["screener questions"]["other questions"]["textarea"].items():
            if question.__eq__("_comment"):
                continue

            if self._validate_textarea_questions(answer=answer):
                print(Fore.YELLOW + f"{question}: {answer}")

                q_emb = self.model.encode(question, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

                if similarity * 100 > 70:
                    WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span/textarea"))).send_keys(answer.title())

    def _fill_other_text_field_questions(self, original_emb, index) -> None:
        """ Fill Mandatory Screener questions """
        for question, answer in self.input_data["screener questions"]["other questions"]["text field"].items():
            if question.__eq__("_comment"):
                continue

            if self._validate_text_field_questions(answer=answer):
                print(Fore.YELLOW + f"{question}: {answer}")

                q_emb = self.model.encode(question, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(original_emb, q_emb).item()

                if similarity * 100 > 70:
                    WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span/input"))).send_keys(answer.title())

    def _fill_screener_questions(self) -> None:
        """ Answer Screener Questions during an Application process """
        print(Fore.YELLOW + "Filling Screener Questions Form")

        # Get all Questions
        time.sleep(self.config.SLEEP_TIMEOUT)

        all_questions = WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[starts-with(@id, 'q_')]")))

        # Get all the Questions, Validate, & Enter the appropriate Answers
        for index in range(len(all_questions)):
            time.sleep(self.config.SLEEP_TIMEOUT)

            try:
                self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span[@data-testid='rich-text']/span"))

                label_text = self.web_driver.find_element(By.XPATH, f"//div[starts-with(@id, 'q_{index}')]//span[@data-testid='rich-text']/span").text
                original_emb = self.model.encode(label_text, convert_to_tensor=True)

                for question_type, questions in self.input_data["screener questions"]["required questions"].items():
                    if question_type.__eq__("radio button") or question_type.__eq__("checkbox"):
                        self._fill_required_radio_button_questions(original_emb=original_emb, index=index)
                    elif question_type.__eq__("textarea"):
                        self._fill_required_textarea_questions(original_emb=original_emb, index=index)
                    elif question_type.__eq__("text field"):
                        self._fill_required_text_field_questions(original_emb=original_emb, index=index)
                    else:
                        self._fill_required_dropdown_questions(original_emb=original_emb, index=index)

                for question_type, questions in self.input_data["screener questions"]["other questions"].items():
                    if question_type.__eq__("radio button"):
                        self._fill_other_radio_button_questions(original_emb=original_emb, index=index)
                    elif question_type.__eq__("textarea"):
                        self._fill_other_textarea_questions(original_emb=original_emb, index=index)
                    else:
                        self._fill_other_text_field_questions(original_emb=original_emb, index=index)
            except Exception as e:
                print(Fore.RED + f"Error: {e}")

        # Click 'Continue' button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button/span[text()='Continue']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Continue']"))).click()

        print(Fore.YELLOW + "Filled Screener Questions Form")

    def _submit_job_application(self) -> None:
        """ Review & Submit the Job Application """
        print(Fore.YELLOW + "Filling Final Form")

        # Click on the Submit button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button/span[text()='Submit your application']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Submit your application']"))).click()

        print(Fore.YELLOW + "Filled Final Form")

    def _fill_contact_information(self) -> None:
        """ Fill the Contact Information form """
        print(Fore.YELLOW + "Filling Contact Information Form")

        # Enter First Name
        if self._read_first_name():
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//input[@data-testid='name-fields-first-name-input'"))).send_keys(self.input_data["user"]["first name"].title())

        # Enter Last Name
        if self._read_last_name():
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//input[@data-testid='name-fields-last-name-input']"))).send_keys(self.input_data["user"]["last name"].title())

        # Click the Country dropdown
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.find_element(By.XPATH, "//button[@aria-haspopup='listbox']").click()

        # Find & select the Country
        if self._read_country():
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//li[@role='option']//span[contains(text(),'{self.input_data['user']['address']['country']}')]"))).click()

        # Enter Phone Number
        if self._read_phone_number():
            time.sleep(self.config.SLEEP_TIMEOUT)
            WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='tel']"))).send_keys(self.input_data["user"]["phone number"])

        # Click on the Continue button
        self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[data-testid='continue-button']"))
        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[data-testid='continue-button']"))).click()

        print(Fore.YELLOW + "Filled Contact Information Form")

    def _process_easy_apply(self) -> None:
        """ Automate the Job with 'Easy Apply' button """
        # Click on the "Easy Apply" button
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test='easyApply']"))).click()
        time.sleep(self.config.SLEEP_TIMEOUT)

        # Switch to a new tab
        self.web_driver.switch_to.window(self.web_driver.window_handles[1])
        time.sleep(self.config.SLEEP_TIMEOUT)

        while True:
            time.sleep(self.config.WEB_DRIVER_TIMEOUT)

            page_title: str = self.web_driver.title.lower()

            if "just a moment" in page_title:
                self._display_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
                self.web_driver.quit()
                sys.exit(1)
            elif "add or update your address" in page_title:
                self._fill_address_form()
            elif "upload a resume for this application" in page_title:
                self._upload_resume()
            elif "add relevant work experience information" in page_title:
                self._fill_work_experience()
            elif "answer screener questions from the employer" in page_title:
                self._fill_screener_questions()
            elif "add or update your contact information" in page_title:
                self._fill_contact_information()
            elif "review the contents of this job application" in page_title:
                self._submit_job_application()
                self._display_notification(title="Success", message="Applied to Job Successfully")

                break

        # Closing the current window
        self.web_driver.close()

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
                time.sleep(self.config.SLEEP_TIMEOUT)
                self.web_driver.find_element(By.XPATH, xpath)

                if text.__eq__("Applied"):
                    self._display_notification(title="Can't Apply to this Job!", message="You have already applied to this Job.")
                    self.web_driver.quit()
                elif text.__eq__("Easy Apply"):
                    self._process_easy_apply()
                    self._save_job()
            except NoSuchElementException:
                print(f"No Element with {text}: {xpath}")
            except TimeoutException as e:
                print(f"TimeoutException: {e}")

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
        # Switch to the Job Posing page and copy the Data
        time.sleep(self.config.SLEEP_TIMEOUT)
        self.web_driver.switch_to.window(self.web_driver.window_handles[0])

        time.sleep(self.config.SLEEP_TIMEOUT)
        WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Show more']"))).click()

        return [self.web_driver.find_element(By.TAG_NAME, "h1").text,
                               self.web_driver.find_element(By.TAG_NAME, "h4").text,
                               self.web_driver.current_url,
                               self.web_driver.find_element(By.XPATH, "//div[@data-test='detailSalary']").text,
                               self.web_driver.find_element(By.XPATH, "//div[@data-test='location']").text,
                               self.web_driver.find_element(By.XPATH, "//div[contains(@class,'JobDetails_jobDescription')]").text]

    def _save_job(self) -> None:
        """ Save's Job as per user preference """
        match self.config.SAVE_JOB_PREFERENCE:
            case "Save to CareerFlow":
                CareerFlow(web_driver=self.web_driver).glassdoor_save_to_career_flow()
            case "Don't Save":
                print(Fore.YELLOW + "Uer chose not to save Job.")
            case _:
                print(Fore.RED + "Invalid Save Option!")

    def _is_job_active(self) -> bool:
        """
            Checks whether the Job posting is Active
            :return: Returns 'True' if available else 'False'
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
        number_of_jobs_to_apply: int = len(self.input_data["jobs url"])

        for index in range(number_of_jobs_to_apply):
            url: str = self.input_data["jobs url"][index]

            if url.startswith("http") and url.__contains__("glassdoor"):
                jobs_url.append(url)

        return jobs_url

    def _read_number_of_search_jobs(self) -> bool:
        """ Read number of Jobs to apply using GlassDoor Search """
        try:
            number_of_jobs = int(self.input_data["search jobs"]["number of jobs"])

            if number_of_jobs in range(1, 31):
                print(Fore.YELLOW + "Number of Jobs are valid.")

                return True

            print(Fore.RED + "Number of Jobs should be in between 1 and 30.")
        except ValueError:
            print(Fore.RED + "Invalid Number of Jobs! The value should be an integer.")

        return False

    def _read_search_job_title(self) -> bool:
        """ Read Job title for Search Jobs """
        job_title = self.input_data["search jobs"]["job title"]

        if job_title:
            print(Fore.YELLOW + "Search Job title is valid.")

            return True

        print(Fore.RED + "Invalid Search Job title!")

        return False

    def _read_search_job_location(self) -> bool:
        """ Read Job location for Search Jobs """
        job_location = self.input_data["search jobs"]["job location"]

        if job_location:
            print(Fore.YELLOW + "Search Job location is valid.")

            return True

        print(Fore.RED + "Invalid Search Job location!")

        return False

    def _read_glassdoor_url(self) -> bool:
        """ Read GlassDoor Landing page URL """
        url = self.input_data["search jobs"]["glassdoor url"]

        if url.startswith("http") and url.__contains__("glassdoor"):
            print(Fore.YELLOW + "GlassDoor Landing Page URL is valid.")

            return True

        print(Fore.RED + "Invalid GlassDoor Landing Page URL!")

        return False

    def _apply_to_job_via_search(self) -> None:
        """ Apply to Jobs using GlassDoor Search """
        if self._read_number_of_search_jobs() and self._read_search_job_title() and self._read_search_job_location() and self._read_glassdoor_url():
            number_of_jobs = int(self.input_data["search jobs"]["number of jobs"])

            self._initialize_web_driver()
            time.sleep(self.config.SLEEP_TIMEOUT)
            self.web_driver.get(self.input_data["search jobs"]["glassdoor url"])

            if self.web_driver.title.lower().__contains__("community"):
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='signedInGlobalNav']//a[text()='Jobs']"))).click()
                time.sleep(self.config.SLEEP_TIMEOUT)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "searchBar-jobTitle"))).send_keys(self.input_data["search jobs"]["job title"].title())
                time.sleep(self.config.SLEEP_TIMEOUT)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#searchBar-jobTitle-search-suggestions li"))).send_keys(Keys.DOWN)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#searchBar-jobTitle-search-suggestions li"))).send_keys(Keys.ENTER)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "searchBar-location"))).send_keys(self.input_data["search jobs"]["job location"].title())
                time.sleep(self.config.SLEEP_TIMEOUT)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#searchBar-location-search-suggestions li"))).send_keys(Keys.DOWN)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#searchBar-location-search-suggestions li"))).send_keys(Keys.ENTER)
                time.sleep(self.config.SLEEP_TIMEOUT)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "(//button[@data-test='expand-filters'])[2]"))).click()
                time.sleep(self.config.SLEEP_TIMEOUT)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "label[for='toggleSwitch-APPLICATION_TYPE']"))).click()
                time.sleep(self.config.SLEEP_TIMEOUT)
                self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, "//button[@data-test='apply-search-filters']"))
                time.sleep(self.config.SLEEP_TIMEOUT)
                WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test='apply-search-filters']"))).click()
                time.sleep(self.config.SLEEP_TIMEOUT)

                try:
                    jobs = WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-test='jobListing']")))
                except TimeoutException:
                    self._display_notification(title="No Jobs Found!", message="Unable to find the jobs.")
                    self.web_driver.quit()
                    sys.exit(1)

                for index, job in enumerate(jobs, start=1):
                    self.web_driver.execute_script(self.config.WEB_DRIVER_SCROLL_BEHAVIOUR, self.web_driver.find_element(By.XPATH, f"//li[@data-test='jobListing'][{index}]"))
                    time.sleep(self.config.SLEEP_TIMEOUT)
                    WebDriverWait(self.web_driver, self.config.WEB_DRIVER_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, f"//li[@data-test='jobListing'][{index}]"))).click()

                    self._handle_application_button()

                    if index.__eq__(number_of_jobs):
                        print(Fore.YELLOW + "Jobs Applied Successfully!")

                        break

                self.web_driver.quit()
                sys.exit(1)
            else:
                print(Fore.RED + "User is not Logged In!")

                self._display_notification(title="User is not Logged In!", message="Please Log In to apply for the Jobs.")
                self.web_driver.quit()
                sys.exit(1)
        else:
            self._display_notification(title="Validation Failed!", message="Data in 'search jobs' is compulsory and should be invalid format.")
            sys.exit(1)

    def _apply_to_job_via_url(self) -> None:
        """ Apply to Jobs using GlassDoor URL """
        jobs_url: list[str] = self._validate_job_url()

        self._initialize_web_driver()

        # Apply to Job's
        for i in range(len(jobs_url)):
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
                        sys.exit(1)

                    self._handle_application_button()
                    time.sleep(self.config.SLEEP_TIMEOUT)
                else:
                    print(Fore.RED + "User is Not Logged In!")

                    self._display_notification(title="Unable to Apply for Job", message="User is not Logged In. Please Login and try again.")
                    sys.exit(1)
            else:
                print(Fore.RED + "Job has expired!")

                self._display_notification(title="Unable to Apply for Job", message="This Job has been expired!")

        # Closing the Web Driver
        self.web_driver.quit()

    def _read_firefox_profile_path(self) -> bool:
        """ Read Firefox Profile Path & Validate """
        firefox_profile_path = self.input_data["config"]["firefox profile path"]
        pattern: re = re.compile(self.config.FIREFOX_PROFILE_PATH_PATTERN, re.IGNORECASE)

        if pattern.match(firefox_profile_path):
            print(Fore.YELLOW + "Firefox Profile Path is valid.")

            return True

        print(Fore.RED + "Invalid Profile Path! Please try again.")

        return False

    def _read_resume_path(self) -> bool:
        """ Read Resume Path & Validate """
        self.config.RESUME_PATH = self.input_data["config"]["resume path"]

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
        country: str = self.input_data["user"]["address"]["country"].title()

        try:
            if pycountry.countries.lookup(country) is not None:
                print(Fore.YELLOW + "Country is valid.")

                return True
        except LookupError:
            print(Fore.RED + "Can't Validate Country! Please try Again")
            self._display_notification(title="Validation Failed!", message="Invalid Country! Please try again.")

        return False

    def _read_postal_code(self) -> bool:
        """ Read Postal Code & Validate """
        postal_code = self.input_data["user"]["address"]["postal code"].upper()

        if postal_code:
            print(Fore.YELLOW + "Postal Code is valid.")

            return True

        print(Fore.RED + "Invalid Postal Code! Please try again.")

        return False

    def _read_city(self) -> bool:
        """ Read City & Validate """
        city = self.input_data["user"]["address"]["city"].title()

        if bool(city.strip()) and city.replace(" ", "").isalpha():
            print(Fore.YELLOW + "City is valid.")

            return True

        print(Fore.RED + "Invalid City Name! Please try again.")

        return False

    def _read_state(self) -> bool:
        """ Read State & Validate """
        state = self.input_data["user"]["address"]["state"]

        if bool(state) and state.replace(" ", "").isalpha():
            print(Fore.YELLOW + "State is Valid")

            return True

        print(Fore.RED + "Invalid State Name!")

        return False

    def _read_street_address(self) -> bool:
        """ Read Street Address & validate """
        street_address = self.input_data["user"]["address"]["street address"]

        if bool(street_address) and any(i.isdigit() for i in street_address) and any(i.isalpha() for i in street_address):
            print(Fore.YELLOW + "Postal Code is valid.")

            return True

        print(Fore.RED + "Invalid Street Address! Please try again.")

        return False

    def _read_past_job_title(self) -> bool:
        """ Read previous Job Title & Validate """
        job_title = self.input_data["user"]["job history"]["title"]

        if bool(job_title.strip()):
            print(Fore.YELLOW + "Past Job Title is valid.")

            return True

        print(Fore.RED + "Invalid Previous Job Title! Please try again.")

        return False

    def _read_past_job_company(self) -> bool:
        """ Read previous Company & Validate """
        company = self.input_data["user"]["job history"]["company"]

        if bool(company):
            print(Fore.YELLOW + "Past Company is valid.")

            return True

        print(Fore.RED + "Invalid Previous Company Name! Please try again.")

        return False

    def _read_past_experience(self) -> bool:
        """ Read past Work Experience & Validate """
        try:
            experience = self.input_data["user"]["job history"]["experience"]

            if experience >= 0:
                print(Fore.YELLOW + "Past Experience is valid.")

                return True

            print(Fore.RED + "Invalid Input! Experience should be greater than 0.")
        except ValueError:
            print(Fore.RED + "Invalid Input! PLease try again.")

        return False

    def _read_first_name(self) -> bool:
        """ Read First Name & Validate """
        first_name = self.input_data["user"]["first name"]

        if bool(first_name) and first_name.replace(" ", "").isalpha():
            print(Fore.YELLOW + "First Name is valid.")

            return True

        print(Fore.RED + "Invalid First Name!")

        return False

    def _read_last_name(self) -> bool:
        """ Read Last Name & Validate """
        last_name = self.input_data["user"]["last name"]

        if bool(last_name) and last_name.replace(" ", "").isalpha():
            print(Fore.YELLOW + "Last Name is valid")

            return True

        print(Fore.RED + "Invalid Last Name!")

        return False

    def _read_phone_number(self) -> bool:
        """ Reads Phone Number & Validate """
        phone_number = self.input_data["user"]["phone number"]

        if phone_number:
            print(Fore.YELLOW + "Phone Number is valid.")

            return True

        print(Fore.RED + "Invalid Phone Number! Plase try again.")

        return False

    def _save_job_preferences(self) -> None:
        """ Read the Save Preference """
        print(Fore.MAGENTA + "Do want to save the Job?")

        save_option: dict[int: str] = {
            1: "Save to CareerFlow",
            2: "Don't Save"
        }

        for index, option in save_option.items():
            print(Fore.MAGENTA + f"{index}. {option}")

        while True:
            try:
                option: int = int(input(Fore.BLUE + "\nSelect your Preference to Save the Job: "))

                if option in range(1, 3):
                    self.config.SAVE_JOB_PREFERENCE = save_option[option]

                    break
            except ValueError:
                print(Fore.RED + "Invalid Input! Please enter a number.")

    def _load_glassdoor_input_data(self) -> None:
        """ Loads input data from data file """
        try:
            with open("./input_data/glassdoor_input_data.json", "r") as file:
                self.input_data = json.load(file)
        except FileNotFoundError as e:
            print(Fore.RED + "Unable to load data from 'glassdoor_input_data.json' file.")
            print(e)

            sys.exit(1)

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
            case 2:
                self._apply_to_job_via_search()
            case _:
                print(Fore.RED + "Invalid Input! Please enter a valid number.")

    def _load_pre_train_model(self) -> None:
        """ Loads the pre-train Model """
        print(Fore.YELLOW + "Loading Pre Train Model ...")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def main(self) -> None:
        """ Main Method """
        print(Fore.GREEN + "\n***** GlassDoor Job Application *****")

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
