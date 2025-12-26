import sys
from PySide6.QtWidgets import QApplication
from ui.home import HomePage  # your PySide6 HomePage

def main():
    app = QApplication(sys.argv)  # create QApplication FIRST
    window = HomePage()           # then create your main window
    window.show()
    sys.exit(app.exec())          # start the PySide6 event loop

if __name__ == "__main__":
    main()
