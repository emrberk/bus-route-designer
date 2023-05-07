import unittest

from src.user.User import User


class UserTests(unittest.TestCase):
    def setUp(self) -> None:
        user = User("def", "def@gmail.com", "default account", "1234")
        token = user.login("1234")
        User.users.append(user)
        self.token = token

    def test_init(self):
        self.assertEqual(len(User.users), 1, "(init) : User count")
        self.assertEqual(User.users[0].sessionToken, self.token, "Session check")

    def test_sessionCheck(self):
        user = User.users[1]
        self.assertTrue(user.checkSession(self.token))


if __name__ == '__main__':
    unittest.main()
