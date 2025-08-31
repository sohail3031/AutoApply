import sys

from glassdoor import GlassDoor
from colorama import init, Fore

class AutoApply:
    def __init__(self) -> None:
        init(autoreset=True)

    @staticmethod
    def _show_welcome_message() -> None:
        """ Display a welcome message to the user """
        message_lines: list[str] = [
            "👋 Welcome to AutoApply – Your Personal Job Application Assistant!",
            "",
            "We're here to simplify your job search by automatically applying to relevant opportunities on your behalf.",
            "No more endless scrolling or repetitive clicks – just smart, efficient applications tailored to your preferences.",
            "",
            "✅ Fast",
            "✅ Accurate",
            "✅ Hassle-Free",
            "",
            "Let’s get started and land your next opportunity faster! 🚀"
        ]

        print(Fore.CYAN + "\n".join(message_lines))

    @staticmethod
    def _show_options() -> None:
        """ Display available options to the user """
        options: list[str] = ["Exit", "GlassDoor"]

        print(Fore.MAGENTA + "Available Options: ")

        for index, option in enumerate(options):
            print(Fore.MAGENTA + f"{index}. {option}")

    def main(self) -> None:
        """ Main method """
        self._show_welcome_message()

        while True:
            self._show_options()

            try:
                user_input: int = int(input(Fore.BLUE + "\nEnter your option: "))

                match user_input:
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