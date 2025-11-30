class UserNotFoundException(Exception):
    def __init__(self, user_id: int = None, username: str = None):
        self.user_id = user_id
        self.username = username
        if user_id:
            super().__init__(f"User with id '{user_id}' not found")
        elif username:
            super().__init__(f"User with username '{username}' not found")
        else:
            super().__init__("User not found")
