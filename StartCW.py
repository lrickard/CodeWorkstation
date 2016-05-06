#!/usr/bin/python3
# Authors: Lukas Rickard (l_rickard@u.pacific.edu), Jake MacMillan (j_macmillan1@u.pacific.edu)
# Purpose: This python script sets up CodeWorkstation
# Details: CodeWorkstation is a productivity and scripting tool utilizing the PyQt library
# -*- coding: utf-8 -*-

import sys
import time
import subprocess
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from CommandBoxDialogUI import Ui_CommandWindowDialog
from MainWindowUI import Ui_MainWindow
from ButtonDialogUI import Ui_ButtonDialog
from CommandBoxChoiceDialogUI import Ui_CommandBoxChoiceDialog
from ErrorDialogUI import Ui_ErrorDialog


# Important Global variables -------------------------------------------------
eventer = QCoreApplication.processEvents
yesRun = True
window = None
fileToSaveTo = ""
butList = []
boxList = []
butDict = {}
boxDict = {}
# ----------------------------------------------------------------------------


class ButData:
	name = ""
	command = ""
	outputLoc = None
	buttonObj = None
	run = False


class BoxData:
	name = ""
	command = ""
	location = "b"
	output = ""
	auto = False
	interval = 1
	boxObj = None
	lastrun = 0;


def runBox(bData):
	tempProc = subprocess.Popen(bData.command.split(), stdout=subprocess.PIPE)
	tempProc.wait()
	bData.output = tempProc.communicate()[0].decode("utf-8")

def runButton(bData):
	tempProc = subprocess.Popen(bData.command.split(), stdout=subprocess.PIPE)
	tempProc.wait()
	bData.outputLoc.output = tempProc.communicate()[0].decode("utf-8")


class CWErrorDialog(QDialog): # ----------------------------------------------
	def __init__(self, errMessage, parent=None, name=None):
		super(CWErrorDialog, self).__init__(parent)
		self.ui = Ui_ErrorDialog()
		self.ui.setupUi(self)
		self.ui.OkayButton.clicked.connect(self.close)
		self.ui.errorMessage.setText(errMessage)
# END CWErrorDialog ----------------------------------------------------------


class CWButtonDialog(QDialog): # ---------------------------------------------
	def __init__(self, butData, parent=None, name=None):
		super(CWButtonDialog, self).__init__(parent) # Formality
		self.ui = Ui_ButtonDialog()
		self.ui.setupUi(self)
		self.ui.outputButton.clicked.connect(self.openCommandBoxChoiceDialog)
		if butData == None:
			self.ui.confirmButton.clicked.connect(self.saveSettings)
			self.ui.outputText.setText("Main Command Box")
			butData = ButData()
		else:
			self.ui.confirmButton.clicked.connect(self.updateSettings)
			self.ui.nameText.setText(butData.name)
			if type(butData.command) is str:
				self.ui.commandText.setText(butData.command)
			else:
				self.ui.commandText.setText("".join(butData.command))
			self.ui.outputText.setText(butData.outputLoc.name)
		self.data = butData

	def saveSettings(self):
		global buttonData
		if self.ui.nameText.text() == "" or self.ui.commandText.text() == "":
			self.errorPopup = CWErrorDialog("Error: All feilds must have appropriate values.")
			self.errorPopup.show()
		else:
			self.data.name = self.ui.nameText.text()
			self.data.command = self.ui.commandText.text()
			self.data.outputLoc = boxDict[self.ui.outputText.text()]
			newButton = CWButton()
			newButton.data = self.data
			newButton.setObjectName(self.data.name)
			newButton.setText(self.data.name)
			newButton.data.buttonObj = newButton
			window.ui.horizontalLayout.addWidget(newButton)
			butDict[self.data.name] = self.data
			butList.append(self.data)
			self.close()

	def updateSettings(self):
		self.data.command = self.ui.commandText.text()
		self.data.outputLoc = boxDict[self.ui.outputText.text()]
		self.data.buttonObj.setText = self.ui.nameText.text()
		self.data.name = self.ui.nameText.text()
		if self.data.command == "":
			self.errorPopup = CWErrorDialog("Error: Cannot have a button without a command.")
			self.errorPopup.show()
		else:
			self.data.outputLoc = boxDict[self.ui.outputText.text()]
			self.close()

	def openCommandBoxChoiceDialog(self):
		self.newCommBoxChoiceDialog = CWCommandBoxChoiceDialog(self)
		self.newCommBoxChoiceDialog.show()
