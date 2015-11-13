#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

class CWWindow(QMainWindow):
	def __init__(self, parent=None, name=None):
		# Formalities
		super(CWWindow, self).__init__(parent)
		print("test")
		mainLayout = QHBoxLayout()
		# Setting Text editor Settings
		self.textEditor = QTextEdit()
		
		mainLayout.addWidget(self.textEditor, 1)
		mainWidget = QWidget()
		mainWidget.setLayout(mainLayout)
		self.setCentralWidget(mainWidget)

	def mousePressEvent(self, event):
		print(str(event.pos()))

	def keyPressEvent(self, event):
		print("keytest")
	
	def resizeEvent(self, event):
		print("FixStuff")
		
"""
class cboxDock(QDockWidget):
	def __init__(self, title, parent):
		super(QDockWidget, self).__init__(parent)
"""

def main():
	app = QApplication(sys.argv)
	window = CWWindow()
	window.resize(640, 480)
	window.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

