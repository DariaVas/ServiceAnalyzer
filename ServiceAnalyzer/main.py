import sys
from PyQt5.QtWidgets import QApplication
from user_interface import ServiceAnalyzerApp


'''
1. Outliers
2. Linear regression weights
3. Prediction 
4. K-means clustering
'''


def main():
    app = QApplication(sys.argv)
    window = ServiceAnalyzerApp()
    window.show()
    app.exec_()
    return 0


if __name__ == '__main__':
    sys.exit(main())
