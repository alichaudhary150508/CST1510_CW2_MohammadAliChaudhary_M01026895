class User:
    def __init__(self, username, email, password, first_name=None, last_name=None):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def to_text_line(self):
        return f"{self.username}:{self.password}\n"