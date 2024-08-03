import unittest
from pydantic import ValidationError
from main import UserModel

class TestUserModel(unittest.TestCase):

    def test_valid_query(self):
        try:
            user = UserModel(user_query="Hello, how are you?")
            self.assertTrue(True)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

    def test_empty_query(self):
        with self.assertRaises(ValidationError) as context:
            UserModel(user_query="")
        self.assertIn("User query cannot be empty.", str(context.exception))

    def test_digits_only_query(self):
        with self.assertRaises(ValidationError) as context:
            UserModel(user_query="12345")
        self.assertIn("User query cannot be only digits.", str(context.exception))

    def test_whitespace_only_query(self):
        with self.assertRaises(ValidationError) as context:
            UserModel(user_query="     ")
        self.assertIn("User query cannot be only whitespace.", str(context.exception))

    def test_invalid_characters_query(self):
        with self.assertRaises(ValidationError) as context:
            UserModel(user_query="@@")
        self.assertIn("User query contains invalid symbols", str(context.exception))

    def test_partial_invalid_characters_query(self):
        with self.assertRaises(ValidationError) as context:
            UserModel(user_query="Hello @@")
        self.assertIn("User query contains invalid symbols", str(context.exception))

    def test_mixed_query(self):
        with self.assertRaises(ValidationError) as context:
            UserModel(user_query="%.[]")
        self.assertIn("User query must be in english.", str(context.exception))

    def test_query_with_letters(self):
        try:
            user = UserModel(user_query="Hello 123")
            self.assertTrue(True)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

if __name__ == '__main__':
    unittest.main()
