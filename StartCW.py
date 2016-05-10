#!/usr/bin/python3
# Authors: Lukas Rickard (l_rickard@u.pacific.edu), Jake MacMillan (j_macmillan1@u.pacific.edu)
# Purpose: This python script sets up CodeWorkstation
# Details: CodeWorkstation is a productivity and scripting tool utilizing the PyQt library
# -*- coding: utf-8 -*-

import sys
import time
import subprocess
import calendar
import pickle
import os.path
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from CommandBoxDialogUI import Ui_CommandBoxDialog
from MainWindowUI import Ui_MainWindow
from ButtonDialogUI import Ui_ButtonDialog
from CommandBoxChoiceDialogUI import Ui_CommandBoxChoiceDialog
from ErrorDialogUI import Ui_ErrorDialog
from ShortcutSaveDialogUI import Ui_ShortcutDialog


# Important Global variables -------------------------------------------------
eventer = QCoreApplication.processEvents
yesRun = True
window = None
fileToSaveTo = ""
butList = []
boxList = []
butDict = {}
boxDict = {}
shortcutDict = {}
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
	try:
		bData.output = subprocess.check_output(bData.command, stderr=subprocess.STDOUT, shell=True).decode("utf-8")
	except Exception as e:
		bData.output = str(e)

def runButton(bData):
	try:
		bData.outputLoc.output = subprocess.check_output(bData.command, stderr=subprocess.STDOUT, shell=True).decode("utf-8")
	except Exception as e:
		bData.outputLoc.output = str(e)


class CWErrorDialog(QDialog): # ----------------------------------------------
	def __init__(self, errMessage, parent=None, name=None):
		super(CWErrorDialog, self).__init__(parent)
		self.ui = Ui_ErrorDialog()
		self.ui.setupUi(self)
		self.ui.OkayButton.clicked.connect(self.close)
		self.ui.errorMessage.setText(errMessage)
# END CWErrorDialog ----------------------------------------------------------

