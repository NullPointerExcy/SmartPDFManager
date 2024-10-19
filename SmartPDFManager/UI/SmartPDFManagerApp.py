import os
import sys
from os.path import expanduser

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QComboBox, QAction, QMenuBar
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from SmartPDFManager.utils import extract_text_from_pdf
import spacy
from collections import Counter


class SmartPDFManagerApp(QWidget):

    __available_languages = ["English", "German", "French"]

    __selected_input_directory = ""
    __selected_output_directory = ""

    nlp = spacy.load("en_core_web_sm")

    def __init__(self):
        super().__init__()
        self.ui_components()

    def analyze_and_categorize_pdf(self, pdf_path):
        text = extract_text_from_pdf(pdf_path)
        doc = self.nlp(text)

        entities = [(ent.text, ent.label_) for ent in doc.ents]
        labels = [label for _, label in entities if label not in ["CARDINAL", "DATE", "TIME"]]
        label_counter = Counter(labels)

        if label_counter:
            most_common_label = label_counter.most_common(1)[0][0]
            return most_common_label
        else:
            return "Uncategorized"

    def ui_components(self):
        self.setWindowTitle("Smart PDF Manager")

        self.setGeometry(100, 100, 400, 200)
        self.setWindowIcon(QtGui.QIcon("resources/SmartPDFManagerLogo.png"))
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Select the language for text analysis:"))
        self.language_combobox = QComboBox(self)
        self.language_combobox.addItems(self.__available_languages)
        self.language_combobox.currentIndexChanged.connect(self.change_language)
        layout.addWidget(self.language_combobox)

        layout.addSpacing(20)

        layout.addWidget(QLabel("Select a directory to organize PDFs:"))
        self.line_edit_input_Directory = QLineEdit(self)
        self.line_edit_input_Directory.setPlaceholderText("No directory selected")
        self.line_edit_input_Directory.setReadOnly(True)
        layout.addWidget(self.line_edit_input_Directory)

        self.pushButton_Directory = QPushButton("Choose Input Directory")
        self.pushButton_Directory.clicked.connect(self.choose_input_directory)
        layout.addWidget(self.pushButton_Directory)

        layout.addSpacing(50)

        layout.addWidget(QLabel("Select a directory to create the categories and move the PDFs to:"))
        self.line_edit_output_directory = QLineEdit(self)
        self.line_edit_output_directory.setPlaceholderText("No directory selected")
        self.line_edit_output_directory.setReadOnly(True)
        layout.addWidget(self.line_edit_output_directory)

        self.pushButton_outputDirectory = QPushButton("Choose Output Directory")
        self.pushButton_outputDirectory.clicked.connect(self.choose_output_directory)
        layout.addWidget(self.pushButton_outputDirectory)

        layout.addSpacing(50)

        self.organize_button = QPushButton("Organize PDFs")
        self.organize_button.setStyleSheet("""
                                        QPushButton {
                                            border: 2px solid black;
                                            padding: 5px;
                                        }
                                        QPushButton:hover {
                                            background-color: lightgreen;
                                        }
                                    """)
        layout.addWidget(self.organize_button)


        self.status_label = QLabel("Idle...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
                                        background-color: lightgreen;
                                        color: black;
                                        border: 2px solid darkgreen;
                                        border-radius: 10px;
                                        padding: 10px;
                                    """)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.organize_button.clicked.connect(self.organize_pdfs)

    def open_file(self):
        self.status_label.setText("Open File clicked")

    def show_about(self):
        self.status_label.setText("Smart PDF Manager v1.0")

    def change_language(self):
        match = self.language_combobox.currentText()
        if match == "English":
            self.nlp = spacy.load("en_core_web_sm")
        elif match == "German":
            self.nlp = spacy.load("de_core_news_sm")
        elif match == "French":
            self.nlp = spacy.load("fr_core_news_sm")

    def choose_input_directory(self):
        input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', expanduser("~"))
        if input_dir:
            self.line_edit_input_Directory.setText(input_dir)
            self.__selected_input_directory = input_dir
        else:
            self.status_label.setText("No directory selected!")

    def choose_output_directory(self):
        input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', expanduser("~"))
        if input_dir:
            self.line_edit_output_directory.setText(input_dir)
            self.__selected_output_directory = input_dir
        else:
            self.status_label.setText("No directory selected!")

    def organize_pdfs(self):
        if not self.__selected_input_directory:
            self.status_label.setText("No directory selected!")
            return

        self.status_label.setText("Organizing PDFs...")
        for root, dirs, files in os.walk(self.__selected_input_directory):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_path = os.path.join(root, file)
                    try:
                        category = self.analyze_and_categorize_pdf(pdf_path)
                        folder_path = os.path.join(self.__selected_output_directory, category)
                        os.makedirs(folder_path, exist_ok=True)

                        new_path = os.path.join(folder_path, file)
                        if os.path.exists(new_path):
                            print(f"File {new_path} already exists, skipping.")
                            continue

                        os.rename(pdf_path, new_path)
                        print(f"Moved '{pdf_path}' to '{new_path}' in category '{category}'")
                    except Exception as e:
                        print(f"Error organizing {pdf_path}: {e}")
                        self.status_label.setText(f"Error organizing PDFs: {e}")
        self.status_label.setText("PDFs organized successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SmartPDFManagerApp()
    window.show()

    sys.exit(app.exec())
