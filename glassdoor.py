class GlassDoor:
    def __init__(self) -> None:
        pass

    @staticmethod
    def __display_options() -> None:
        print("0. Exit"
              "\n1. Apply Using URL"
              "\n2. Apply with Job Search")

    def main(self) -> None:
        while True:
            self.__display_options()

            try:
                __user_input: int = int(input("\nEnter your option: "))

                match __user_input:
                    case 0:
                        break
                    case 1:
                        pass
                    case 2:
                        pass
            except ValueError:
                print("Invalid Input!")
