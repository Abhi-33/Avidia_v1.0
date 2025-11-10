# -*- coding: utf-8 -*-
# Copyright (c) 2025 Abhishek Vashisth
# All Rights Reserved.
# This software is proprietary and confidential.
# Unauthorized copying, modification, or distribution is strictly prohibited.

import sys
from PyQt5.QtWidgets import *
from CamOperation_class import CameraOperation 
from MvImport.MvCameraControl_class import *
from MvImport.MvErrorDefine_const import *
from MvImport.CameraParams_header import *
# from UI import Ui_MainWindow
from app_window import Ui_MainWindow
import ctypes
import cv2
import os
import subprocess
import qdarktheme
from PyQt5.QtGui import QImage , QPixmap
from PyQt5.QtCore import Qt, QTimer, QDateTime , pyqtSignal  , QObject



import logging
logging.basicConfig(level=logging.INFO)

# Get the index of the selected device information by parsing the characters inside the []
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()


# Convert the returned error code to hexadecimal for display
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr


if __name__ == "__main__":
    print("[!! WELCOME !!] Starting Vision Inspection System !!")
    global deviceList
    deviceList = MV_CC_DEVICE_INFO_LIST()
    global cam
    cam = MvCamera()
    global nSelCamIndex
    nSelCamIndex = 0
    global obj_cam_operation
    obj_cam_operation = 0
    global isOpen
    isOpen = False
    global isGrabbing
    isGrabbing = False
    global isCalibMode  # Whether it's calibration mode (to get the raw image)
    isCalibMode = True
    
