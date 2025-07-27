from colorama import init, Fore
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import Firefox

class GlassDoor:
    def __init__(self) -> None:
        init(autoreset=True)

        self.__check_user_login: bool = bool()
        self.__web_driver: Firefox = None

    @staticmethod
    def __display_options() -> None:
        print(Fore.GREEN + "\n***** GlassDoor Job Application *****")
        print(Fore.MAGENTA + "\n0. Exit"
              "\n1. Apply Using URL"
              "\n2. Apply with Job Search")

    def __set_up(self) -> None:
        __options: Options = Options()
        __profile_path: str = input(Fore.BLUE + "\nEnter the Profile Path of Firefox: ")

        __options.set_preference("profile", __profile_path)
        __options.add_argument("-profile")
        __options.add_argument(__profile_path)

        __service: Service =Service(executable_path=f"geckodriver-v0.36.0-win64/geckodriver.exe")
        self.__web_driver = Firefox(service=__service, options=__options)

    def __check_if_user_is_logged_in(self) -> None:
        self.__set_up()

        self.__web_driver.get("https://glassdoor.ca")

        print(self.__web_driver.title)

    def __apply_using_url(self) -> None:
        if not self.__check_user_login:
            self.__check_if_user_is_logged_in()
        else:
            print("User Logged In")

    def main(self) -> None:
        while True:
            self.__display_options()

            try:
                __user_input: int = int(input(Fore.BLUE + "\nEnter your option: "))

                match __user_input:
                    case 0:
                        print(Fore.YELLOW + "\nExited from GlassDoor Job Applications")

                        break
                    case 1:
                        self.__apply_using_url()
                    case _:
                        print(Fore.RED + "Invalid Input!")
            except ValueError:
                print(Fore.RED + "Invalid Input! Please Enter a Number!")
