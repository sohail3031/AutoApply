import sys

from glassdoor import GlassDoor

class AutoApply:
    @staticmethod
    def __show_welcome_message() -> None:
        print("""👋 Welcome to AutoApply – Your Personal Job Application Assistant!
            We're here to simplify your job search by automatically applying to relevant opportunities on your behalf. No more endless scrolling or repetitive clicks – just smart, efficient applications tailored to your preferences.
            
            ✅ Fast.  
            ✅ Accurate.  
            ✅ Hassle-Free.
            
            Let’s get started and land your next opportunity faster! 🚀
            """)

    @staticmethod
    def __display_options() -> None:
        print("\n0. Exit")
        print("1. GlassDoor")

    def main(self) -> None:
        self.__show_welcome_message()

        while True:
            self.__display_options()

            try:
                __user_input: int = int(input("\nEnter your option: "))

                match __user_input:
                    case 0:
                        print("Bye!")

                        sys.exit(0)
                    case 1:
                        GlassDoor().main()
            except ValueError:
                print("Invalid Input!")

if __name__ == "__main__":
    AutoApply().main()