import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLineEdit, QLabel, QPushButton,
    QFormLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QSize, QDate

''' Hashes the input password using SHA-256 and returns the hexadecimal digest. '''
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

''' A widget that provides a login and registration interface for users. '''
class LoginRegisterWidget(QWidget):


    """ Initializes the LoginRegisterWidget instance with a database connection and a callback for successful logins.

        :param conn: The database connection object.
        :param login_success_callback: A function to call when a user logs in successfully. """
    def __init__(self, conn, login_success_callback):
        super().__init__()
        self.tabs = None
        self.login_tab = None
        self.register_tab = None
        self.login_username_input = None
        self.login_password_input = None
        self.login_button = None
        self.register_username_input = None
        self.register_password_input = None
        self.register_button = None
        self.conn = conn
        self.login_success_callback = login_success_callback
        self.init_ui()

    def sizeHint(self):
        # Suggests a size of 250x300 for the login/register view.
        return QSize(250, 300)

    ''' Initializes the user interface of the widget, including the tab layout and login/register tabs. '''
    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Login")
        self.tabs.addTab(self.register_tab, "Register")
        self.setup_login_tab()
        self.setup_register_tab()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    ''' Configures the login tab with a form layout, including input fields for username and password. '''
    def setup_login_tab(self):
        layout = QFormLayout()
        layout.setHorizontalSpacing(5)
        layout.setVerticalSpacing(5)

        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("Username")
        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("Password")
        self.login_password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        button_container = QWidget()
        button_container.setLayout(button_layout)

        layout.addRow("Username:", self.login_username_input)
        layout.addRow("Password:", self.login_password_input)
        layout.addRow("", button_container)
        self.login_tab.setLayout(layout)

    ''' Configures the registration tab with a form layout, including input fields for username and password. '''
    def setup_register_tab(self):
        layout = QFormLayout()
        layout.setHorizontalSpacing(5)
        layout.setVerticalSpacing(5)

        self.register_username_input = QLineEdit()
        self.register_username_input.setPlaceholderText("Username")
        self.register_password_input = QLineEdit()
        self.register_password_input.setPlaceholderText("Password")
        self.register_password_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.handle_register)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.register_button)
        button_layout.addStretch()
        button_container = QWidget()
        button_container.setLayout(button_layout)

        layout.addRow("Username:", self.register_username_input)
        layout.addRow("Password:", self.register_password_input)
        layout.addRow("", button_container)
        self.register_tab.setLayout(layout)


    ''' Handles the login button click event, validating user input and calling the login success callback if successful. '''

    def handle_login(self):
        """
        Verifies user credentials. The provided password is hashed with SHA-256
        and compared against the stored hash.
        """
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password!")
            return
        hashed_password = hash_password(password)
        c = self.conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed_password))
        result = c.fetchone()
        if result:
            self.login_success_callback(result[0])
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password!")

    def handle_register(self):
        """
        Registers a new user. The password entered by the user is hashed using SHA-256
        before being stored in the database.
        """
        username = self.register_username_input.text().strip()
        password = self.register_password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password!")
            return
        hashed_password = hash_password(password)
        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            self.conn.commit()
            QMessageBox.information(self, "Registration Successful",
                                    "You have registered successfully! You can now login.")
        except Exception:
            QMessageBox.warning(self, "Registration Failed", "Username already exists!")
