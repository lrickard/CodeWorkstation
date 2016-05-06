# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ErrorDialog.ui'
#
# Created: Mon Apr 11 19:43:52 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ErrorDialog(object):
    def setupUi(self, ErrorDialog):
        ErrorDialog.setObjectName("ErrorDialog")
        ErrorDialog.resize(400, 130)
        self.gridLayout = QtWidgets.QGridLayout(ErrorDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.ErrorLabel = QtWidgets.QLabel(ErrorDialog)
        self.ErrorLabel.setObjectName("ErrorLabel")
        self.gridLayout.addWidget(self.ErrorLabel, 0, 0, 1, 1)
        self.OkayButton = QtWidgets.QPushButton(ErrorDialog)
        self.OkayButton.setObjectName("OkayButton")
        self.gridLayout.addWidget(self.OkayButton, 2, 0, 1, 1)
        self.errorMessage = QtWidgets.QLabel(ErrorDialog)
        self.errorMessage.setText("")
        self.errorMessage.setObjectName("errorMessage")
        self.gridLayout.addWidget(self.errorMessage, 1, 0, 1, 1)

        self.retranslateUi(ErrorDialog)
        QtCore.QMetaObject.connectSlotsByName(ErrorDialog)

    def retranslateUi(self, ErrorDialog):
        _translate = QtCore.QCoreApplication.translate
        ErrorDialog.setWindowTitle(_translate("ErrorDialog", "Dialog"))
        self.ErrorLabel.setText(_translate("ErrorDialog", "Error!"))
        self.OkayButton.setText(_translate("ErrorDialog", "Okay"))

