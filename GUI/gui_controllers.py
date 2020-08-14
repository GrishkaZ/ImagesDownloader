from PyQt5 import QtWidgets
import GUI.MainWindow as design
import sys


class DonwloadImagesApp(QtWidgets.QMainWindow,design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)





def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DonwloadImagesApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

