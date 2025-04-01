import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from database import init_db
from login_register import LoginRegisterWidget
from dashboard import DashboardWidget

''' The main application window that manages the login/register and dashboard views. '''
class MainWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.current_user_id = None
        self.setWindowTitle("Expense Tracker")
        self.stack = QStackedWidget()
        self.login_register_widget = LoginRegisterWidget(conn, self.login_success)
        self.stack.addWidget(self.login_register_widget)
        self.dashboard = None
        self.setCentralWidget(self.stack)
        self.set_login_register_size()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

    ''' Sets the fixed size of the main window to 250x300 for the login/register view. '''
    def set_login_register_size(self):
        self.setFixedSize(250, 300)
        self.login_register_widget.setFixedSize(250, 300)

    ''' Sets the fixed size of the main window to 800x600 for the dashboard view. '''
    def set_dashboard_size(self):
        self.setFixedSize(800, 600)
        if self.dashboard:
            self.dashboard.setFixedSize(800, 600)

    ''' Called when a user logs in successfully. Sets up the dashboard view and switches to it.

        :param user_id: The ID of the logged-in user. '''
    def login_success(self, user_id):
        self.current_user_id = user_id
        self.set_dashboard_size()
        self.dashboard = DashboardWidget(self.conn, self.current_user_id, logout_callback=self.logout)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)

    ''' Called when the user logs out. Removes the dashboard view and switches back to the login/register view. '''
    def logout(self):
        self.current_user_id = None
        self.stack.removeWidget(self.dashboard)
        self.dashboard.deleteLater()
        self.dashboard = None
        self.stack.setCurrentWidget(self.login_register_widget)
        self.set_login_register_size()


if __name__ == "__main__":
    conn = init_db()
    app = QApplication(sys.argv)
    window = MainWindow(conn)
    window.show()
    sys.exit(app.exec_())
