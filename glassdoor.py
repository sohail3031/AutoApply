import re
import time
import sys
import pycountry
import os

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

    @staticmethod
    def _get_country() -> str:
        while True:
            # _country: str = input("Enter Country: ")
            _country: str = "Canada"

            try:
                if pycountry.countries.lookup(_country) is not None:
                    return _country.title()
            except LookupError:
                print(Fore.RED + "Invalid Country!")

    @staticmethod
    def _get_postal_code() -> str:
        while True:
            # _postal_code: str = input("Enter Postal Code: ")
            _postal_code: str = "N2H OB7"

            if len(_postal_code) in range(4, 8):
                return _postal_code.upper()

            print(Fore.RED + "Invalid Postal Code!")

    @staticmethod
    def _get_city() -> str:
        while True:
            # _city: str = input("Enter City: ")
            _city: str = "Kitchener"

            if _city:
                return _city.title()

            print(Fore.RED + "Invalid City Name!")

    @staticmethod
    def _get_state() -> str:
        while True:
            # _state: str = input("Enter State: ")
            _state: str = "Ontario"

            if _state:
                return _state.title()

            print(Fore.RED + "Invalid State Name!")

    @staticmethod
    def _get_street_address() -> str:
        while True:
            # _street_address: str = input("Enter Street Address: ")
            _street_address: str = "85 Duke Street West"

            if _street_address:
                return _street_address.title()

            print(Fore.RED + "Invalid Street Address!")

    def _add_or_update_your_address(self) -> None:
        _country: str = self._get_country()
        _postal_code: str = self._get_postal_code()
        _city: str = self._get_city()
        _state: str = self._get_state()
        _street_address: str = self._get_street_address()

        # country field
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Change']]"))).click()

        time.sleep(self._sleep_timeout)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-country-list")))

        _select = Select(self._web_driver.find_element(By.ID, "location-fields-country-list"))

        _select.select_by_visible_text(_country)

        time.sleep(self._sleep_timeout)

        # postal code field
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.ID, "location-fields-postal-code-input"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-postal-code-input"))).send_keys(_postal_code)

        time.sleep(self._sleep_timeout)

        # city & state field
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.ID, "location-fields-locality-input"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-locality-input"))).send_keys(_city + ", " + _state)

        time.sleep(self._sleep_timeout)

        # street address field
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.ID, "location-fields-address-input"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-address-input"))).send_keys(_street_address)

        time.sleep(self._sleep_timeout)

        # continue button
        self._web_driver.execute_script("arguments[0].scrollIntoView({behaviour: 'smooth', block: 'center'});", self._web_driver.find_element(By.XPATH, "//button[@data-testid='continue-button']"))
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continue-button']"))).click()

    def _set_resume_path(self) -> None:
        while True:
            self._resume_path = input(Fore.BLUE + "Enter the Resume Path: ")

            if os.path.isfile(self._resume_path):
                if ".pdf" in self._resume_path or ".docx" in self._resume_path:
                    break
                else:
                    print(Fore.RED + "Incorrect File Format")
            else:
                print(Fore.RED + "File Not Found!")

    def _upload_a_resume_for_this_application(self) -> None:
        self._set_resume_path()

    def _easy_apply(self) -> None:
        time.sleep(self._sleep_timeout)

        # click on easy apply button
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test='easyApply']"))).click()

        time.sleep(self._sleep_timeout)

        # switch to a new browser tab
        self._web_driver.switch_to.window(self._web_driver.window_handles[1])

        time.sleep(self._sleep_timeout)

        while True:
            print(self._web_driver.title)

            match self._web_driver.title:
                case "Just a moment...":
                    self._show_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
                    sys.exit()
                case "Add or update your address | Indeed":
                    self._show_notification(title="Need Information", message="Please fill the details in the terminal and comeback to the automation window.")
                    self._add_or_update_your_address()
                case "Upload a resume for this application | Indeed":
                    self._upload_a_resume_for_this_application()
                case _:
                    self._show_notification(title="Something Went Wrong!", message="We are unable to apply for the job. Please try again later!")
                    sys.exit()

            time.sleep(self._sleep_timeout)

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

        try:
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-test='easyApply']")))

            self._easy_apply()
        except TimeoutException:
            print("Apply on Company Website")

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

    def main(self) -> None:
        self._set_glassdoor_landing_page_url()
        self._set_firefox_profile_path()

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