# END CWButtonDialog ---------------------------------------------------------


class CWCommandBoxChoiceDialog(QDialog): # -----------------------------------
	def __init__(self, parent, same=None):
		super(CWCommandBoxChoiceDialog, self).__init__(parent) #Formality
		self.ui = Ui_CommandBoxChoiceDialog()
		self.ui.setupUi(self)
		self.ui.OkayButton.clicked.connect(self.saveSettings)
		self.ui.CancelButton.clicked.connect(self.selfDestruct)
		self.ui.tableWidget.setRowCount(len(boxList))
		self.buttonWindow = parent
		for i, box in enumerate(boxList):
			name = box.name
			listItem = QTableWidgetItem(name)
			location = box.location
			self.ui.tableWidget.setItem(i, 0, listItem)
			if location == "l":
				loc = QTableWidgetItem("Left")
			elif location == "r":
				loc = QTableWidgetItem("Right")
			elif location == "b":
				loc = QTableWidgetItem("Bottom")
			self.ui.tableWidget.setItem(i, 1, loc)

	def saveSettings(self):
		selected = self.ui.tableWidget.currentItem()	
		if selected.column() == 1:
			selected = self.ui.tableWidget.item(selected.row(), 0)
		self.buttonWindow.ui.outputText.setText(selected.text())
		self.close()

	def selfDestruct(self):
		self.close()
# END CWCommandBoxChoiceDialog -----------------------------------------------