class CWShortcutDialog(QDialog): # -------------------------------------------
	def __init__(self, parent=None, name=None):
		global shortcutDict
		super(CWShortcutDialog, self).__init__(parent)
		self.ui = Ui_ShortcutDialog()
		self.ui.setupUi(self)
		self.ui.saveShortcutButton.clicked.connect(self.saveShortcut)
		self.ui.okayButton.clicked.connect(self.close)
		self.ui.shortcutTable.setRowCount(len(shortcutDict.keys()))
		for but in butList:
			self.ui.functionDropdown.addItem(but.name)

		for i, key in enumerate(shortcutDict.keys()):
			k = QTableWidgetItem("Ctrl+" + key)
			fn = QTableWidgetItem(shortcutDict[key])
			self.ui.shortcutTable.setItem(i, 0, k)
			self.ui.shortcutTable.setItem(i, 1, fn)

	def saveShortcut(self):
		global shortcutDict, window
		key = self.ui.keyEntry.text().lower()
		if key == "a" or key == "u" or key == "c" or key == "v" or key == "z" or key == "x":
			self.errorPopup = CWErrorDialog("Error: the '" + key + "' key is reserved for OS text editing functions")
			self.errorPopup.show()
		elif key == "":
			self.errorPopup = CWErrorDialog("Error: Please enter a key")
			self.errorPopup.show()
		elif len(key) > 1:
			self.errorPopup = CWErrorDialog("Error: Please use only one character.")
			self.errorPopup.show()
		else:
			isIn = False
			fn = self.ui.functionDropdown.currentText()
			if fn in shortcutDict.values():
				for k in shortcutDict.keys():
					if fn == shortcutDict[k]:
						isIn = True
						if k != key: 
							del shortcutDict[k]
							break
				for act in window.ui.menuCommands.actions():
					if act.text() == fn:
						window.ui.menuCommands.removeAction(act)
						break
			for x in shortcutDict.keys():
				if x == key:
					for y in range(len(shortcutDict.keys())):
						if self.ui.shortcutTable.item(y, 0).text() ==  "Ctrl+" + key:
							self.ui.shortcutTable.removeRow(y)
							break
					del shortcutDict[x]
					break
			k = QTableWidgetItem("Ctrl+" + key)
			f = QTableWidgetItem(fn)
			shortcutDict[key] = fn
			self.ui.shortcutTable.setRowCount(len(shortcutDict.keys()))
			pos = len(shortcutDict.keys()) - 1
			if not isIn:
				self.ui.shortcutTable.setItem(pos, 0, k)
				self.ui.shortcutTable.setItem(pos, 1, f)
			else:
				for i in range(pos+1):
					if self.ui.shortcutTable.item(i, 1).text() == f.text():
						self.ui.shortcutTable.setItem(i, 0, k)
						break

			seq = QKeySequence("Ctrl+" + key)
			if fn == "Save":
				window.ui.actionSave.setShortcut(seq)
			elif fn == "Save As":
				window.ui.actionSave_As.setShortcut(seq)
			elif fn == "Open":
				window.ui.actionOpen.setShortcut(seq)
			elif fn == "Edit Shortcuts":
				window.ui.actionShortcuts.setShortcut(seq)
			elif fn == "New Button":
				window.ui.actionButton.setShortcut(seq)
			elif fn == "New Command Box":
				window.ui.actionCommand_Box.setShortcut(seq)
			elif fn == "Beginning of Line":
				window.ui.actionBoL.setShortcut(seq)
			elif fn == "End of Line":
				window.ui.actionEoL.setShortcut(seq)
			elif fn == "Delete Line":
				window.ui.actionDL.setShortcut(seq)
			elif fn == "Beginning of File":
				window.ui.actionBoF.setShortcut(seq)
			elif fn == "End of File":
				window.ui.actionEoF.setShortcut(seq)
			else:
				act = QAction(window)
				act.setText(fn)
				act.triggered.connect(butDict[fn].buttonObj.click)
				act.setShortcut(seq)
				window.ui.menuCommands.addAction(act)

			self.ui.keyEntry.setText("")

	def closeEvent(self, event):
		if self.ui.keyEntry.text() != "":
			self.saveShortcut()
