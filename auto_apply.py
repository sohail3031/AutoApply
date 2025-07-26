import sys

from glassdoor import GlassDoor
from colorama import init, Fore

class AutoApply:
    def __init__(self) -> None:
        init(autoreset=True)

    @staticmethod
    def __show_welcome_message() -> None:
        print(Fore.CYAN + """👋 Welcome to AutoApply – Your Personal Job Application Assistant!
            \nWe're here to simplify your job search by automatically applying to relevant opportunities on your behalf. No more endless scrolling or repetitive clicks – just smart, efficient applications tailored to your preferences.
            
            ✅ Fast.  
            ✅ Accurate.  
            ✅ Hassle-Free.
            
            Let’s get started and land your next opportunity faster! 🚀
            """)

    @staticmethod
    def __display_options() -> None:
        print(Fore.MAGENTA +
              "\n0. Exit"
              "\n1. GlassDoor")

    def main(self) -> None:
        self.__show_welcome_message()

        while True:
            self.__display_options()

            try:
                __user_input: int = int(input(Fore.BLUE + "\nEnter your option: "))

                match __user_input:
                    case 0:
                        print(Fore.YELLOW + "Bye!")

                        sys.exit(0)
                    case 1:
                        GlassDoor().main()
                    case _:
                        print(Fore.RED + "Invalid Input!")
            except ValueError:
                print(Fore.RED + "Invalid Input! Please Enter a Number!")

if __name__ == "__main__":
    AutoApply().main()