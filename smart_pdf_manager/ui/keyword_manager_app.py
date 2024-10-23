from typing import Dict

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QComboBox, \
    QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

from smart_pdf_manager.db.db_manager import DBManager


class KeywordManagerApp(QWidget):

    table_widget: QTableWidget = None

    __label_keyword: Dict[str, str] = {}
    __db_manager: DBManager = None
    __original_data: Dict[str, str] = {}

    def __init__(self, db_manager):
        super().__init__()
        self.__db_manager = db_manager
        self.init_ui()
        self.load_data_from_db()

    def init_ui(self):
        # Create a window with title
        self.setWindowTitle("Keyword Manager")

        self.setGeometry(100, 100, 370, 400)
        self.setWindowIcon(QtGui.QIcon("resources/SmartPDFManagerLogo.png"))

        # Create a layout
        layout = QVBoxLayout()
        # Display label-keyword dict
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(5)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Original Label", "Replacer"])

        self.table_widget.itemChanged.connect(self.check_last_row)

        layout.addWidget(self.table_widget)

        delete_button = QPushButton("Delete selected rows")
        delete_button.setStyleSheet("background-color: #820f00; font-weight: bold; color: white;")
        delete_button.clicked.connect(self.delete_selected_rows)
        layout.addWidget(delete_button)

        # Add a button to submit or process the key-value pairs
        submit_button = QPushButton("Submit new labels")
        submit_button.setStyleSheet("background-color: #316e00; font-weight: bold; color: white;")
        submit_button.clicked.connect(self.submit_pairs)
        layout.addWidget(submit_button)

        # Set the layout
        self.setLayout(layout)

    def delete_selected_rows(self):
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if not selected_rows:
            return

        for selected_row in selected_rows:
            row = selected_row.row()
            key_item = self.table_widget.item(row, 0)

            if key_item:
                key = key_item.text()
                self.__db_manager.delete_label(key)
                self.table_widget.removeRow(row)

    def load_data_from_db(self):
        if self.__db_manager is None:
            print("DB Manager is not initialized")
            return
        rows = self.__db_manager.select_all()

        self.table_widget.setRowCount(len(rows))

        self.__original_data.clear()
        for row_index, (key, value) in enumerate(rows):
            self.table_widget.setItem(row_index, 0, QTableWidgetItem(key))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(value))
            self.__original_data[key] = value
        self.add_empty_row()

    def check_last_row(self, item):
        """Check if the last row is fully filled, and if so, add a new empty row."""
        row_count = self.table_widget.rowCount()
        last_row_filled = True

        # Check if the last row (second to last, as rows are 0-indexed) is filled
        for column in range(self.table_widget.columnCount()):
            cell_item = self.table_widget.item(row_count - 1, column)
            if not cell_item or not cell_item.text().strip():
                last_row_filled = False
                break

        if last_row_filled:
            self.add_empty_row()

    def add_empty_row(self):
        """Add an empty row at the end of the table."""
        row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(row_count)
        self.table_widget.setItem(row_count, 0, QTableWidgetItem(''))
        self.table_widget.setItem(row_count, 1, QTableWidgetItem(''))

    def submit_pairs(self):
        for row in range(self.table_widget.rowCount()):
            key_item = self.table_widget.item(row, 0)
            value_item = self.table_widget.item(row, 1)

            if key_item and value_item and key_item.text() and value_item.text():
                new_key = key_item.text()
                new_value = value_item.text()
                original_entry = self.__original_data.get(new_key, None)
                if original_entry is not None:
                    self.__db_manager.update_label(new_key, new_key, new_value)
                    self.__original_data[new_key] = new_value
                else:
                    _ = self.__db_manager.insert_label(new_key, new_value)
                    # Update the original data
                    self.__original_data[new_key] = new_value
        self.load_data_from_db()

