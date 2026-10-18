from Database_Helper import DatabaseHelper

class Login:
    """Handle authentication and database access for the application."""

    def __init__(self):
        self.database = DatabaseHelper()
        self.current_username = None

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate a user.

        Returns True if the credentials are valid; otherwise, False.
        """
        username = username.strip()

        if not username or not password:
            print("Username and password are required.")
            return False

        try:
            authenticated = self.database.login_user(username, password)

            if authenticated:
                self.current_username = username
                print(f"Welcome back, {username}!")
                return True

            print("Invalid username or password.")
            return False

        except Exception as exc:
            print(f"Login failed because of a database error: {exc}")
            return False

    def register(self, username: str, password: str) -> bool:
        """
        Register a new account.

        Returns True if registration succeeds; otherwise, False.
        """
        username = username.strip()

        if not username or not password:
            print("Username and password are required.")
            return False

        if len(username) > 100:
            print("Username must be 100 characters or fewer.")
            return False

        if len(password) < 8:
            print("Password must be at least 8 characters long.")
            return False

        try:
            registered = self.database.register_user(username, password)

            if registered:
                print("Account created successfully. You can now log in.")
                return True

            print(
                "Registration failed. The username may already exist, "
                "or the information may be invalid."
            )
            return False

        except Exception as exc:
            print(f"Registration failed because of a database error: {exc}")
            return False

    def logout(self) -> None:
        """Clear the currently authenticated user."""
        self.current_username = None
        print("You have been logged out.")

    def close(self) -> None:
        """Close the database connection when the application exits."""
        if getattr(self, "database", None) is not None:
            self.database.close()
