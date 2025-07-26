from colorama import init, Fore

class GlassDoor:
    def __init__(self) -> None:
        init(autoreset=True)

        self.__check_user_login: bool = bool()

    @staticmethod
    def __display_options() -> None:
        print(Fore.GREEN + "\n***** GlassDoor Job Application *****")
        print(Fore.MAGENTA + "\n0. Exit"
              "\n1. Apply Using URL"
              "\n2. Apply with Job Search")

    def __check_if_user_is_logged_in(self) -> None:
        pass

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
