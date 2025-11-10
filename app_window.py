# Copyright (c) 2025 Abhishek Vashisth
# All Rights Reserved.
# This software is proprietary and confidential.
# Unauthorized copying, modification, or distribution is strictly prohibited.

import os

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, window):
        window.setObjectName("MainWindow")
        window.resize(1100, 700)  # Larger default size for modern look

        # Central widget and main horizontal layout
        self.centralWidget = QtWidgets.QWidget(window)
        self.centralWidget.setObjectName("centralWidget")
        self.mainLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.mainLayout.setContentsMargins(24, 24, 24, 24)  # left top right bottom
        self.mainLayout.setSpacing(24)

        # ---- Left panel: Device selection + display ----
        self.leftPanel = QtWidgets.QVBoxLayout()
        self.leftPanel.setSpacing(18)
        self.leftPanel.setContentsMargins(0, 0, 0, 0)

        # --- Top row: logo + brand + device combo + refresh ---
        self.topLeftLayout = QtWidgets.QHBoxLayout()
        self.topLeftLayout.setSpacing(8)
        self.topLeftLayout.setContentsMargins(0, 0, 0, 0)

        self.lblLogo = QtWidgets.QLabel()
        self.lblLogo.setFixedSize(250, 150)
        self.lblLogo.setScaledContents(True)
        logo_path = os.path.join(os.path.dirname(__file__), "main_logo.png")
        # logo_path = os.path.join(os.path.dirname(__file__), "avidia.png")
        if os.path.exists(logo_path):
            self.lblLogo.setPixmap(QtGui.QPixmap(logo_path))
        self.topLeftLayout.addWidget(self.lblLogo)

        # self.lblBrand = QtWidgets.QLabel("Foamatomatic International Technologies")
        self.lblBrand = QtWidgets.QLabel("Avidia")
        self.lblBrand.setObjectName("lblBrand")
        self.lblBrand.setStyleSheet("""
    color: #007BFF;            /* elegant blue tone similar to your logo */
    font-size: 28px;
    font-weight: 700;
    font-family: 'Montserrat', 'Poppins', 'Segoe UI', sans-serif;
    letter-spacing: 2px;
""")
        self.lblBrand.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        self.lblBrand.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.topLeftLayout.addWidget(self.lblBrand)

        self.ComboDevices = QtWidgets.QComboBox()
        self.ComboDevices.setMinimumHeight(32)
        self.ComboDevices.setMaximumWidth(400)
        self.ComboDevices.setObjectName("ComboDevices")
        self.topLeftLayout.addWidget(self.ComboDevices)

        self.btnRefresh = QtWidgets.QPushButton("🔃")
        self.btnRefresh.setObjectName("btnRefresh")
        self.btnRefresh.setFixedSize(36, 32)
        self.btnRefresh.setToolTip("Refresh/Restart Application")
        self.topLeftLayout.addWidget(self.btnRefresh)

        self.topLeftLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.topLeftLayout.setSpacing(26)
        self.leftPanel.addLayout(self.topLeftLayout)

        # Display widget (placeholder for camera/image)
        self.widgetDisplay = QtWidgets.QLabel()
        self.widgetDisplay.setFixedSize(1366, 768)
        self.widgetDisplay.setScaledContents(True)
        self.widgetDisplay.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        self.widgetDisplay.setAlignment(QtCore.Qt.AlignCenter)
        self.widgetDisplay.setStyleSheet("background: rgba(30,30,30,0.85); border-radius: 18px; border: 2px solid #2e8fff;")
        self.widgetDisplay.setObjectName("widgetDisplay")
        self.leftPanel.addWidget(self.widgetDisplay, stretch=1)

        # ====== Right: we will build widgets first, then place them into tabs ======
        # Keep your object names so external code continues to work.

        # --- Initialization Group ---
        self.groupInit = QtWidgets.QGroupBox()
        self.groupInit.setObjectName("groupInit")
        self.initLayout = QtWidgets.QGridLayout(self.groupInit)
        self.initLayout.setContentsMargins(12, 12, 12, 12)
        self.initLayout.setSpacing(10)

        self.bnEnum = QtWidgets.QPushButton()
        self.bnEnum.setObjectName("bnEnum")
        self.initLayout.addWidget(self.bnEnum, 0, 0, 1, 2)

        self.bnOpen = QtWidgets.QPushButton()
        self.bnOpen.setObjectName("bnOpen")
        self.initLayout.addWidget(self.bnOpen, 1, 0)

        self.bnClose = QtWidgets.QPushButton()
        self.bnClose.setEnabled(False)
        self.bnClose.setObjectName("bnClose")
        self.initLayout.addWidget(self.bnClose, 1, 1)

        self.btnUploadImage = QtWidgets.QPushButton("Upload Image")
        self.btnUploadImage.setObjectName("btnUploadImage")
        self.btnUploadImage.setMaximumWidth(210)
        self.initLayout.addWidget(self.btnUploadImage, 2, 0, 1, 1)

        self.btnLoadModel = QtWidgets.QPushButton()
        self.btnLoadModel.setObjectName("btnLoadModel")
        self.btnLoadModel.setMaximumWidth(210)
        self.initLayout.addWidget(self.btnLoadModel, 2, 1, 1, 1)

        self.lblModel = QtWidgets.QLabel()
        self.lblModel.setObjectName("lblModel")
        self.lblModel.setText("Model: (none)")
        self.lblModel.setStyleSheet("color: #7ee787; font-size: 13px;")
        self.lblModel.setWordWrap(True)
        self.initLayout.addWidget(self.lblModel, 3, 0, 1, 2)

        # --- Acquisition Group ---
        self.groupGrab = QtWidgets.QGroupBox()
        self.groupGrab.setEnabled(False)
        self.groupGrab.setObjectName("groupGrab")
        self.grabLayout = QtWidgets.QGridLayout(self.groupGrab)
        self.grabLayout.setContentsMargins(12, 12, 12, 12)
        self.grabLayout.setSpacing(10)

        self.radioContinueMode = QtWidgets.QRadioButton()
        self.radioContinueMode.setObjectName("radioContinueMode")
        self.grabLayout.addWidget(self.radioContinueMode, 0, 0)

        self.radioTriggerMode = QtWidgets.QRadioButton()
        self.radioTriggerMode.setObjectName("radioTriggerMode")
        self.grabLayout.addWidget(self.radioTriggerMode, 0, 1)

        self.bnStart = QtWidgets.QPushButton()
        self.bnStart.setEnabled(False)
        self.bnStart.setObjectName("bnStart")
        self.grabLayout.addWidget(self.bnStart, 1, 0)

        self.bnStop = QtWidgets.QPushButton()
        self.bnStop.setEnabled(False)
        self.bnStop.setObjectName("bnStop")
        self.grabLayout.addWidget(self.bnStop, 1, 1)

        self.bnSoftwareTrigger = QtWidgets.QPushButton()
        self.bnSoftwareTrigger.setEnabled(False)
        self.bnSoftwareTrigger.setObjectName("bnSoftwareTrigger")
        self.grabLayout.addWidget(self.bnSoftwareTrigger, 2, 0, 1, 2)

        self.bnSaveImage = QtWidgets.QPushButton()
        self.bnSaveImage.setEnabled(False)
        self.bnSaveImage.setObjectName("bnSaveImage")
        self.grabLayout.addWidget(self.bnSaveImage, 3, 0, 1, 2)

        # --- Last NG mini panel (QA summary) ---
        self.groupNG = QtWidgets.QGroupBox()
        self.groupNG.setObjectName("groupNG")
        ngLayout = QtWidgets.QVBoxLayout(self.groupNG)
        ngLayout.setContentsMargins(12, 12, 12, 12)
        ngLayout.setSpacing(8)

        self.lblLastNG = QtWidgets.QLabel()
        self.lblLastNG.setObjectName("lblLastNG")
        self.lblLastNG.setAlignment(QtCore.Qt.AlignCenter)
        self.lblLastNG.setMinimumSize(220, 140)
        self.lblLastNG.setStyleSheet("background: #101317; border: 1px dashed #2e8fff; border-radius: 8px;")
        self.lblLastNG.setText("No NG yet")
        self.lblLastNG.setScaledContents(True)
        ngLayout.addWidget(self.lblLastNG)

        self.btnReviewNG = QtWidgets.QPushButton()
        self.btnReviewNG.setObjectName("btnReviewNG")
        ngLayout.addWidget(self.btnReviewNG)

        # --- Parameters (Camera tab) ---
        self.groupParam = QtWidgets.QGroupBox()
        self.groupParam.setEnabled(False)
        self.groupParam.setObjectName("groupParam")
        self.groupParam.setMinimumWidth(220)
        self.groupParam.setMaximumWidth(260)
        self.paramLayout = QtWidgets.QGridLayout(self.groupParam)
        self.paramLayout.setContentsMargins(12, 12, 12, 12)
        self.paramLayout.setSpacing(10)

        self.label_4 = QtWidgets.QLabel()
        self.label_4.setObjectName("label_4")
        self.paramLayout.addWidget(self.label_4, 0, 0)
        self.edtExposureTime = QtWidgets.QLineEdit()
        self.edtExposureTime.setObjectName("edtExposureTime")
        self.paramLayout.addWidget(self.edtExposureTime, 0, 1)

        self.label_5 = QtWidgets.QLabel()
        self.label_5.setObjectName("label_5")
        self.paramLayout.addWidget(self.label_5, 1, 0)
        self.edtGain = QtWidgets.QLineEdit()
        self.edtGain.setObjectName("edtGain")
        self.paramLayout.addWidget(self.edtGain, 1, 1)

        self.label_6 = QtWidgets.QLabel()
        self.label_6.setObjectName("label_6")
        self.paramLayout.addWidget(self.label_6, 2, 0)
        self.edtFrameRate = QtWidgets.QLineEdit()
        self.edtFrameRate.setObjectName("edtFrameRate")
        self.paramLayout.addWidget(self.edtFrameRate, 2, 1)

        self.bnGetParam = QtWidgets.QPushButton()
        self.bnGetParam.setObjectName("bnGetParam")
        self.paramLayout.addWidget(self.bnGetParam, 3, 0)
        self.bnSetParam = QtWidgets.QPushButton()
        self.bnSetParam.setObjectName("bnSetParam")
        self.paramLayout.addWidget(self.bnSetParam, 3, 1)

        # --- Status Box (Logs tab) ---
        self.statusBox = QtWidgets.QTextEdit()
        self.statusBox.setReadOnly(True)
        self.statusBox.setMinimumHeight(80)
        self.statusBox.setMinimumWidth(220)
        self.statusBox.setObjectName("statusBox")
        self.statusBox.setStyleSheet("background: #181c20; color: #7ee787; border-radius: 10px; font-size: 14px;")

        # --- OK/NG Status row (Run tab footer) ---
        self.statusRow = QtWidgets.QHBoxLayout()
        self.statusRow.setContentsMargins(0, 0, 0, 0)
        self.statusRow.setSpacing(8)

        self.btnPartStatus = QtWidgets.QPushButton("—")
        self.btnPartStatus.setObjectName("btnPartStatus")
        self.btnPartStatus.setEnabled(False)  # display-only
        self.btnPartStatus.setMinimumHeight(44)
        self.btnPartStatus.setMinimumWidth(140)
        self.btnPartStatus.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                font-size: 18px;
                font-weight: 700;
                background-color: #444;
                color: #ddd;
            }
        """)

        self.lblDetectionTime = QtWidgets.QLabel("Detection Time: 0.0 s")
        self.lblDetectionTime.setObjectName("lblDetectionTime")
        self.lblDetectionTime.setStyleSheet("color: #7ee787; font-size: 14px; font-weight: 600;")
        self.lblDetectionTime.setAlignment(QtCore.Qt.AlignCenter)

        self.btnClearTime = QtWidgets.QPushButton("Clear")
        self.btnClearTime.setObjectName("btnClearTime")
        self.btnClearTime.setMinimumHeight(36)
        self.btnClearTime.setMinimumWidth(140)
        self.btnClearTime.setStyleSheet("""
            QPushButton {
                background-color: #2e8fff;
                color: white;
                border-radius: 12px;
                font-weight: 600;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #7ee787;
                color: #222;
            }
        """)

        self.statusLayoutVertical = QtWidgets.QVBoxLayout()
        self.statusLayoutVertical.setContentsMargins(0, 0, 0, 0)
        self.statusLayoutVertical.setSpacing(8)
        self.statusLayoutVertical.addWidget(self.btnPartStatus)
        self.statusLayoutVertical.addWidget(self.lblDetectionTime)
        self.statusLayoutVertical.addWidget(self.btnClearTime)

        self.statusRow.addStretch(1)
        self.statusRow.addLayout(self.statusLayoutVertical)
        self.statusRow.addStretch(1)

        # ====== TABS on the right ======
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QtWidgets.QTabWidget.North)

        # Tab: Run (operator)
        self.tabRun = QtWidgets.QWidget()
        self.tabRunLayout = QtWidgets.QVBoxLayout(self.tabRun)
        self.tabRunLayout.setContentsMargins(0, 0, 0, 0)
        self.tabRunLayout.setSpacing(12)
        self.tabRunLayout.addWidget(self.groupInit)
        self.tabRunLayout.addWidget(self.groupGrab)
        self.tabRunLayout.addLayout(self.statusRow)
        self.tabRunLayout.addStretch(1)
        self.tabs.addTab(self.tabRun, "Run")

        # Tab: Camera (parameters)
        self.tabCamera = QtWidgets.QWidget()
        self.tabCameraLayout = QtWidgets.QVBoxLayout(self.tabCamera)
        self.tabCameraLayout.setContentsMargins(8, 8, 8, 8)
        self.tabCameraLayout.setSpacing(12)
        self.tabCameraLayout.addWidget(self.groupParam)
        self.tabCameraLayout.addStretch(1)
        self.tabs.addTab(self.tabCamera, "Camera")

        # Tab: QA (Last NG + gallery entry)
        self.tabQA = QtWidgets.QScrollArea()
        self.tabQA.setWidgetResizable(True)
        self.qaInner = QtWidgets.QWidget()
        self.qaLayout = QtWidgets.QVBoxLayout(self.qaInner)
        self.qaLayout.setContentsMargins(8, 8, 8, 8)
        self.qaLayout.setSpacing(12)
        self.qaLayout.addWidget(self.groupNG)
        self.qaLayout.addStretch(1)
        self.tabQA.setWidget(self.qaInner)
        self.tabs.addTab(self.tabQA, "QA")

        # Tab: Logs (status box)
        self.tabLogs = QtWidgets.QWidget()
        self.tabLogsLayout = QtWidgets.QVBoxLayout(self.tabLogs)
        self.tabLogsLayout.setContentsMargins(8, 8, 8, 8)
        self.tabLogsLayout.setSpacing(12)
        self.tabLogsLayout.addWidget(self.statusBox)
        self.tabs.addTab(self.tabLogs, "Logs")

        # ====== Splitter: left (live) | right (tabs) ======
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self.centralWidget)
        self.leftContainer = QtWidgets.QWidget()
        self.leftContainer.setLayout(self.leftPanel)

        self.rightContainer = QtWidgets.QWidget()
        self.rightContainerLayout = QtWidgets.QVBoxLayout(self.rightContainer)
        self.rightContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.rightContainerLayout.setSpacing(0)
        self.rightContainerLayout.addWidget(self.tabs)

        self.splitter.addWidget(self.leftContainer)
        self.splitter.addWidget(self.rightContainer)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 1)

        # Put splitter into main layout (instead of adding left/right layouts directly)
        self.mainLayout.addWidget(self.splitter)

        window.setCentralWidget(self.centralWidget)

        self.retranslateUi(window)
        QtCore.QMetaObject.connectSlotsByName(window)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupInit.setTitle(_translate("MainWindow", "Initialization"))
        self.bnClose.setText(_translate("MainWindow", "Close Device"))
        self.bnOpen.setText(_translate("MainWindow", "Open Device"))
        self.bnEnum.setText(_translate("MainWindow", "Find Devices"))
        self.groupGrab.setTitle(_translate("MainWindow", "Acquisition"))
        self.bnSaveImage.setText(_translate("MainWindow", "Save Image"))
        self.radioContinueMode.setText(_translate("MainWindow", "Continuous Mode"))
        self.radioTriggerMode.setText(_translate("MainWindow", "Trigger Mode"))
        self.bnStop.setText(_translate("MainWindow", "Stop Acquisition"))
        self.bnStart.setText(_translate("MainWindow", "Start Acquisition"))
        self.bnSoftwareTrigger.setText(_translate("MainWindow", "Software Trigger Once"))
        self.groupParam.setTitle(_translate("MainWindow", "Parameters"))
        self.label_6.setText(_translate("MainWindow", "Frame Rate"))
        self.edtGain.setText(_translate("MainWindow", "0"))
        self.label_5.setText(_translate("MainWindow", "Gain"))
        self.label_4.setText(_translate("MainWindow", "Exposure"))
        self.edtExposureTime.setText(_translate("MainWindow", "0"))
        self.bnGetParam.setText(_translate("MainWindow", "Get"))
        self.bnSetParam.setText(_translate("MainWindow", "Set"))
        self.edtFrameRate.setText(_translate("MainWindow", "0"))
        self.btnLoadModel.setText(_translate("MainWindow", "Load Model"))
        self.lblModel.setText(_translate("MainWindow", "Model: (none)"))
        self.groupNG.setTitle(_translate("MainWindow", "Last NG"))
        self.btnReviewNG.setText(_translate("MainWindow", "Review NG (0)"))
