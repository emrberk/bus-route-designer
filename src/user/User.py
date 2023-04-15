import hashlib
import uuid

class User:
    def __init__(self, username, email, fullName, password):
        self.username = username
        self.email = email
        self.fullName = fullName
        self.password = hashlib.md5(password.encode())
        self.sessionToken = None

    def __str__(self):
        return (f"Username: {self.username}\n"
                f"Email: {self.email}\n"
                f"Full Name: {self.fullName}."
                )

    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username

    def getEmail(self):
        return self.email

    def setEmail(self, email):
        self.email = email

    def getFullName(self):
        return self.fullName

    def setFullName(self, fullName):
        self.fullName = fullName

    def setPassword(self, password):
        self.password = hashlib.md5(password.encode())

    def auth(self, password):
        return self.password.hexdigest() == hashlib.md5(password.encode()).hexdigest()

    def login(self, password):
        if self.auth(password):
            token = uuid.uuid1()
            self.sessionToken = token
            return token
        else:
            raise Exception('Password is invalid.')

    def checkSession(self, token):
        return self.sessionToken is not None and self.sessionToken == token

    def logout(self):
        self.sessionToken = None

if __name__ == '__main__':
    user = User('asd', 'asd', 'asd', 'asd')
    token = user.login('asd')
    print(token)
    user.logout()
    print(user.sessionToken)

