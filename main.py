from src.dal.UserManagement import UserManagement
from src.models.Like import Like
from src.models.User import User
from src.services.UserService import UserService

"""
u1 = User(1, "gal", "name", "abc@gmail.com", "1234", 2)
um = UserManagement()
um.add_new_user(u1)
l1 = Like(1, 5)
um.add_like(l1)
um.remove_like(l1)
"""

ui = UserService()
ui.start_app()