class CWCommandBoxDialog(QDialog): # -----------------------------------------
	def __init__(self, bData, parent=None, name=None):
		super(CWCommandBoxDialog, self).__init__(parent) #Formality
		self.ui = Ui_CommandWindowDialog()
		self.ui.setupUi(self)
		self.ui.CancelButton.clicked.connect(self.selfDestruct)
		if bData == None:
			self.ui.OkayButton.clicked.connect(self.saveSettings)
		else:
			self.ui.NameText.setReadOnly(True)
			self.data = bData
			self.ui.OkayButton.clicked.connect(self.updateSettings)
			self.ui.NameText.setText(bData.name)
			print(bData.command)
			self.ui.CommandText.setText(bData.command)
			if bData.auto:
				self.ui.CBAutoUpdate.setTristate(True)
			if bData.interval == 1:
				self.ui.RB1s.toggle()
			elif bData.interval == 3:
				self.ui.RB3s.toggle()
			elif bData.interval == 5:
				self.ui.RB5s.toggle()
			else:
				self.ui.RB10s.toggle()
			if bData.location == 'l':
				self.ui.RBLeft.toggle()
			elif bData.location == 'r':
			 	self.ui.RBRight.toggle()
			else:
				self.ui.RBBottom.toggle()
	
	def checkInput(self):
		if self.ui.CBAutoUpdate.isChecked() and self.ui.CommandText.text() == "":
			self.errorPopup = CWErrorDialog("Error: Cannot auto-run without a command.")
			self.errorPopup.show()
			return False
		elif self.ui.CBAutoUpdate.isChecked() and not self.ui.RB1s.isChecked() and not self.ui.RB3s.isChecked() and not self.ui.RB5s.isChecked() and not self.ui.RB10s.isChecked():
			self.errorPopup = CWErrorDialog("Error: All fields must have appropriate values.")
			self.errorPopup.show()
			return False
		return True

	def saveSettings(self):
		global boxList, boxDict
		if self.checkInput():
			bData = BoxData()
			if self.ui.CBAutoUpdate.isChecked():
				bData.auto = True
			if self.ui.RB1s.isChecked():
				bData.interval = 1
			elif self.ui.RB3s.isChecked():
				bData.interval = 3
			elif self.ui.RB5s.isChecked():
				bData.interval = 5
			else:
				bData.interval = 10
			bData.command = self.ui.CommandText.text()
			newCommandBox = CWCommandBox(bData)# QPlainTextEdit(window.ui.dockWidgetContents_6)
			newCommandBox.setReadOnly(True)
			newCommandBox.setObjectName(self.ui.NameText.text())
			bData.name = self.ui.NameText.text()
			if self.ui.RBLeft.isChecked():
				bData.location = "l"
				window.ui.verticalLayout_2.addWidget(newCommandBox)
			elif self.ui.RBBottom.isChecked():
				bData.location = "b"
				window.ui.horizontalLayout_3.addWidget(newCommandBox)
			else:
				bData.location = "r"
				window.ui.verticalLayout.addWidget(newCommandBox)
			bData.boxObj = newCommandBox
			boxDict[bData.name] = bData
			boxList.append(bData)
			self.close()
		

	def updateSettings(self):
		global boxList, boxDict
		if self.checkInput():
			if self.ui.CBAutoUpdate.isChecked():
				self.data.auto = True
			if self.ui.RB1s.isChecked():
				self.data.interval = 1
			elif self.ui.RB3s.isChecked():
				self.data.interval = 3
			elif self.ui.RB5s.isChecked():
				self.data.interval = 5
			else:
				self.data.interval = 10
			self.data.command = self.ui.CommandText.text()
			self.data.name = self.ui.NameText.text()
			if self.ui.RBLeft.isChecked():
				if self.data.location == "r":
					window.ui.verticalLayout.removeWidget(self.data.boxObj)
				elif self.data.location == "b":
					window.ui.horizontalLayout.removeWidget(self.data.boxObj)
				if self.data.location != "l":
					self.data.location = "l"
					window.ui.verticalLayout_2.addWidget(self.data.boxObj)
			elif self.ui.RBBottom.isChecked():
				if self.data.location == "r":
					window.ui.verticalLayout.removeWidget(self.data.boxObj)
				elif self.data.location == "l":
					window.ui.verticallayout_2.removeWidget(self.data.boxObj)
				if self.data.location != "b":
					bData.location = "b"
					window.ui.horizontalLayout_3.addWidget(self.data.boxObj)
			else:
				if self.data.location == "b":
					window.ui.horizontalLayout.removeWidget(self.data.boxObj)
				elif self.data.location == "l":
					window.ui.verticalLayout_2.removeWidget(self.data.boxobj)
				if self.data.location != "r":
					bData.location = "r"
					window.ui.verticalLayout.addWidget(self.data.boxObj)
			self.close()

	def selfDestruct(self):
		self.close()
# END CWCommandBoxDialog -----------------------------------------------------


class CWButton(QPushButton): # -----------------------------------------------
	def __init__(self, parent=None, name=None):
		super(CWButton, self).__init__(parent)
		self.data = ButData()
		# Function run when Button is pressed
		self.clicked.connect(self.onClickFunction)

	def onClickFunction(self):
		self.data.run = True

	def contextMenuEvent(self, event):
		self.buttonContext = QMenu()
		self.editAction = QAction('Edit', self)
		self.editAction.triggered.connect(self.editButton)
		self.buttonContext.addAction(self.editAction)
		self.buttonContext.popup(QCursor.pos())

	def editButton(self):
		self.newButtonDialog=CWButtonDialog(self.data)
		self.newButtonDialog.show()
# END CWButton ---------------------------------------------------------------
		

class CWCommandBox(QPlainTextEdit): # ----------------------------------------
	def __init__(self, bData, parent=None, name=None):
		super(CWCommandBox, self).__init__(parent)
		if bData == None:
			bData = BoxData()
		self.data = bData
		self.setReadOnly(True)

	def contextMenuEvent(self, event):
		self.boxContext = QMenu()
		self.editAction = QAction('Edit', self)
		self.editAction.triggered.connect(self.editBox)
		self.boxContext.addAction(self.editAction)
		self.boxContext.popup(QCursor.pos())

	def editBox(self):
		self.editBoxDialog = CWCommandBoxDialog(self.data)
		self.editBoxDialog.show()
