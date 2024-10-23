import os
import subprocess
import sys
import threading
import time
from os.path import expanduser
from pathlib import Path
from typing import List, Any, Tuple

from smart_pdf_manager.db.db_manager import DBManager
from smart_pdf_manager.ui.keyword_manager_app import KeywordManagerApp

sys.path.append(str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QComboBox
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from smart_pdf_manager.utils import extract_text_from_pdf
# import smart_pdf_manager.ui.configuration.configuration as config
import spacy
from collections import Counter


class SmartPDFManagerApp(QWidget):
    __available_languages: List[str] = ["English", "German", "French"]

    __selected_input_directory: str | None = None
    __selected_output_directory: str | None = None
    __default_model_path = Path.home() / "spacy_models"
    __db_manager = None
    __keyword_manager_app: KeywordManagerApp = None

    nlp = None
    status_label = None

    @property
    def db_manager(self):
        if not self.__db_manager:
            from smart_pdf_manager.db.db_manager import DBManager
            self.__db_manager = DBManager()
        return self.__db_manager

    def __init__(self):
        super().__init__()
        self.__db_manager = DBManager()

        self.status_label = QLabel("Idle...")
        self.download_model_if_needed("English")

        model_path = self.__default_model_path / "en_core_web_sm" / "en_core_web_sm-3.8.0"
        self.nlp = spacy.load(str(model_path))
        self.ui_components()

    def analyze_and_categorize_pdf(self, pdf_path: str) -> str:
        text: str = extract_text_from_pdf(pdf_path)
        doc: Any = self.nlp(text)

        label_replacements = self.__db_manager.load_labels_from_db()

        entities: List[Tuple[str, Any]] = [(ent.text, ent.label_) for ent in doc.ents]
        replaced_labels = []
        # Replace the labels with the custom labels from the database
        for _, label in entities:
            if label in label_replacements:
                replaced_labels.append(label_replacements[label])
            else:
                replaced_labels.append(label)

        label_counter = Counter(replaced_labels)

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

        layout.addSpacing(20)
        self.open_label_keyword_manager = QPushButton("Open Label Keyword Manager")
        self.open_label_keyword_manager.setStyleSheet("""
                                                    QPushButton { 
                                                        background-color: lightblue;
                                                    }
                                                    """)
        self.open_label_keyword_manager.clicked.connect(self.open_keyword_manager_app)
        layout.addWidget(self.open_label_keyword_manager)

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
        self.organize_button.setDisabled(
            self.__selected_output_directory is None or self.__selected_input_directory is None)
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

    def open_keyword_manager_app(self):
        self.__keyword_manager_app = KeywordManagerApp(db_manager=self.db_manager)
        self.__keyword_manager_app.show()

    def download_model_in_thread(self, model_name: str):
        download_thread = threading.Thread(target=self.download_model_if_needed, args=(model_name,))
        download_thread.start()

    def download_model_if_needed(self, language: str):
        if language == "English":
            model_path: Path = self.__default_model_path / "en_core_web_sm"
            if not (model_path / "config.cfg").exists():
                self.status_label.setText("Downloading English model...")
                subprocess.run(
                    ["python", "-m", "spacy", "download", "en_core_web_sm", "--target", str(self.__default_model_path)])
                self.status_label.setText("Idle...")
        elif language == "German":
            model_path: Path = self.__default_model_path / "de_core_news_sm"
            if not (model_path / "config.cfg").exists():
                self.status_label.setText("Downloading German model...")
                subprocess.run(["python", "-m", "spacy", "download", "de_core_news_sm", "--target",
                                str(self.__default_model_path)])
                self.status_label.setText("Idle...")
        elif language == "French":
            model_path: Path = self.__default_model_path / "fr_core_news_sm"
            if not (model_path / "config.cfg").exists():
                self.status_label.setText("Downloading French model...")
                subprocess.run(["python", "-m", "spacy", "download", "fr_core_news_sm", "--target",
                                str(self.__default_model_path)])
                self.status_label.setText("Idle...")

    def change_language(self):
        match: str = self.language_combobox.currentText()
        self.status_label.setText(f"Downloading {match} model...")

        self.download_model_in_thread(match)

        if match == "English":
            model_path = self.__default_model_path / "en_core_web_sm" / "en_core_web_sm-3.8.0"
            self.nlp = spacy.load(str(model_path))
        elif match == "German":
            model_path = self.__default_model_path / "de_core_news_sm" / "de_core_news_sm-3.8.0"
            self.nlp = spacy.load(str(model_path))
        elif match == "French":
            model_path = self.__default_model_path / "fr_core_news_sm" / "fr_core_news_sm-3.8.0"
            self.nlp = spacy.load(str(model_path))

    def choose_input_directory(self):
        input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', expanduser("~"))
        if input_dir:
            self.line_edit_input_Directory.setText(input_dir)
            self.__selected_input_directory = input_dir
            self.organize_button.setDisabled(
                self.__selected_output_directory is None or self.__selected_input_directory is None)
        else:
            self.status_label.setText("No directory selected!")

    def choose_output_directory(self):
        input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', expanduser("~"))
        if input_dir:
            self.line_edit_output_directory.setText(input_dir)
            self.__selected_output_directory = input_dir
            self.organize_button.setDisabled(
                self.__selected_output_directory is None or self.__selected_input_directory is None)
        else:
            self.status_label.setText("No directory selected!")

    def organize_pdfs(self):
        if not self.__selected_input_directory:
            self.status_label.setText("No directory selected!")
            return

        self.status_label.setText("Organizing PDFs...")
        self.status_label.setStyleSheet("""
                                        background-color: red;
                                        color: black;
                                        border: 2px solid red;
                                        border-radius: 10px;
                                        padding: 10px;
                                    """)
        for root, dirs, files in os.walk(self.__selected_input_directory):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_path: str = os.path.join(root, file)
                    try:
                        category: str = self.analyze_and_categorize_pdf(pdf_path)
                        folder_path: str = os.path.join(self.__selected_output_directory, category)
                        os.makedirs(folder_path, exist_ok=True)

                        new_path: str = os.path.join(folder_path, file)
                        if os.path.exists(new_path):
                            print(f"File {new_path} already exists, skipping.")
                            continue

                        os.rename(pdf_path, new_path)
                        print(f"Moved '{pdf_path}' to '{new_path}' in category '{category}'")
                    except Exception as e:
                        print(f"Error organizing {pdf_path}: {e}")
                        self.status_label.setText(f"Error organizing PDFs: {e}")
        self.status_label.setStyleSheet("""
                                        background-color: lightgreen;
                                        color: black;
                                        border: 2px solid lightgreen;
                                        border-radius: 10px;
                                        padding: 10px;
                                    """)
        self.status_label.setText("PDFs organized successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SmartPDFManagerApp()
    window.show()

    sys.exit(app.exec())