# END CWShortcutDialog ------------------------------------------------------


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
		global butList, butDict
		if self.ui.nameText.text() == "" or self.ui.commandText.text() == "":
			self.errorPopup = CWErrorDialog("Error: All fields must have appropriate values.")
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
			window.ui.buttonDock.addWidget(newButton)
			butDict[self.data.name] = self.data
			butList.append(self.data)
			self.close()

	def updateSettings(self):
		global butDict, butList
		if butDict.get(self.ui.nameText.text()) != None and self.data.name != self.ui.nameText.text():
			self.errorPopup = CWErrorDialog("Error: Another button has this name")
			self.errorPopup.show()
		elif self.ui.commandText.text() == "":
			self.errorPopup = CWErrorDialog("Error: Cannot have a button without a command.")
			self.errorPopup.show()
		elif boxDict.get(self.ui.outputText.text()) == None:
			self.errorPopup = CWErrorDialog("Error: Not a valid command box")
			self.errorPopup.show()
		else:	
			self.close()
			# Saving the name for later removal of the shortcut
			oldname = self.data.name
			oldButtonObj = self.data.buttonObj
			# Removing the old button data
			for x in range(len(butList)):
				if butList[x].name == oldname:
					del butList[x]
					break
			del butDict[oldname]
			# Creating new button data
			newData = ButData()
			newData.name = self.ui.nameText.text()
			newData.command = self.ui.commandText.text()
			newData.outputLoc = boxDict[self.ui.outputText.text()]
			newData.buttonObj = oldButtonObj
			butList.append(newData)
			butDict[newData.name] = newData
			newData.buttonObj.setText(newData.name)
			# Attaching the data to the Button
			newData.buttonObj.data = newData
			# Changing the shortuct
			for key in shortcutDict.keys():
				if shortcutDict[key] == oldname:
					del shortcutDict[key]
					shortcutDict[key] = newData.name
					break
			for act in window.ui.menuCommands.actions():
				if act.text() == oldname:
					act.setText(newData.name)
					break




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
		self.ui = Ui_CommandBoxDialog()
		self.ui.setupUi(self)
		self.ui.CancelButton.clicked.connect(self.selfDestruct)
		if bData == None:
			self.ui.OkayButton.clicked.connect(self.saveSettings)
		else:
			self.ui.NameText.setReadOnly(True)
			self.data = bData
			self.ui.OkayButton.clicked.connect(self.updateSettings)
			self.ui.NameText.setText(bData.name)
			self.ui.CommandText.setText(bData.command)
			if bData.auto:
				self.ui.CBAutoUpdate.setChecked(True)
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
		if self.ui.NameText.text() == "":
		 	self.errorPopup = CWErrorDialog("Please enter a name.")
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
					window.ui.horizontalLayout_3.removeWidget(self.data.boxObj)
				if self.data.location != "l":
					self.data.location = "l"
					window.ui.verticalLayout_2.addWidget(self.data.boxObj)
			elif self.ui.RBBottom.isChecked():
				if self.data.location == "r":
					window.ui.verticalLayout.removeWidget(self.data.boxObj)
				elif self.data.location == "l":
					window.ui.verticalLayout_2.removeWidget(self.data.boxObj)
				if self.data.location != "b":
					self.data.location = "b"
					window.ui.horizontalLayout_3.addWidget(self.data.boxObj)
			else:
				if self.data.location == "b":
					window.ui.horizontalLayout_3.removeWidget(self.data.boxObj)
				elif self.data.location == "l":
					window.ui.verticalLayout_2.removeWidget(self.data.boxObj)
				if self.data.location != "r":
					self.data.location = "r"
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
		self.deleteAction = QAction('Delete', self)
		self.editAction.triggered.connect(self.editButton)
		self.deleteAction.triggered.connect(self.deleteButton)
		self.buttonContext.addAction(self.editAction)
		self.buttonContext.addAction(self.deleteAction)
		self.buttonContext.popup(QCursor.pos())
	
	def loadButton(self, but):
		self.data = but

	def editButton(self):
		self.newButtonDialog=CWButtonDialog(self.data)
		self.newButtonDialog.updateSettings()
		self.newButtonDialog.show()
	
	def deleteButton(self):
		for bindex in range(len(butList)):
			if butList[bindex].name == self.data.name:
				del butDict[self.data.name]
				del butList[bindex]				
				break
		window.ui.buttonDock.removeWidget(self)
		for key in shortcutDict.keys():
			if shortcutDict[key] == self.data.name:
				del shortcutDict[key]
				break
		for act in window.ui.menuCommands.actions():
			if act.text() == self.data.name:
				window.ui.menuCommands.removeAction(act)
				break
		self.parent = None
		self.deleteLater()
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
		self.deleteAction = QAction('Delete', self)
		self.deleteAction.triggered.connect(self.deleteBox)
		self.editAction.triggered.connect(self.editBox)
		self.boxContext.addAction(self.editAction)
		self.boxContext.addAction(self.deleteAction)
		self.boxContext.popup(QCursor.pos())

	def loadBox(self, box):
		self.data = box

	def editBox(self):
		self.editBoxDialog = CWCommandBoxDialog(self.data)
		self.editBoxDialog.show()

	def deleteBox(self):
		for bindex in range(len(butList)):
			if butList[bindex].outputLoc.name == self.data.name:
				butList[bindex].outputLoc = boxDict["Main Command Box"]
		for bindex in range(len(boxList)):
			if boxList[bindex].name == self.data.name:
				del boxDict[self.data.name]
				del boxList[bindex]
			self.parent = None
			self.deleteLater()
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
		self.ui.actionCommand_Box.triggered.connect(self.newCommandBox)
		self.ui.actionShortcuts.triggered.connect(self.newShortcut)
		self.ui.NewButtonButton.clicked.connect(self.newButton)
		self.ui.actionSave.triggered.connect(self.save)
		self.ui.actionSave_As.triggered.connect(self.saveAs)
		self.ui.actionOpen.triggered.connect(self.openFile)
		self.ui.actionSave_Settings.triggered.connect(self.saveSettings)
		self.ui.actionLoad_Settings.triggered.connect(self.loadSettings)
		self.ui.actionBoL.triggered.connect(self.beginningOfLine)
		self.ui.actionEoL.triggered.connect(self.endOfLine)
		self.ui.actionDL.triggered.connect(self.deleteLine)
		self.ui.actionBoF.triggered.connect(self.beginningOfFile)
		self.ui.actionEoF.triggered.connect(self.endOfFile)
		self.newButtonDialog = None
		self.newCommandDialog = None
		self.updateSignal.connect(self.updateCBoxes)
		self.mainBoxData = BoxData()
		self.mainBoxData.name = "Main Command Box"
		self.mainBoxData.boxObj = self.ui.MainCommandBox
		boxDict["Main Command Box"] = self.mainBoxData
		boxList.append(self.mainBoxData)

	def updateCBoxes(self):
		for box in boxList:
			if box.boxObj.toPlainText() != box.output:
				box.boxObj.setPlainText(box.output)
	
	def newButton(self):
		self.newButtonDialog=CWButtonDialog(None)
		self.newButtonDialog.show()

	def newCommandBox(self):
		self.newCommandDialog=CWCommandBoxDialog(None)
		self.newCommandDialog.show()

	def newShortcut(self):
		self.newShortcutDialog=CWShortcutDialog(self)
		self.newShortcutDialog.show()

	def save(self):
		if fileToSaveTo != "":
			text = self.ui.MainTextBox.toPlainText()
			fileSave = open(fileToSaveTo, 'w')
			fileSave.write(text)
			fileSave.close()
		else:
			self.saveAs()

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

	def beginningOfLine(self):
		cursor = self.ui.MainTextBox.textCursor()
		cursor.movePosition(3)
		self.ui.MainTextBox.setTextCursor(cursor)

	def endOfLine(self):
		cursor = self.ui.MainTextBox.textCursor()
		cursor.movePosition(13)
		self.ui.MainTextBox.setTextCursor(cursor)
	
	def deleteLine(self):
		cursor = self.ui.MainTextBox.textCursor()
		cursor.movePosition(3)
		cursor.movePosition(13, 1)
		cursor.removeSelectedText()
		cursor.movePosition(12)
		cursor.deletePreviousChar()
	
	def beginningOfFile(self):
		cursor = self.ui.MainTextBox.textCursor()
		cursor.movePosition(1)
		self.ui.MainTextBox.setTextCursor(cursor)

	def endOfFile(self):
		cursor = self.ui.MainTextBox.textCursor()
		cursor.movePosition(11)
		self.ui.MainTextBox.setTextCursor(cursor)
	
	def saveSettingsSecret(self):
		global butList, boxList, butDict, boxDict, shortcutDict
		butCList = []
		boxCList = []
		shortcutCList = []
		filename = ".cwrc"
		for but in butList:
			butC = ButData()
			butC.name = but.name
			butC.command = but.command
			butC.run = but.run
			butC.outputName = but.outputLoc.name
			butCList.append(butC)
		for box in boxList:
			boxC = BoxData()
			boxC.name = box.name
			boxC.command = box.command
			boxC.location = box.location
			boxC.output = box.output
			boxC.auto = box.auto
			boxC.interval = box.interval
			boxC.lastrun = box.lastrun
			boxCList.append(boxC)
		for key in shortcutDict.keys():
			shortcut = [key, shortcutDict[key]]
			shortcutCList.append(shortcut)
		with open(os.path.expanduser("~/") + filename, "wb") as f:
			allObjs = [butCList, boxCList, shortcutCList]
			pickle.dump(allObjs, f)

	def saveSettings(self):
		global butList, boxList, butDict, boxDict, shortcutDict
		butCList = []
		boxCList = []
		shortcutCList = []
		filename = QFileDialog.getSaveFileName(self, 'Save File', '.')
		for but in butList:
			butC = ButData()
			butC.name = but.name
			butC.command = but.command
			butC.run = but.run
			butC.outputName = but.outputLoc.name
			butCList.append(butC)
		for box in boxList:
			boxC = BoxData()
			boxC.name = box.name
			boxC.command = box.command
			boxC.location = box.location
			boxC.output = box.output
			boxC.auto = box.auto
			boxC.interval = box.interval
			boxC.lastrun = box.lastrun
			boxCList.append(boxC)
		for key in shortcutDict.keys():
			shortcut = [key, shortcutDict[key]]
			shortcutCList.append(shortcut)
		with open(filename[0], "wb") as f:
			allObjs = [butCList, boxCList, shortcutCList]
			pickle.dump(allObjs, f)
	
	def loadSettingsSecret(self):
		global butList, boxList, butDict, boxDict, shortcutDict
		filename = ".cwrc"
		if os.path.isfile(os.path.expanduser("~/") + filename):
			with open(os.path.expanduser("~/") + filename, "rb") as f:
				allObjs = pickle.load(f)
			butCList = allObjs[0]
			boxCList = allObjs[1]
			shortcutCList= allObjs[2]
			for boxC in boxCList:
				if boxC.name != "Main Command Box":
					box = BoxData()
					box.name = boxC.name
					box.command = boxC.command
					box.location = boxC.location
					box.output = boxC.output
					box.auto = boxC.auto
					box.interval = boxC.interval
					box.lastrun = boxC.lastrun
					boxOb = CWCommandBox(box)
					boxOb.loadBox(box)
					boxOb.setObjectName(box.name)
					box.boxObj = boxOb
					boxDict[box.name] = box 
					boxList.append(box)
					if box.location == "l": 
						window.ui.verticalLayout_2.addWidget(boxOb)
					elif box.location == "b":
						window.ui.horizontalLayout_3.addWidget(boxOb)
					else:
						window.ui.verticalLayout.addWidget(boxOb)

			for butC in butCList:
				but = ButData()
				but.name = butC.name
				but.command = butC.command
				but.run = butC.run
				butOb = CWButton()
				butOb.loadButton(but)
				butOb.setObjectName(but.name)
				butOb.setText(but.name)
				but.buttonObj = butOb
				but.outputLoc = boxDict[butC.outputName]
				butDict[but.name] = but
				butList.append(but)
				window.ui.buttonDock.addWidget(butOb)

			for shortcut in shortcutCList:
				key = shortcut[0]
				fn = shortcut[1]
				shortcutDict[key] = fn
				seq = QKeySequence("Ctrl+" + key)
				if fn == "Save":
					window.ui.actionSave.setShortcut(seq)
				elif fn == "Save As":
					window.ui.actionSave_As.setShortcut(seq)
				elif fn == "Open":
					window.ui.actionOpen.setShortcut(seq)
				elif fn == "Edit Shortcuts":
					window.ui.actionShortcuts.setShortcut(seq)
				elif fn == "New Button":
					window.ui.actionButton.setShortcut(seq)
				elif fn == "New Command Box":
					window.ui.actionCommand_Box.setShortcut(seq)
				elif fn == "Beginning of Line":
					window.ui.actionBoL.setShortcut(seq)
				elif fn == "End of Line":
					window.ui.actionEoL.setShortcut(seq)
				elif fn == "Delete Line":
					window.ui.actionDL.setShortcut(seq)
				elif fn == "Beginning of File":
					window.ui.actionBoF.setShortcut(seq)
				elif fn == "End of File":
					window.ui.actionEoF.setShortcut(seq)
				else:
					act = QAction(window)
					act.setText(fn)
					act.triggered.connect(butDict[fn].buttonObj.click)
					act.setShortcut(seq)
					window.ui.menuCommands.addAction(act)

	def loadSettings(self):
		global butList, boxList, butDict, boxDict, shortcutDict
		filename = QFileDialog.getOpenFileName(self, 'Open File', '.')
		with open(filename[0], "rb") as f:
			allObjs = pickle.load(f)
		butCList = allObjs[0]
		boxCList = allObjs[1]
		shortcutCList= allObjs[2]
		for but in butList:
			window.ui.buttonDock.removeWidget(but.buttonObj)
			for act in window.ui.menuCommands.actions():
				if act.text() == but.name:
					window.ui.menuCommands.removeAction(act)
					break
			but.buttonObj.parent = None
			but.buttonObj.deleteLater()
		for box in boxList:
			if box.name != "Main Command Box":
				box.boxObj.deleteBox()
		butList = []
		butDict = {}
		boxList = []
		boxDict = {}
		shortcutDict = {}
		boxDict["Main Command Box"] = window.mainBoxData
		boxList.append(window.mainBoxData)
