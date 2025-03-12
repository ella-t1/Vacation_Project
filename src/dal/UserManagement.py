from src.models.Like import Like
from src.models.User import User

class UserManagement:
    def __init__(self):
        pass

    def add_new_user(self, new_user: User):
        print("adding user to db: ", new_user.first_name, new_user.user_id)

    def get_user(self, email: str, password: str) -> User:
        u1 = User(1, "gal", "name", "abc@gmail.com", "1234", 2)
        return u1

    def is_email_exist(self, email: str) -> bool:
        return True

    def add_like(self, like: Like):
        print(f"adding like to db. user: {like.user_id}, vacation: {like.vacation_id}")

    def remove_like(self, like: Like):
        print(f"removing like from db. user: {like.user_id}, vacation: {like.vacation_id}")