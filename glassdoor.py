import re
import time

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
        self._is_security_message_appeared: bool = bool()

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

    def _log_user_in(self) -> None:
        _email: str = self._get_email()
        _password: str = getpass(Fore.BLUE + "\nEnter Password: ")

        self._set_up()
        self._web_driver.get(self._glassdoor_landing_page_url)

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "inlineUserEmail"))).send_keys(_email)
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Continue with email']]"))).click()
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "inlineUserPassword"))).send_keys(_password)
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Sign in']]"))).click()

        try:
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-display-variant='full-bleed']")))
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "modalUserEmail"))).send_keys(_email)
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Continue with email']]"))).click()
            WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "modalUserPassword"))).send_keys(_password)
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

        if self._web_driver.title.__eq__("Security | Glassdoor"):
            self._show_notification(title="Unable to LogIn", message="\nA security window has popup. Please open the firefox, go to the home page of 'GlassDoor', and close and finally re-run the application again.")
            self._web_driver.quit()

            self._is_security_message_appeared = True
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
        _country: str = input("Enter Country: ")
        _postal_code: str = input("Enter Postal Code: ")
        _city: str = input("Enter City: ")
        _state: str = input("Enter State: ")
        _street_address: str = input("Enter Street Address: ")

        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Change']]"))).click()
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.ID, "location-fields-country-list")))

        _select = Select(self._web_driver.find_element(By.ID, "location-fields-country-list"))

        _select.select_by_visible_text(_country)

    def _easy_apply(self) -> None:
        WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[4]/div/div[2]/div/div[1]/header/div[1]/div[2]/div[2]/div/div/button"))).click()
        time.sleep(5)
        self._web_driver.switch_to.window(self._web_driver.window_handles[1])
        time.sleep(5)

        print("easy apply: " + self._web_driver.title)

        if self._web_driver.title.__eq__("Just a moment..."):
            self._show_notification(title="Unable to Apply for Job", message="A security popup has appeared. Please open the Firefox, click on any job with easy apply and answer the security questions.")
        elif self._web_driver.title.__eq__("Add or update your address | Indeed"):
            self._add_or_update_your_address()

    def _apply_using_url(self) -> None:
        print(Fore.YELLOW + "\nChecking if the User is Already Logged In")

        # if not self._check_user_login:
        #     self._check_if_user_is_logged_in()

        if not self._is_security_message_appeared:
            _url: str = input(Fore.BLUE + "\nEnter the Job URL: ")

            self._set_up()

            self._web_driver.get(_url)

            print("url: " + self._web_driver.title)

            _apply_button_text: str = WebDriverWait(self._web_driver, self._web_driver_timeout).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div[4]/div/div[2]/div/div[1]/header/div[1]/div[2]/div[2]/div/div/button/span/div"))).text

            if _apply_button_text.__eq__("Easy Apply"):
                self._easy_apply()
            else:
                print("Apply on Company Website")

    def _set_glassdoor_landing_page_url(self) -> None:
        while True:
            self._glassdoor_landing_page_url = input(Fore.BLUE + "\nEnter the GlassDoor URL: ")

            if "glassdoor" in self._glassdoor_landing_page_url:
                break
            else:
                print(Fore.RED + "Invalid URL!")

    def _set_firefox_profile_path(self) -> None:
        while True:
            self._firefox_profile_path = input(Fore.BLUE + "\nEnter the Profile Path of Firefox: ")
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