#
# Bind the dropdown list to the device information index
    def xFunc(event):
        global nSelCamIndex
        nSelCamIndex = TxtWrapBy("[", "]", ui.ComboDevices.get())

    # Decoding Characters
    def decoding_char(c_ubyte_value):
        c_char_p_value = ctypes.cast(c_ubyte_value, ctypes.c_char_p)
        try:
            decode_str = c_char_p_value.value.decode('gbk')  # Chinese characters
        except UnicodeDecodeError:
            decode_str = str(c_char_p_value.value)
        return decode_str

    # # Enumerate cameras or enum devices
    def enum_devices():
        global deviceList
        global obj_cam_operation

        deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE , deviceList)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            return ret

        if deviceList.nDeviceNum == 0:
            QMessageBox.warning(mainWindow, "Info", "Find no device", QMessageBox.Ok)
            return ret
        print("Find %d devices!" % deviceList.nDeviceNum)

        devList = []
        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("\ngige device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("current ip: %d.%d.%d.%d " % (nip1, nip2, nip3, nip4))
                devList.append(
                    "[" + str(i) + "]GigE: " + user_defined_name + " " + model_name + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]USB: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")

        ui.ComboDevices.clear()
        ui.ComboDevices.addItems(devList)
        ui.ComboDevices.setCurrentIndex(0)

    
    
    def clear_detection_time():
        ui.lblDetectionTime.setText("Detection Time: 0.0 s")


    def log_status(message) :
        ui.statusBox.append(message)
    # Open Camera | open device
    def update_detection_time(duration):
        ui.lblDetectionTime.setText(f"Detection Time: {duration:.3f} s")
        print(f"Detection time: {duration:.3f} s")
        
    def open_device():
        global deviceList
        global nSelCamIndex
        global obj_cam_operation
        global isOpen
        if isOpen:
            QMessageBox.warning(mainWindow, "Error", 'Camera is Running!', QMessageBox.Ok)
            return MV_E_CALLORDER

        nSelCamIndex = ui.ComboDevices.currentIndex()
        if nSelCamIndex < 0:
            QMessageBox.warning(mainWindow, "Error", 'Please select a camera!', QMessageBox.Ok)
            return MV_E_CALLORDER

        obj_cam_operation = CameraOperation(cam, deviceList, nSelCamIndex)
        obj_cam_operation.detection_time_signal.connect(update_detection_time)
        obj_cam_operation.signal.connect(lambda pm: ui.widgetDisplay.setPixmap(pm))

        ret = obj_cam_operation.Open_device()
        if 0 != ret:
            strError = "Open device failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            isOpen = False
        else:
            # Connect worker->UI signal
            obj_cam_operation.status_changed.connect(
                lambda ok: set_ok_style(ui.btnPartStatus) if ok else set_ng_style(ui.btnPartStatus)
            )
            set_continue_mode()

            get_param()

            isOpen = True
            enable_controls()

    # Start image acquisition (start streaming) | Start grab image
    def start_grabbing():
        global isGrabbing
        ret = obj_cam_operation.Start_grabbing(ui.widgetDisplay.winId())
        if ret != 0:
            strError = "Start grabbing failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            return

        isGrabbing = True
        enable_controls()


    # Stop acquisition| Stop grab image
    def stop_grabbing():
        global isGrabbing
        ret = obj_cam_operation.Stop_grabbing()
        if ret != 0:
            QMessageBox.warning(mainWindow, "Error", "Stop grabbing failed.", QMessageBox.Ok)
            return

        isGrabbing = False
        enable_controls()




    # Close device
    def close_device():
        global isOpen
        global isGrabbing
        global obj_cam_operation

        if isOpen:
            obj_cam_operation.Close_device()
            isOpen = False

        isGrabbing = False

        enable_controls()

    def _switch_mode(setter_fn):
        global isGrabbing
        was_Grabbing = isGrabbing
        if was_Grabbing :
            stop_grabbing() #clean stop

        ret = setter_fn() #call the mode setter (camera is stopped)
        if ret == MV_OK and was_Grabbing :
            start_grabbing() #clkean restart

        return ret
    
    def set_continue_mode():
        print("Switched to Continous mode !!")
        ret = _switch_mode(lambda :obj_cam_operation.Set_trigger_mode(False))
        if ret != MV_OK:
            strError = "Set continue mode failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            ui.radioContinueMode.setChecked(True)
            ui.radioTriggerMode.setChecked(False)
            ui.bnSoftwareTrigger.setEnabled(False)
            
                
                
    
    # Set trigger command or set software trigger mode
    # def set_software_trigger_mode():

    #     ret = obj_cam_operation.Set_trigger_mode(True)
    #     if ret != 0:
    #         strError = "Set trigger mode failed ret:" + ToHexStr(ret)
    #         QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    #     else:
    #         ui.radioContinueMode.setChecked(False)
    #         ui.radioTriggerMode.setChecked(True)
    #         ui.bnSoftwareTrigger.setEnabled(isGrabbing)
    
    
    def set_software_trigger_mode():
        print("Switched to Trigger Mode!!!")
        # Switch to external hardware trigger on Line0 (rising edge, single frame per pulse)
        ret = _switch_mode(lambda:obj_cam_operation.Set_trigger_mode(True, source='Line0',
                                                activation='RisingEdge',
                                                selector='FrameBurstStart',
                                                burst_count=1))
        if ret != MV_OK:
            strError = "Set trigger mode failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            ui.radioContinueMode.setChecked(False)
            ui.radioTriggerMode.setChecked(True)
            # Hardware trigger -> you don't need Software Trigger button
            ui.bnSoftwareTrigger.setEnabled(False)


    # # Set trigger command |set trigger software
    def trigger_once():
        ret = obj_cam_operation.Trigger_once()
        if ret != 0:
            strError = "TriggerSoftware failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            

    def manual_refresh():
        import sys, os
        # Relaunch the current script with the same arguments
        os.execv(sys.executable, [sys.executable] + sys.argv)


    # Save image in BMP format
    def save_bmp():
        ret = obj_cam_operation.Save_Bmp()
        if ret != MV_OK:
            strError = "Save BMP failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
    
            print("Save image success")
    # Save image in JPG format
    def save_jpg():
        
        ret = obj_cam_operation.Save_jpg()
        if ret != MV_OK:
            strError = "Save JPG failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            print("Save image success")
            
    def is_float(str):
        try:
            float(str)
            return True
        except ValueError:
            return False

    # get parameters
    def get_param():
        ret = obj_cam_operation.Get_parameter()
        if ret != MV_OK:
            strError = "Get param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            ui.edtExposureTime.setText("{0:.2f}".format(obj_cam_operation.exposure_time))
            ui.edtGain.setText("{0:.2f}".format(obj_cam_operation.gain))
            ui.edtFrameRate.setText("{0:.2f}".format(obj_cam_operation.frame_rate))

    # set parameters
    def set_param():
        frame_rate = ui.edtFrameRate.text()
        exposure = ui.edtExposureTime.text()
        gain = ui.edtGain.text()

        if is_float(frame_rate)!=True or is_float(exposure)!=True or is_float(gain)!=True:
            strError = "Set param failed ret:" + ToHexStr(MV_E_PARAMETER)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            return MV_E_PARAMETER
        
        ret = obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
        if ret != MV_OK:
            strError = "Set param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)

        return MV_OK

    # Task selection 
    def launch_task():
        task = ui.comboTasks.currentText()
        
        
        if task == "Select Task":
            QMessageBox.information(mainWindow ,"Info","Please select a task to launch.")
            return
        
        # Absolute path to training script
        script_path = os.path.join(os.path.dirname(__file__),"yolo_trainer","main.py")
        if task == "Annotation/Augmentation" :
            # Launch annotator.py as a new process/window
            subprocess.Popen([sys.executable, "annotator.py"])
        if task == "Training" :
           subprocess.Popen([sys.executable, script_path])

        else:
            QMessageBox.information(mainWindow, "Info", f"'{task}' is a dummy option for now.")


    
    # Set the control or enable status
    def enable_controls():
        global isGrabbing
        global isOpen

        # Set the status of the group first, then set the status of each control individually

        ui.groupGrab.setEnabled(isOpen)
        ui.groupParam.setEnabled(isOpen)

        ui.bnOpen.setEnabled(not isOpen)
        ui.bnClose.setEnabled(isOpen)

        ui.bnStart.setEnabled(isOpen and (not isGrabbing))
        ui.bnStop.setEnabled(isOpen and isGrabbing)
        ui.bnSoftwareTrigger.setEnabled(isGrabbing and ui.radioTriggerMode.isChecked())

        ui.bnSaveImage.setEnabled(isOpen and isGrabbing)

    # Init app, bind ui and api
    app = QApplication(sys.argv)

    # Step 1: Apply the dark theme globally
    qdarktheme.setup_theme("dark")

    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    

    
    # class EmittingStream(QObject):
    #     text_written = pyqtSignal(str)

    #     def __init__(self, parent=None):
    #         super().__init__(parent)
    #         self._buf = ""

    #     def write(self, text):
    #         if not text:
    #             return
    #         self._buf += text
    #         # emit complete lines only (avoid partial writes)
    #         while "\n" in self._buf:
    #             line, self._buf = self._buf.split("\n", 1)
    #             if line.strip():
    #                 self.text_written.emit(line)

    #     def flush(self):
    #         if self._buf.strip():
    #             self.text_written.emit(self._buf.strip())
    #         self._buf = ""

    # # Hook stdout/stderr to the UI
    # stream = EmittingStream()
    # stream.text_written.connect(lambda s: ui.statusBox.append(s))
    # sys.stdout = stream
    # sys.stderr = stream
    # Step 2: Apply custom stylesheet for branding
    mainWindow.setStyleSheet("""
    QComboBox, QLineEdit, QTextEdit {
        background: #23272e;
        color: #fff;
        border-radius: 12px;
        border: 1.5px solid #2e8fff;
        font-size: 16px;
        font-family: 'Montserrat', 'Segoe UI', 'Arial', sans-serif;
        padding: 6px 12px;
    }
    QComboBox#ComboDevices { min-width: 320px; }
    QComboBox QAbstractItemView {
        background: #1f1f1f;
        color: #fff;
        selection-background-color: #2e8fff;
        font-size: 15px;
        border-radius: 8px;
    }
    QPushButton {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #2e8fff, stop:1 #7ee787
        );
        color: #fff;
        border-radius: 16px;
        border: none;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: 600;
    }
    QPushButton:disabled {
        background: #444;
        color: #888;
    }
    QPushButton:hover {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #7ee787, stop:1 #2e8fff
        );
        color: #222;
    }
    QGroupBox {
        border: 2px solid #2e8fff;
        border-radius: 14px;
        margin-top: 8px;
        font-size: 18px;
        font-weight: bold;
        color: #7ee787;
        background: rgba(30, 30, 30, 0.85);
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 4px 0 4px;
    }
    QLabel {
        color: #7ee787;
        font-size: 15px;
        font-weight: 500;
    }
    QStatusBar {
        background: #23272e;
        color: #7ee787;
        border-top: 1px solid #2e8fff;
    }
    """)
    
    def set_ok_style(button):
        button.setText("OK")
        button.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                font-size: 18px;
                font-weight: 700;
                background-color: #28a745;   /* green */
                color: white;
            }
        """)

    def set_ng_style(button):
        button.setText("NG")
        button.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                font-size: 18px;
                font-weight: 700;
                background-color: #dc3545;   /* red */
                color: white;
            }
        """)
    # ui.btnUploadImage.clicked.connect(upload_image)
    ui.bnEnum.clicked.connect(enum_devices)
    ui.bnOpen.clicked.connect(open_device)
    ui.bnClose.clicked.connect(close_device)
    ui.bnStart.clicked.connect(start_grabbing)
    ui.bnStop.clicked.connect(stop_grabbing)
    # ui.btnLaunchTask.clicked.connect(launch_task)
    ui.bnSoftwareTrigger.clicked.connect(trigger_once)
    ui.btnRefresh.clicked.connect(manual_refresh)
    ui.radioTriggerMode.clicked.connect(set_software_trigger_mode)
    ui.radioContinueMode.clicked.connect(set_continue_mode)

    ui.bnGetParam.clicked.connect(get_param)
    ui.bnSetParam.clicked.connect(set_param)

    ui.bnSaveImage.clicked.connect(save_bmp)
    ui.btnClearTime.clicked.connect(clear_detection_time)
    

    mainWindow.setWindowTitle("Foamatomatic")
    mainWindow.showMaximized()
    app.exec_()
    close_device()
    sys.exit()
    