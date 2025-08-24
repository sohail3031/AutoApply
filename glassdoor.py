import re
import time
import sys
import pycountry
import os
import pyperclip
import pyautogui

from colorama import init, Fore
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

class GlassDoor:
    def __init__(self) -> None:
        init(autoreset=True)

        self._check_user_login: bool = bool()
        self._web_driver: Firefox = None
        self._email_pattern: str = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        self._web_driver_timeout: int = 10
        self._glassdoor_landing_page_url: str = str()
        self._firefox_profile_path: str = str()
        self._firefox_profile_path_pattern: str = r"^C:\\Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+$"
        self._sleep_timeout: int = 4
        self._resume_path: str = str()
        self._country: str = str()
        self._postal_code: str = str()
        self._city: str = str()
        self._state: str = str()
        self._street_address: str = str()
        self._past_job_title: str = str()
        self._past_job_company: str = str()
        self._past_experience: int = int()
        self._commute_to_work: str = str()
        self._first_name: str = str()
        self._last_name: str = str()
        self._phone_number: str = str()

    @staticmethod
    def _display_options() -> None:
        print(Fore.GREEN + "\n***** GlassDoor Job Application *****")
        print(Fore.MAGENTA + "\n0. Exit"
              "\n1. Apply Using URL"
              "\n2. Apply with Job Search")

    def _set_up(self) -> None:
        _options: Options = Options()

        _options.set_preference("profile", self._firefox_profile_path)
        _options.add_argument("-profile")
        _options.add_argument(self._firefox_profile_path)

        _service: Service =Service(executable_path=f"geckodriver-v0.36.0-win64/geckodriver.exe")
        self._web_driver = Firefox(service=_service, options=_options)

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

        self._set_up()
        self._web_driver.get(self._glassdoor_landing_page_url)

        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "inlineUserEmail"))).send_keys(_email)
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Continue with email']]"))).click()
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "inlineUserPassword"))).send_keys(_password)

        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Sign in']]"))).click()

        try:
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-display-variant='full-bleed']")))
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "modalUserEmail"))).send_keys(_email)
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Continue with email']]"))).click()
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "modalUserPassword"))).send_keys(_password)

            time.sleep(self._sleep_timeout)

            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div/div/div/dialog/div[2]/div[1]/div/div[2]/div/div/div/div/div/div/form/div[2]/div/button"))).click()
        except TimeoutException:
            print(Fore.RED + "\nSomething went Wrong! Please try Again!")

        time.sleep(5)

        if self._web_driver.title.__eq__("Community | Glassdoor"):
            print(Fore.YELLOW + "\nYou are Logged In!")
        else:
            print(Fore.RED + "\nUnable to Login! Something went Wrong! Please try Again!")

        self._web_driver.quit()

    @staticmethod
    def _show_notification(title="", message="", timeout=10) -> None:
        notification.notify(title=title, message=message, app_name="AutoApply", timeout=timeout)

    def _check_if_user_is_logged_in(self) -> None:
        self._set_up()
        self._web_driver.get(self._glassdoor_landing_page_url)

        time.sleep(self._sleep_timeout)

        if self._web_driver.title.__eq__("Security | Glassdoor"):
            self._show_notification(title="Unable to LogIn", message="\nA security window has popup. Please open the firefox, go to the home page of 'GlassDoor', and close and finally re-run the application again.")
            self._web_driver.quit()
            sys.exit()

            # self._is_security_message_appeared = True
        else:
            self._check_user_login = True if self._web_driver.title.__eq__("Community | Glassdoor") else False

            self._web_driver.quit()

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

    def _add_or_update_your_address(self) -> None:
        time.sleep(self._sleep_timeout)

        # country field
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Change']]"))).click()

        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-country-list")))

        _select = Select(self._web_driver.find_element(By.ID, "location-fields-country-list"))

        _select.select_by_visible_text(self._country)

        time.sleep(self._sleep_timeout)

        # postal code field
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.ID, "location-fields-postal-code-input"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-postal-code-input"))).send_keys(self._postal_code)

        time.sleep(self._sleep_timeout)

        # city & state field
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.ID, "location-fields-locality-input"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-locality-input"))).send_keys(self._city + ", " + self._state)

        time.sleep(self._sleep_timeout)

        # street address field
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.ID, "location-fields-address-input"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-address-input"))).send_keys(self._street_address)

        time.sleep(self._sleep_timeout)

        # continue button
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

    def _upload_a_resume_for_this_application(self) -> None:
        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//span[@data-testid='FileResumeCardHeader-title']"))).click()

        time.sleep(self._sleep_timeout)

        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.XPATH, "//button[@data-testid='ResumeOptionsMenu-btn']"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='ResumeOptionsMenu-btn']"))).click()

        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Upload a different file']"))).click()

        time.sleep(self._sleep_timeout)

        pyperclip.copy(self._resume_path)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")

        time.sleep(self._sleep_timeout)

        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.CSS_SELECTOR, ".aac0a2873947e840f419e51db0fc4dbf6.a7df1b2535603e486cb9d8f3e1cd3068e.css-q81v3z.e8ju0x50"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".aac0a2873947e840f419e51db0fc4dbf6.a7df1b2535603e486cb9d8f3e1cd3068e.css-q81v3z.e8ju0x50"))).click()

    def _add_relevant_work_experience_information(self) -> None:
        """ Method to Add Relevant Work Experience """
        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "job-title-input"))).send_keys(self._past_job_title)
        pyautogui.moveTo(300, 300)
        pyautogui.click()
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "company-name-input"))).send_keys(self._past_job_company)
        pyautogui.moveTo(300, 300)
        pyautogui.click()

        time.sleep(self._sleep_timeout)

        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

    def _answer_screener_questions_from_the_employer(self) -> None:
        """ Method to Answer the Additional Questions from the Employer """
        time.sleep(self._sleep_timeout)

        text_inputs = self._web_driver.find_elements(By.XPATH, "//input[@type='text']")

        for input_field in text_inputs:
            field_id = input_field.get_attribute("id")

            self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.ID, field_id))
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, field_id))).send_keys(str(self._past_experience))

            time.sleep(self._sleep_timeout)

        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviout: 'smooth', block: 'center'});", self._web_driver.find_element(By.XPATH, f"//span[text()='{self._commute_to_work}']"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{self._commute_to_work}']"))).click()

        time.sleep(self._sleep_timeout)

        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.XPATH, "//button/span[text()='Continue']"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Continue']"))).click()

    def _review_the_contents_of_this_job_application(self) -> None:
        """ Method to Review the Content """
        time.sleep(self._sleep_timeout)

        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.XPATH, "//button/span[text()='Submit your application']"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Submit your application']")))

    def _add_or_update_your_contact_information(self) -> None:
        """ Method to Update Contact Information """
        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "ifl-InputFormField-:rn:"))).send_keys(self._first_name)

        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "ifl-InputFormField-:rs:"))).send_keys(self._last_name)

        time.sleep(self._sleep_timeout)

        self._web_driver.find_element(By.XPATH, "//button[@aria-labelledby='hidden-country-select-label-:r14:']").click()




    def _easy_apply(self) -> None:
        time.sleep(self._sleep_timeout)

        # click on easy apply button
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test='easyApply']"))).click()

        time.sleep(self._sleep_timeout)

        # switch to a new browser tab
        self._web_driver.switch_to.window(self._web_driver.window_handles[1])

        time.sleep(self._sleep_timeout)

        while True:
            _title: str = self._web_driver.title

            print(_title)

            if "Just a moment" in _title:
                self._show_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
                sys.exit()
            elif "Add or update your address" in _title:
                self._add_or_update_your_address()
            elif "Upload a resume for this application" in _title:
                self._upload_a_resume_for_this_application()
            elif "Add relevant work experience information" in _title:
                self._add_relevant_work_experience_information()
            elif "Answer Screener Questions from the employer" in _title:
                self._answer_screener_questions_from_the_employer()
            elif "Review the contents of this job application" in _title:
                self._review_the_contents_of_this_job_application()
                self._show_notification(title="Success", message="Applied to Job Successfully")
            elif "Add or update your contact information" in _title:
                self._add_or_update_your_contact_information()
            else:
                self._show_notification(title="Something Went Wrong!", message="We are unable to apply for the job. Please try again later!")
                sys.exit()

            time.sleep(self._sleep_timeout * 2)

    def _apply_using_url(self) -> None:
        print(Fore.YELLOW + "\nChecking if the User is Already Logged In")

        # if not self._check_user_login:
        #     self._check_if_user_is_logged_in()

        # _url: str = input(Fore.BLUE + "\nEnter the Job URL: ")
        _url: str = "https://www.glassdoor.ca/job-listing/junior-ai-integration-engineer-full-stack-venuiti-JV_IC2280158_KO0,41_KE42,49.htm?jl=1009852238063&utm_source=jobalert&utm_medium=email&utm_content=ja-jobpos3-1009852238063&utm_campaign=jobAlertAlert&tgt=GD_JOB_VIEW&src=GD_JOB_AD&uido=2B4F8C43B4AF03F6F90033411AC61A7B&ao=1136043&jrtk=5-yul1-0-1j3achbjkiuek805-5dab5a4bf7c2a922&cs=1_7196c3be&s=224&t=JA&pos=103&ja=358098550&guid=00000198d4c2a5a48712787a4778738f&jobListingId=1009852238063&ea=1&vt=e&cb=1755916578669&ctt=1755929691044&srs=EMAIL_JOB_ALERT&gdir=1"

        self._set_up()

        self._web_driver.get(_url)

        time.sleep(self._sleep_timeout)

        if self._web_driver.title.__eq__("Just a moment..."):
            self._show_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")

        # try:
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-test='easyApply']")))

        self._easy_apply()
        # except TimeoutException as e:
        #     print(e.msg)
        #     print(e.stacktrace)
            # print("Apply on Company Website")

    def _set_glassdoor_landing_page_url(self) -> None:
        while True:
            # self._glassdoor_landing_page_url = input(Fore.BLUE + "\nEnter the GlassDoor URL: ")
            self._glassdoor_landing_page_url = "https://www.glassdoor.ca/index.htm"

            if "glassdoor" in self._glassdoor_landing_page_url:
                break
            else:
                print(Fore.RED + "Invalid URL!")

    def _set_firefox_profile_path(self) -> None:
        while True:
            # self._firefox_profile_path = input(Fore.BLUE + "\nEnter the Profile Path of Firefox: ")
            self._firefox_profile_path = r"C:\Users\SOHAIL\AppData\Roaming\Mozilla\Firefox\Profiles\ds6fadtr.default-release"
            _pattern: re = re.compile(self._firefox_profile_path_pattern, re.IGNORECASE)

            if _pattern.match(self._firefox_profile_path):
                break
            else:
                print(Fore.RED + "Invalid Profile Path!")

    def _set_resume_path(self) -> None:
        while True:
            # self._resume_path = input(Fore.BLUE + "Enter the Resume Path: ")
            self._resume_path = r"C:\Users\SOHAIL\OneDrive\Desktop\Automation Resume\Full Stack\Mohammed Sohail Ahmed - Resume.pdf"

            if os.path.isfile(self._resume_path):
                if ".pdf" in self._resume_path or ".docx" in self._resume_path:
                    break
                else:
                    print(Fore.RED + "Incorrect File Format")
            else:
                print(Fore.RED + "File Not Found!")

    def _set_country(self) -> None:
        while True:
            # self._country: str = input("Enter Country: ")
            self._country: str = "Canada"

            try:
                if pycountry.countries.lookup(self._country) is not None:
                    self._country.title()

                    break
            except LookupError:
                print(Fore.RED + "Invalid Country!")

    def _set_postal_code(self) -> None:
        while True:
            # self._postal_code: str = input("Enter Postal Code: ")
            self._postal_code: str = "N2H OB7"

            if len(self._postal_code) in range(4, 8):
                self._postal_code.upper()

                break

            print(Fore.RED + "Invalid Postal Code!")

    def _set_city(self) -> None:
        while True:
            # self._city: str = input("Enter City: ")
            self._city: str = "Kitchener"

            if self._city:
                self._city.title()

                break

            print(Fore.RED + "Invalid City Name!")

    def _set_state(self) -> None:
        while True:
            # self._state: str = input("Enter State: ")
            self._state: str = "Ontario"

            if self._state:
                self._state.title()

                break

            print(Fore.RED + "Invalid State Name!")

    def _set_street_address(self) -> None:
        while True:
            # self._street_address: str = input("Enter Street Address: ")
            self._street_address: str = "85 Duke Street West"

            if self._street_address:
                self._street_address.title()

                break

            print(Fore.RED + "Invalid Street Address!")

    def _set_past_job_title(self) -> None:
        while True:
            # self._past_job_title = input(Fore.BLUE + "Enter Past Job Title: ")
            self._past_job_title = "Full Stack Developer"

            if self._past_job_title:
                self._past_job_title.title()

                break

            print(Fore.RED + "Invalid Job Title!")

    def _set_past_job_company(self) -> None:
        """ Read the Past Company """
        while True:
            # self._past_job_company = input(Fore.BLUE + "Enter Past Company: ")
            self._past_job_company = "Infosys"

            if self._past_job_company:
                self._past_job_company.title()

                break

            print(Fore.RED + "Invalid Past Company Name!")

    def _set_past_experience(self) -> None:
        """ Read Experience Years """
        while True:
            try:
                # self._past_experience = int(input(Fore.BLUE + "Enter Experience: "))
                self._past_experience = 3
                
                if self._past_experience:
                    break
            except ValueError:
                print(Fore.RED + "Invalid Input! PLease Enter a Number!")

    @staticmethod
    def _display_commute_to_work_options() -> None:
        """ Method to Display Commute to Work Options """
        print(Fore.MAGENTA + "Will you be able to reliably commute or relocate to Waterloo, ON for this job?")
        print(Fore.MAGENTA + "1. Yes, I can make the commute")
        print(Fore.MAGENTA + "2. Yes, I am planning to relocate")
        print(Fore.MAGENTA + "3. Yes, but I need relocation assistance")
        print(Fore.MAGENTA + "4. No")

    def _set_commute_to_work(self) -> None:
        while True:
            self._display_commute_to_work_options()

            try:
                # option: int = int(input(Fore.BLUE + "Select Commute to Work Option: "))
                option: int = 1

                match option:
                    case 1:
                        self._commute_to_work = "Yes, I can make the commute"

                        break
                    case 2:
                        self._commute_to_work = "Yes, I am planning to relocate"

                        break
                    case 3:
                        self._commute_to_work = "Yes, but I need relocation assistance"

                        break
                    case 4:
                        self._commute_to_work = "No"

                print(Fore.RED + "Invalid Input! The Number Should be in Between 1 & 4")
            except ValueError:
                print(Fore.RED + "Invalid Input! Please Enter a Number")

    def _set_first_name(self) -> None:
        while True:
            self._first_name = input(Fore.BLUE + "Enter First Name: ")

            if self._first_name:
                break

            print(Fore.RED + "Invalid Input! Plase Enter a Valid First Name!")

    def _set_last_name(self) -> None:
        while True:
            self._last_name = input(Fore.BLUE + "Enter Last Name: ")

            if self._last_name:
                break

            print(Fore.RED + "Invalid Input! Plase Enter a Valid Last Name!")

    def _set_phone_number(self) -> None:
        while True:
            self._first_name = input(Fore.BLUE + "Enter First Name: ")

            if self._phone_number:
                break

            print(Fore.RED + "Invalid Input! Plase Enter a Valid hone Number!")

    def _read_user_inputs(self) -> None:
        self._set_glassdoor_landing_page_url()
        self._set_firefox_profile_path()
        self._set_resume_path()
        self._set_first_name()
        self._set_last_name()
        self._set_phone_number()
        self._set_country()
        self._set_postal_code()
        self._set_city()
        self._set_state()
        self._set_street_address()
        self._set_past_job_title()
        self._set_past_job_company()
        self._set_past_experience()
        self._set_commute_to_work()

    def main(self) -> None:
        self._read_user_inputs()

        while True:
            self._display_options()

            try:
                _user_input: int = int(input(Fore.BLUE + "\nEnter your option: "))

                match _user_input:
                    case 0:
                        print(Fore.YELLOW + "\nExited from GlassDoor Job Applications")

                        break
                    case 1:
                        self._apply_using_url()
                    case _:
                        print(Fore.RED + "Invalid Input!")
            except ValueError:
                print(Fore.RED + "Invalid Input! Please Enter a Number!")