# END CWCommandBox -----------------------------------------------------------


class CWWindow(QMainWindow): # -----------------------------------------------
	# Calls the updatCBoxes function whenever this signal is heard
	updateSignal = QtCore.pyqtSignal(name='Update')

	def __init__(self, parent=None, name=None):
		global boxDict, boxList
		super(CWWindow, self).__init__(parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.actionButton.triggered.connect(self.newButton)
		self.ui.actionCommand_Window.triggered.connect(self.newCommandWindow)
		self.ui.NewButtonButton.clicked.connect(self.newButton)
		self.ui.actionSave.triggered.connect(self.save)
		self.ui.actionSave_As.triggered.connect(self.saveAs)
		self.ui.actionOpen.triggered.connect(self.openFile)
		self.newButtonDialog = None
		self.newCommandDialog = None
		self.updateSignal.connect(self.updateCBoxes)
		mainBoxData = BoxData()
		mainBoxData.name = "Main Command Box"
		mainBoxData.boxObj = self.ui.MainCommandBox
		boxDict["Main Command Box"] = mainBoxData
		boxList.append(mainBoxData)

	def updateCBoxes(self):
		for box in boxList:
			box.boxObj.setPlainText(box.output)
	
	def newButton(self):
		self.newButtonDialog=CWButtonDialog(None)
		self.newButtonDialog.show()

	def newCommandWindow(self):
		self.newCommandDialog=CWCommandBoxDialog(None)
		self.newCommandDialog.show()

	def save(self):
		if fileToSaveTo != "":
			text = self.ui.MainTextBox.toPlainText()
			fileSave = open(fileToSaveTo, 'w')
			fileSave.write(text)
			fileSave.close()
		else:
			saveAs()

	def saveAs(self):
		global fileToSaveTo
		filename = QFileDialog.getSaveFileName(self, 'Save File', '.')
		fileSave = open(filename[0], 'w')
		text = self.ui.MainTextBox.toPlainText()
		fileSave.write(text)
		fileSave.close() 
		fileToSaveTo = filename[0]

	def openFile(self):
		global fileToSaveTo
		filename = QFileDialog.getOpenFileName(self, 'Open File', '.')
		fileOpen = open(filename[0])
		data = fileOpen.read()
		self.ui.MainTextBox.setText(data)
		fileOpen.close() 
		fileToSaveTo = filename[0]

	def closeEvent(self, event):
		global yesRun
		print("CWWindow being manually closed")
		yesRun = False
		del self.newButtonDialog
		del self.newCommandDialog

	def _close_(self):
		print("CWWindow being forcibly closed")
		# Functions you place here will not run when the window closes
		# Yet it will complain if you delete a variable used here
		# This function is not very useful overall - [Lukas Rickard]

	def __del__(self):
		print("CWWindow deallocating")
# END CWMainWindow -----------------------------------------------------------


# These are examples for reference because the pyqt5 documentation is bad
"""
	def mousePressEvent(self, event):
		print(str(event.pos()))
		
	def keyPressEvent(self, event):
		print("keytest")
	
	def resizeEvent(self, event):
		print("FixStuff")

	def mouseDoubleClickEvent(self, event):
		print("doubleclick")
"""


class mainThread(QtCore.QThread): # ------------------------------------------
	def __init__(self):
		QThread.__init__(self)

	def run(self):
		index = 0
		while yesRun:
			if len(boxList) != 0:
				if boxList[index].auto:
					runBox(boxList[index])
				for btn in butList:
					if btn.run == True:
						runButton(btn)
						btn.run = False
				index = (index + 1) % len(boxList)
			if index == 0:
				time.sleep(.1)
				window.updateSignal.emit()
# END mainThread -------------------------------------------------------------


def main():
	global window
	app = QApplication(sys.argv)
	window = CWWindow()
	window.showMaximized()
	mainT = mainThread()
	mainT.start()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

