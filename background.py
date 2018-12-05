# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'background.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BackGround(object):
    def setupUi(self, BackGround):
        BackGround.setObjectName("BackGround")
        BackGround.resize(1920, 1080)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 26, 44))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 26, 44))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 26, 44))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(42, 26, 44))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        BackGround.setPalette(palette)
        self.centralwidget = QtWidgets.QWidget(BackGround)
        self.centralwidget.setObjectName("centralwidget")
        BackGround.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(BackGround)
        self.statusbar.setObjectName("statusbar")
        BackGround.setStatusBar(self.statusbar)

        self.retranslateUi(BackGround)
        QtCore.QMetaObject.connectSlotsByName(BackGround)

    def retranslateUi(self, BackGround):
        _translate = QtCore.QCoreApplication.translate
        BackGround.setWindowTitle(_translate("BackGround", "MainWindow"))

