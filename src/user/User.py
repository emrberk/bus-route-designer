import hashlib
import uuid
from src.util.Validators import *

class User:
    users = []

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

    @staticmethod
    def listUsers():
        for unnamed in User.users:
            print(unnamed.getFullName())

    @staticmethod
    def createUser():
        print("Please give me a username :")
        username = input()
        while True:
            print("Please enter your email : ")
            email = input()
            if not email_validator(email):
                print("Please provide an valid email address")
                continue
            break
        print("What is your name (name - lastname) : ")
        fullName = input()
        print("Please select your password : ")
        while True:
            ch = 'y'
            passwd1 = input()
            if not password_validator(passwd1):
                print("Password is not valid. Your password should include\n "
                      "- At least 8 characters long\n"
                      "- Contains at least one lowercase letter\n"
                      "- Contains at least one uppercase letter\n"
                      "- Contains at least one digit\n"
                      "- Contains at least one special character from @#$%^&+=\n"
                      "please try another password.")
                continue
            print("Please enter your password again : ")
            passwd2 = input()
            if passwd2 != passwd1:
                print("Your passwords are not matching, do you want to try again (y/N)")
                while ch.lower() != 'y':
                    ch = input()
                    if ch.lower() == 'n':
                        print("See you again. Goodbye :)")
                        exit(0)
                    else:
                        print("You typed wrong character, please try again (y/N)")
            else:
                break
        newUser = User(username, email, fullName, passwd1)
        User.users.append(newUser)
        print("Welcome to the ecosystem of BRD")
        return newUser

    @staticmethod
    def getUser(usrname):
        if not User.users:
            print(f"There is no user named {usrname}. If you wish to create new account, you need to type signUp.")
            return None
        for unnamed in User.users:
            if unnamed.getUsername() == usrname:
                return unnamed
            else:
                print(f"There is no user named {usrname}. If you wish to create new account, you need to type signUp.")
                return None
