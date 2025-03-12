class UserService:
    def sign_up(self):
        pass

    def login(self):
        print("***LOGIN***")
        email = input("please enter a valid email: ")
        if not self.validate_email(email):
            print("invalid email")
            return
        password = input("please enter your password: ")
        if not self.validate_password(password):
            print("invalid password")
            return
        # login with user management and get user data

    def add_like(self):
        pass

    def remove_like(self):
        pass

    def print_menu(self):
        print("***MENU***")
        print("1 - sign up")
        print("2 - login")
        print("3 - add like")
        print("4 - remove like")
        print("5 - exit")

    def start_app(self):
        print("***WELCOME***")
        while True:
            self.print_menu()
            user_choice = int(input("please select an option: "))
            match user_choice:
                case 1:
                    self.sign_up()
                case 2:
                    self.login()
                case 3:
                    self.add_like()
                case 4:
                    self.remove_like()
                case 5:
                    break


        print("exiting the system")

    def validate_email(self, email: str) -> bool:
        if "@" in email:
            return True
        else:
            return False

    def validate_password(self, password: str) -> bool:
        if len(password) >= 4:
            return True
        else:
            return False

