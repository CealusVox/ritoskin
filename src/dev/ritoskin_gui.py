import sys
import subprocess
import os
import shutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QLineEdit
from PyQt6.QtCore import QProcess, Qt, pyqtSignal

class MainWindow(QMainWindow):
    input_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RitoSkin - Contact: nylish.me")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create terminal output display
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        layout.addWidget(self.terminal_output)

        # Create input line
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter input here...")
        self.input_line.returnPressed.connect(self.send_input)
        self.input_line.setEnabled(False)
        layout.addWidget(self.input_line)

        # Create button layout
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Create "Delete Images Folder" button
        self.delete_folder_button = QPushButton("Delete Images Folder")
        self.delete_folder_button.clicked.connect(self.delete_folder)
        button_layout.addWidget(self.delete_folder_button)

        # Create "Run Program" button
        self.run_program_button = QPushButton("Run Program")
        self.run_program_button.clicked.connect(self.run_program)
        button_layout.addWidget(self.run_program_button)

        # Create "Scrap Loading Screen" button
        self.scrap_loading_screen_button = QPushButton("Scrap Loading Screen")
        self.scrap_loading_screen_button.clicked.connect(self.scrap_tex_to_dds)
        button_layout.addWidget(self.scrap_loading_screen_button)

        # Set up QProcess for running the main program
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.input_ready.connect(self.write_to_process)

        # Set up QProcess for scraping
        self.scrape_process = QProcess(self)
        self.scrape_process.readyReadStandardOutput.connect(self.handle_scrape_stdout)
        self.scrape_process.readyReadStandardError.connect(self.handle_scrape_stderr)
        self.scrape_process.finished.connect(self.handle_scrape_finished)

    def scrap_tex_to_dds(self):
        script_path = os.path.join("../resources", "scrap_tex_to_dds.py")
        if os.path.exists(script_path):
            self.terminal_output.append("Starting to scrape loading screen...")
            self.scrap_loading_screen_button.setEnabled(False)
            self.scrape_process.start(sys.executable, [script_path])
        else:
            self.terminal_output.append(f"Error: {script_path} not found.")

    def handle_scrape_stdout(self):
        data = self.scrape_process.readAllStandardOutput().data().decode(errors='replace')
        self.terminal_output.append(data.strip())

    def handle_scrape_stderr(self):
        data = self.scrape_process.readAllStandardError().data().decode(errors='replace')
        self.terminal_output.append(f"Scraping Error: {data.strip()}")

    def handle_scrape_finished(self, exit_code, exit_status):
        if exit_status == QProcess.ExitStatus.NormalExit:
            self.terminal_output.append("Scraping loading screen finished successfully.")
        else:
            self.terminal_output.append(f"Scraping process crashed or was killed. Exit code: {exit_code}")
        self.scrap_loading_screen_button.setEnabled(True)

    def delete_folder(self):
        images_folder = "images"
        if os.path.exists(images_folder):
            try:
                shutil.rmtree(images_folder)
                self.terminal_output.append(f"Deleted '{images_folder}' folder.")
            except Exception as e:
                self.terminal_output.append(f"Error deleting '{images_folder}' folder: {str(e)}")
        else:
            self.terminal_output.append(f"'{images_folder}' folder not found.")

    def run_program(self):
        program = "./ritoskin.exe"
        if os.path.exists(program):
            self.process.start(program)
            self.run_program_button.setEnabled(False)
            self.input_line.setEnabled(True)
            self.input_line.setFocus()
        else:
            self.terminal_output.append(f"Error: {program} not found.")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        self.terminal_output.append(data.strip())

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='replace')
        self.terminal_output.append(data.strip())

    def handle_finished(self):
        self.terminal_output.append("Program finished.")
        self.run_program_button.setEnabled(True)
        self.input_line.setEnabled(False)

    def send_input(self):
        text = self.input_line.text()
        if text:
            self.input_ready.emit(text)
            self.terminal_output.append(f"> {text}")
            self.input_line.clear()

    def write_to_process(self, text):
        self.process.write((text + '\n').encode())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())