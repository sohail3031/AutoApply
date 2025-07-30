import sys

from glassdoor import GlassDoor
from colorama import init, Fore

class AutoApply:
    def __init__(self) -> None:
        init(autoreset=True)

    @staticmethod
    def _show_welcome_message() -> None:
        print(Fore.CYAN + """👋 Welcome to AutoApply – Your Personal Job Application Assistant!
            \nWe're here to simplify your job search by automatically applying to relevant opportunities on your behalf. No more endless scrolling or repetitive clicks – just smart, efficient applications tailored to your preferences.
            
            ✅ Fast.  
            ✅ Accurate.  
            ✅ Hassle-Free.
            
            Let’s get started and land your next opportunity faster! 🚀
            """)

    @staticmethod
    def _display_options() -> None:
        print(Fore.MAGENTA +
              "\n0. Exit"
              "\n1. GlassDoor")

    def main(self) -> None:
        self._show_welcome_message()

        while True:
            self._display_options()

            try:
                _user_input: int = int(input(Fore.BLUE + "\nEnter your option: "))

                match _user_input:
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