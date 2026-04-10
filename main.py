import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt


class AudioSplitter(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Music Segmenter")
        self.setMinimumWidth(500)
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
        self.file_button = QPushButton("Choose Audio", self)
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

        # Timestamps input
        self.ts_label = QLabel("Timestamps with track names (one per line):", self)
        self.ts_input = QTextEdit(self)
        self.ts_input.setPlaceholderText(
            "00:00 Track Name\n03:18 Track Name\n05:30 Track Name"
        )
        self.ts_input.setMinimumHeight(160)

        # Run button
        self.run_button = QPushButton("Split Audio", self)
        self.run_button.clicked.connect(self.run_split)

        # Status
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)

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
        parts = list(map(int, t.split(":")))
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        raise ValueError(f"Invalid time format: {t}")

    def sanitize_filename(self, name: str) -> str:
        forbidden = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for ch in forbidden:
            name = name.replace(ch, '_')
        return name.strip()

    def parse_lines(self, text: str) -> list[tuple[int, str]]:
        entries = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)  # split on first whitespace only
            if len(parts) < 2:
                raise ValueError(f"Missing track name on line: '{line}'")
            timestamp, name = parts[0], parts[1].strip()
            entries.append((self.parse_time(timestamp), self.sanitize_filename(name)))
        return entries

    def run_split(self) -> None:
        if not self.input_file:
            QMessageBox.warning(self, "Error", "Please select an audio file first!")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "Error", "Please select an output folder first!")
            return

        raw = self.ts_input.toPlainText().strip()
        if not raw:
            QMessageBox.warning(self, "Error", "Please enter timestamps!")
            return

        try:
            entries = self.parse_lines(raw)
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Parse error: {e}")
            return

        if len(entries) < 2:
            QMessageBox.warning(self, "Error", "At least 2 entries are required!")
            return

        errors = []
        for i in range(len(entries) - 1):
            start = entries[i][0]
            name = entries[i][1]
            duration = entries[i + 1][0] - start
            output = f"{self.output_dir}/{name}.mp3"
            result = subprocess.run([
                "ffmpeg", "-y",
                "-i", self.input_file,
                "-ss", str(start),
                "-t", str(duration),
                "-acodec", "copy",
                output
            ], capture_output=True)
            if result.returncode != 0:
                errors.append(f"'{name}': ffmpeg error")

        last_start = entries[-1][0]
        last_name = entries[-1][1]
        output = f"{self.output_dir}/{last_name}.mp3"
        result = subprocess.run([
            "ffmpeg", "-y",
            "-i", self.input_file,
            "-ss", str(last_start),
            "-acodec", "copy",
            output
        ], capture_output=True)
        if result.returncode != 0:
            errors.append(f"'{last_name}': ffmpeg error")

        if errors:
            QMessageBox.critical(self, "Errors", "\n".join(errors))
        else:
            count = len(entries)
            QMessageBox.information(
                self, "Done", f"Successfully created {count} track(s)!\nSaved to: {self.output_dir}"
            )


app = QApplication(sys.argv)
window = AudioSplitter()
sys.exit(app.exec())