#for key in shortcutDict.keys():
#			del shortcutDict[key]
		for boxC in boxCList:
			if boxC.name != "Main Command Box":
				box = BoxData()
				box.name = boxC.name
				box.command = boxC.command
				box.location = boxC.location
				box.output = boxC.output
				box.auto = boxC.auto
				box.interval = boxC.interval
				box.lastrun = boxC.lastrun
				boxOb = CWCommandBox(box)
				boxOb.loadBox(box)
				boxOb.setObjectName(box.name)
				box.boxObj = boxOb
				boxDict[box.name] = box 
				boxList.append(box)
				if box.location == "l": 
					window.ui.verticalLayout_2.addWidget(boxOb)
				elif box.location == "b":
					window.ui.horizontalLayout_3.addWidget(boxOb)
				else:
					window.ui.verticalLayout.addWidget(boxOb)

		for butC in butCList:
			but = ButData()
			but.name = butC.name
			but.command = butC.command
			but.run = butC.run
			butOb = CWButton()
			butOb.loadButton(but)
			butOb.setObjectName(but.name)
			butOb.setText(but.name)
			but.buttonObj = butOb
			but.outputLoc = boxDict[butC.outputName]
			butDict[but.name] = but
			butList.append(but)
			window.ui.buttonDock.addWidget(butOb)

		for shortcut in shortcutCList:
			key = shortcut[0]
			fn = shortcut[1]
			shortcutDict[key] = fn
			seq = QKeySequence("Ctrl+" + key)
			if fn == "Save":
				window.ui.actionSave.setShortcut(seq)
			elif fn == "Save As":
				window.ui.actionSave_As.setShortcut(seq)
			elif fn == "Open":
				window.ui.actionOpen.setShortcut(seq)
			elif fn == "Edit Shortcuts":
				window.ui.actionShortcuts.setShortcut(seq)
			elif fn == "New Button":
				window.ui.actionButton.setShortcut(seq)
			elif fn == "New Command Box":
				window.ui.actionCommand_Box.setShortcut(seq)
			elif fn == "Beginning of Line":
				window.ui.actionBoL.setShortcut(seq)
			elif fn == "End of Line":
				window.ui.actionEoL.setShortcut(seq)
			elif fn == "Delete Line":
				window.ui.actionDL.setShortcut(seq)
			elif fn == "Beginning of File":
				window.ui.actionBoF.setShortcut(seq)
			elif fn == "End of File":
				window.ui.actionEoF.setShortcut(seq)
			else:
				act = QAction(window)
				act.setText(fn)
				act.triggered.connect(butDict[fn].buttonObj.click)
				act.setShortcut(seq)
				window.ui.menuCommands.addAction(act)

	def closeEvent(self, event):
		global yesRun
		print("CWWindow being manually closed")
		yesRun = False
		del self.newButtonDialog
		del self.newCommandDialog
		self.saveSettingsSecret()
		
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
					if (calendar.timegm(time.gmtime()) - boxList[index].lastrun) >= boxList[index].interval:
						runBox(boxList[index])
						boxList[index].lastrun = calendar.timegm(time.gmtime())
				for btn in butList:
					if btn.run == True:
						runButton(btn) # TODO Run these Async with thread and check performance
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
	window.loadSettingsSecret()
	window.showMaximized()
	mainT = mainThread()
	mainT.start()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

