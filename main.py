import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt


class App(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Music Segmenter")
        self.setMinimumWidth(450)
        self.input_file = ""
        self.output_dir = ""
        self.init_ui()
        self.show()

    def init_ui(self) -> None:
        layout = QVBoxLayout()

        # Input file
        input_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected", self)
        self.file_label.setWordWrap(True)
        self.file_button = QPushButton("Choose MP3", self)
        self.file_button.clicked.connect(self.choose_file)
        input_layout.addWidget(self.file_label)
        input_layout.addWidget(self.file_button)

        # Output directory
        output_layout = QHBoxLayout()
        self.output_label = QLabel("No output folder selected", self)
        self.output_label.setWordWrap(True)
        self.output_button = QPushButton("Choose Output Folder", self)
        self.output_button.clicked.connect(self.choose_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_button)

        # Timestamps
        self.ts_label = QLabel("Timestamps:", self)
        self.ts_input = QLineEdit(self)
        self.ts_input.setPlaceholderText("e.g. 0:00 1:30 3:45 5:00")

        # Run button
        self.run_button = QPushButton("Start", self)
        self.run_button.clicked.connect(self.run_split)

        # Status
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.ts_label)
        layout.addWidget(self.ts_input)
        layout.addWidget(self.run_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose Audio File", "", "Audio Files (*.mp3 *.wav *.ogg)"
        )
        if path:
            self.input_file = path
            self.file_label.setText(path)

    def choose_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose Output Folder")
        if path:
            self.output_dir = path
            self.output_label.setText(path)

    def parse_time(self, t: str) -> int:
        m, s = map(int, t.split(":"))
        return m * 60 + s

    def run_split(self) -> None:
        if not self.input_file:
            QMessageBox.warning(self, "Error", "Please select an audio file first!")
            return

        if not self.output_dir:
            QMessageBox.warning(self, "Error", "Please select an output folder first!")
            return

        raw = self.ts_input.text().strip()
        if not raw:
            QMessageBox.warning(self, "Error", "Please enter timestamps!")
            return

        try:
            timestamps = [self.parse_time(t) for t in raw.split()]
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid timestamp format. Use mm:ss")
            return

        if len(timestamps) < 2:
            QMessageBox.warning(self, "Error", "At least 2 timestamps are required!")
            return

        errors = []
        for i in range(len(timestamps) - 1):
            start = timestamps[i]
            duration = timestamps[i + 1] - timestamps[i]
            output = f"{self.output_dir}/output_{i}.mp3"
            result = subprocess.run([
                "ffmpeg", "-y",
                "-i", self.input_file,
                "-ss", str(start),
                "-t", str(duration),
                "-acodec", "copy",
                output
            ], capture_output=True)
            if result.returncode != 0:
                errors.append(f"Segment {i}: ffmpeg returned an error")

        if errors:
            QMessageBox.critical(self, "Errors", "\n".join(errors))
        else:
            count = len(timestamps) - 1
            QMessageBox.information(
                self, "Done", f"Successfully created {count} segment(s)!\nSaved to: {self.output_dir}"
            )


app = QApplication(sys.argv)
window = App()
sys.exit(app.exec())