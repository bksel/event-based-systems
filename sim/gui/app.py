import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PySide6 + uv")
        self._count = 0

        self._label = QLabel("Clicked 0 times")
        button = QPushButton("Click me")
        button.clicked.connect(self._on_click)

        layout = QVBoxLayout(self)
        layout.addWidget(self._label)
        layout.addWidget(button)

    @Slot()
    def _on_click(self) -> None:
        self._count += 1
        self._label.setText(f"Clicked {self._count} times")


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(300, 120)
    window.show()
    return app.exec()
