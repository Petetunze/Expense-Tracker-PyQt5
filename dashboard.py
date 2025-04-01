from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QDateEdit,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import QDate, Qt
from openpyxl import Workbook
from datetime import datetime

''' A widget that provides a dashboard for users to manage their expenses. '''
class DashboardWidget(QWidget):
    def __init__(self, conn, user_id, logout_callback):
        super().__init__()
        self.logout_button = None
        self.expense_name_input = None
        self.expense_cost_input = None
        self.expense_date_input = None
        self.description_input = None
        self.add_expense_button = None
        self.update_expense_button = None
        self.delete_expense_button = None
        self.export_button = None
        self.expenses_table = None
        self.conn = conn
        self.user_id = user_id
        self.selected_expense_id = None  # To track the selected expense.
        self.logout_callback = logout_callback
        self.init_ui()
        self.load_expenses()

    ''' Initializes the user interface of the widget, including the form layout and expense table. '''
    def init_ui(self):
        main_layout = QVBoxLayout()

        # Logout button on the top-right.
        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.handle_logout)
        logout_layout.addWidget(self.logout_button)
        main_layout.addLayout(logout_layout)

        # Expense form layout.
        form_layout = QFormLayout()
        self.expense_name_input = QLineEdit()
        self.expense_cost_input = QLineEdit()
        self.expense_date_input = QDateEdit(calendarPopup=True)
        self.expense_date_input.setDate(QDate.currentDate())
        self.description_input = QTextEdit()
        form_layout.addRow("Expense Name:", self.expense_name_input)
        form_layout.addRow("Expense Cost:", self.expense_cost_input)
        form_layout.addRow("Expense Date:", self.expense_date_input)
        form_layout.addRow("Description:", self.description_input)

        # Buttons for expense operations.
        self.add_expense_button = QPushButton("Add New Expense")
        self.add_expense_button.clicked.connect(self.add_expense)
        self.update_expense_button = QPushButton("Update Selected Expense")
        self.update_expense_button.clicked.connect(self.update_expense)
        self.update_expense_button.setEnabled(False)
        self.delete_expense_button = QPushButton("Delete Selected Expense")
        self.delete_expense_button.clicked.connect(self.delete_expense)
        self.delete_expense_button.setEnabled(False)
        self.export_button = QPushButton("Export as Excel Sheet")
        self.export_button.clicked.connect(self.export_expenses)

        # Layout for expense operations.
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_expense_button)
        button_layout.addWidget(self.update_expense_button)
        button_layout.addWidget(self.delete_expense_button)
        button_layout.addWidget(self.export_button)

        # Table to display expenses.
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(5)
        self.expenses_table.setHorizontalHeaderLabels(["ID", "Name", "Cost", "Date", "Description"])
        self.expenses_table.cellClicked.connect(self.load_selected_expense)

        # Assemble dashboard layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Your Expenses:"))
        main_layout.addWidget(self.expenses_table)
        self.setLayout(main_layout)

    '''  Handles the logout event by calling the provided logout_callback function. '''
    def handle_logout(self):
        self.logout_callback()

    ''' Retrieves expenses from the database and populates the expense table. '''
    def load_expenses(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name, cost, date, description FROM expenses WHERE user_id=?", (self.user_id,))
        rows = c.fetchall()
        self.expenses_table.setRowCount(0)
        for row_data in rows:
            row_number = self.expenses_table.rowCount()
            self.expenses_table.insertRow(row_number)
            for col, data in enumerate(row_data):
                # Cost column: add a dollar sign.
                if col == 2:
                    display_data = "$" + str(data)
                # Date column: reformat from yyyy-MM-dd to "Month day, Year".
                elif col == 3:
                    qdate = QDate.fromString(data, "yyyy-MM-dd")
                    display_data = qdate.toString("MMMM d, yyyy") if qdate.isValid() else str(data)
                else:
                    display_data = str(data)
                self.expenses_table.setItem(row_number, col, QTableWidgetItem(display_data))
        self.expenses_table.clearSelection()
        self.selected_expense_id = None
        self.update_expense_button.setEnabled(False)
        self.delete_expense_button.setEnabled(False)

    ''' Adds a new expense to the database.'''
    def add_expense(self):
        name = self.expense_name_input.text().strip()
        cost_text = self.expense_cost_input.text().strip()
        description = self.description_input.toPlainText().strip()
        date_str = self.expense_date_input.date().toString("yyyy-MM-dd")
        if not name or not cost_text:
            QMessageBox.warning(self, "Input Error", "Please enter both expense name and cost!")
            return
        try:
            cost = float(cost_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Cost must be a number!")
            return
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO expenses (user_id, name, cost, date, description) VALUES (?, ?, ?, ?, ?)",
            (self.user_id, name, cost, date_str, description)
        )
        self.conn.commit()
        QMessageBox.information(self, "Success", "Expense added successfully!")
        self.clear_form()
        self.load_expenses()

    ''' Loads the user selected expense's details into the form for editing. '''
    def load_selected_expense(self, row, column):
        expense_id_item = self.expenses_table.item(row, 0)
        if not expense_id_item:
            return
        self.selected_expense_id = int(expense_id_item.text())
        self.expense_name_input.setText(self.expenses_table.item(row, 1).text())
        cost_text = self.expenses_table.item(row, 2).text().lstrip("$")
        self.expense_cost_input.setText(cost_text)
        date_text = self.expenses_table.item(row, 3).text()
        qdate = QDate.fromString(date_text, "MMMM d, yyyy")
        self.expense_date_input.setDate(qdate if qdate.isValid() else QDate.currentDate())
        self.description_input.setPlainText(self.expenses_table.item(row, 4).text())
        self.update_expense_button.setEnabled(True)
        self.delete_expense_button.setEnabled(True)

    ''' Updates the selected expense in the database as well as updates the table. '''
    def update_expense(self):
        if not self.selected_expense_id:
            QMessageBox.warning(self, "Selection Error", "No expense selected for update!")
            return
        name = self.expense_name_input.text().strip()
        cost_text = self.expense_cost_input.text().strip()
        description = self.description_input.toPlainText().strip()
        date_str = self.expense_date_input.date().toString("yyyy-MM-dd")
        if not name or not cost_text:
            QMessageBox.warning(self, "Input Error", "Please enter both expense name and cost!")
            return
        try:
            cost = float(cost_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Cost must be a number!")
            return
        c = self.conn.cursor()
        c.execute(
            "UPDATE expenses SET name=?, cost=?, date=?, description=? WHERE id=? AND user_id=?",
            (name, cost, date_str, description, self.selected_expense_id, self.user_id)
        )
        self.conn.commit()
        QMessageBox.information(self, "Success", "Expense updated successfully!")
        self.clear_form()
        self.load_expenses()

    ''' Deletes the selected expense from the database as well as updates the table. '''
    def delete_expense(self):
        if not self.selected_expense_id:
            QMessageBox.warning(self, "Selection Error", "No expense selected for deletion!")
            return
        confirm = QMessageBox.question(
            self, "Confirm Deletion", "Are you sure you want to delete the selected expense?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return
        c = self.conn.cursor()
        c.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (self.selected_expense_id, self.user_id))
        self.conn.commit()
        QMessageBox.information(self, "Success", "Expense deleted successfully!")
        self.clear_form()
        self.load_expenses()

    '''  Exports the expenses to an Excel file. '''
    def export_expenses(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        c = self.conn.cursor()
        c.execute("SELECT id, name, cost, date, description FROM expenses WHERE user_id=?", (self.user_id,))
        rows = c.fetchall()
        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"
        # Write header row.
        ws.append(["ID", "Name", "Cost", "Date", "Description"])
        for row in rows:
            expense_id, name, cost, exp_date, desc = row
            try:
                dt = datetime.strptime(exp_date, "%Y-%m-%d")
                formatted_date = f"{dt.strftime('%B')} {dt.day}, {dt.strftime('%Y')}"
            except Exception:
                formatted_date = exp_date
            ws.append([expense_id, name, "$" + str(cost), formatted_date, desc])
        try:
            wb.save(file_path)
            QMessageBox.information(self, "Export Complete", "Expenses exported successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"An error occurred: {e}")

    ''' Clears the form and disables the update and delete buttons. '''
    def clear_form(self):
        self.expense_name_input.clear()
        self.expense_cost_input.clear()
        self.expense_date_input.setDate(QDate.currentDate())
        self.description_input.clear()
        self.selected_expense_id = None
        self.update_expense_button.setEnabled(False)
        self.delete_expense_button.setEnabled(False)
