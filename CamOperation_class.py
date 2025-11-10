# -- coding: utf-8 --
# Copyright (c) 2025 Abhishek Vashisth
# All Rights Reserved.
# This software is proprietary and confidential.
# Unauthorized copying, modification, or distribution is strictly prohibited.

import sys
import threading
import msvcrt
import numpy as np
import time
import sys, os
import cv2
import numpy
import datetime
import inspect
import ctypes
import random
from ctypes import *


import cv2
import torch
from ultralytics import YOLO
import requests, base64
from pymodbus.client import ModbusTcpClient


sys.path.append("../MvImport")

from MvImport.CameraParams_header import *
from MvImport.MvCameraControl_class import *
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QPixmap , QImage


# 强制关闭线程
def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


# 停止线程
def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)


# 转为16进制字符串
def To_hex_str(num):
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


# 是否是Mono图像
def Is_mono_data(enGvspPixelType):
    if PixelType_Gvsp_Mono8 == enGvspPixelType or PixelType_Gvsp_Mono10 == enGvspPixelType \
            or PixelType_Gvsp_Mono10_Packed == enGvspPixelType or PixelType_Gvsp_Mono12 == enGvspPixelType \
            or PixelType_Gvsp_Mono12_Packed == enGvspPixelType:
        return True
    else:
        return False


# 是否是彩色图像
def Is_color_data(enGvspPixelType):
    if PixelType_Gvsp_BayerGR8 == enGvspPixelType or PixelType_Gvsp_BayerRG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB8 == enGvspPixelType or PixelType_Gvsp_BayerBG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10 == enGvspPixelType or PixelType_Gvsp_BayerRG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10 == enGvspPixelType or PixelType_Gvsp_BayerBG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12 == enGvspPixelType or PixelType_Gvsp_BayerRG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12 == enGvspPixelType or PixelType_Gvsp_BayerBG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_YUV422_Packed == enGvspPixelType or PixelType_Gvsp_YUV422_YUYV_Packed == enGvspPixelType:
        return True
    else:
        return False


# Mono图像转为python数组
# def Mono_numpy(data, nWidth, nHeight):
#     data_ = np.frombuffer(data, count=int(nWidth * nHeight), dtype=np.uint8, offset=0)
#     data_mono_arr = data_.reshape(nHeight, nWidth)
#     numArray = np.zeros([nHeight, nWidth, 1], "uint8")
#     numArray[:, :, 0] = data_mono_arr
#     return numArray

def Mono_numpy(data, nWidth, nHeight):
    expected_size = nWidth * nHeight
    actual_size = len(data)

    if actual_size < expected_size:
        print(f"[ERROR] Mono frame too small: Expected {expected_size}, got {actual_size}")
        return None

    data_mono = np.frombuffer(data, count=expected_size, dtype=np.uint8)
    return data_mono.reshape((nHeight, nWidth))



# 彩色图像转为python数组
# def Color_numpy(data, nWidth, nHeight):
#     data_ = np.frombuffer(data, count=int(nWidth * nHeight * 3), dtype=np.uint8, offset=0)
#     data_r = data_[0:nWidth * nHeight * 3:3]
#     data_g = data_[1:nWidth * nHeight * 3:3]
#     data_b = data_[2:nWidth * nHeight * 3:3]

#     data_r_arr = data_r.reshape(nHeight, nWidth)
#     data_g_arr = data_g.reshape(nHeight, nWidth)
#     data_b_arr = data_b.reshape(nHeight, nWidth)
#     numArray = np.zeros([nHeight, nWidth, 3], "uint8")

#     numArray[:, :, 0] = data_r_arr
#     numArray[:, :, 1] = data_g_arr
#     numArray[:, :, 2] = data_b_arr
#     return numArray

def Color_numpy(data, nWidth, nHeight):
    expected_size = nWidth * nHeight * 3
    actual_size = len(data)

    if actual_size < expected_size:
        print(f"[ERROR] Frame too small: Expected {expected_size}, got {actual_size}")
        return None  # or raise an exception

    data_ = np.frombuffer(data, count=expected_size, dtype=np.uint8)
    data_r = data_[0::3]
    data_g = data_[1::3]
    data_b = data_[2::3]

    data_r_arr = data_r.reshape(nHeight, nWidth)
    data_g_arr = data_g.reshape(nHeight, nWidth)
    data_b_arr = data_b.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 3], "uint8")

    numArray[:, :, 0] = data_r_arr
    numArray[:, :, 1] = data_g_arr
    numArray[:, :, 2] = data_b_arr
    return numArray



# 相机操作类
class CameraOperation(QObject):
    status_changed = pyqtSignal(bool)   # <— emits True for OK, False for NG
    signal = pyqtSignal(QPixmap)
    detection_time_signal = pyqtSignal(float) #emit detection time in seconds

    #region INIT
    def __init__(self, obj_cam, st_device_list, n_connect_num=0, b_open_device=False, b_start_grabbing=False,
                 h_thread_handle=None,
                 b_thread_closed=False, st_frame_info=None, b_exit=False, b_save_bmp=False, b_save_jpg=False,
                 buf_save_image=None,
                 n_save_image_size=0, n_win_gui_id=0, frame_rate=0, exposure_time=0, gain=0):
        super().__init__()

        self.obj_cam = obj_cam
        self.st_device_list = st_device_list
        self.n_connect_num = n_connect_num
        self.b_open_device = b_open_device
        self.b_start_grabbing = b_start_grabbing
        self.b_thread_closed = b_thread_closed
        self.st_frame_info = st_frame_info
        self.b_exit = b_exit
        self.b_save_bmp = b_save_bmp
        self.b_save_jpg = b_save_jpg
        self.buf_save_image = buf_save_image
        self.n_save_image_size = n_save_image_size
        self.h_thread_handle = h_thread_handle
        self.b_thread_closed
        self.frame_rate = frame_rate
        self.exposure_time = exposure_time
        self.gain = gain
        
        self.yolo_model = None
        self.yolo_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.buf_bgr = None
        self.buf_bgr_size = 0

        self.telemetry_host = 'http://localhost:8080' #serverthingsboard
        self.access_token = 'XAtrODB3qAVbo4nGxPET' 
        self.last_sent_names = set() #debounce telemety on changes
    
        
        self.reject_lock = threading.Lock()
        self.last_reject_ts = 0
        self.reject_cooldown_us =150 #tune for converyor speed
        
        
        # self.on_status_change = None     # UI callback (set by main)
        self._last_ok_flag = None        # for change detection (debounce)
        self.is_trigger_mode = False

        self.buf_lock = threading.Lock()  # 取图和存图的buffer锁

    # 打开相机
    # def Open_device(self):
    #     if not self.b_open_device:
    #         if self.n_connect_num < 0:
    #             return MV_E_CALLORDER

    #         # ch:选择设备并创建句柄 | en:Select device and create handle
    #         nConnectionNum = int(self.n_connect_num)
    #         stDeviceList = cast(self.st_device_list.pDeviceInfo[int(nConnectionNum)],
    #                             POINTER(MV_CC_DEVICE_INFO)).contents
    #         self.obj_cam = MvCamera()
    #         ret = self.obj_cam.MV_CC_CreateHandle(stDeviceList)
    #         if ret != 0:
    #             self.obj_cam.MV_CC_DestroyHandle()
    #             return ret

    #         ret = self.obj_cam.MV_CC_OpenDevice()
    #         # ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_RGB8_Packed)
    #         # if ret != 0:
    #         #     print(f"[ERROR] Failed to set PixelFormat to RGB8Packed. ret = {To_hex_str(ret)}")
    #         # else:
    #         #     print("PixelFormat set to RGB8Packed successfully.")
    #         ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_Mono8)
    #         if ret == 0:
    #             print("Set to Mono8 successfully")
    #             self.pixel_format = PixelType_Gvsp_Mono8
    #         else:
    #             # If Mono8 fails, try Bayer format
    #             print("Failed to set Mono8, trying BayerRG8...")
    #             ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_BayerRG8)
    #             if ret == 0:
    #                 print("Set to BayerRG8 successfully")
    #                 self.pixel_format = PixelType_Gvsp_BayerRG8
    #             else:
    #                 print("Failed to set pixel format")
    #                 return ret
    #         print("open device successfully!")
    #         self.b_open_device = True
    #         self.b_thread_closed = False

    #         # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
    #         if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
    #             nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
    #             if int(nPacketSize) > 0:
    #                 ret = self.obj_cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
    #                 if ret != 0:
    #                     print("warning: set packet size fail! ret[0x%x]" % ret)
    #             else:
    #                 print("warning: set packet size fail! ret[0x%x]" % nPacketSize)

    #         stBool = c_bool(False)
    #         ret = self.obj_cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
    #         if ret != 0:
    #             print("get acquisition frame rate enable fail! ret[0x%x]" % ret)

    #         # ch:设置触发模式为off | en:Set trigger mode as off
    #         ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    #         if ret != 0:
    #             print("set trigger mode fail! ret[0x%x]" % ret)
                
    #             # --- YOLO: load once ---
    #         try:
    #             # change to your weights path
    #             self.yolo_model = YOLO("segment.pt")
    #             self.yolo_model.to(self.yolo_device)
    #             print(f"YOLO loaded on {self.yolo_device}")
    #         except Exception as e:
    #             print("YOLO load failed:", e)
    #             self.yolo_model = None
    #         return MV_OK
    
    #region Open device
    # real live view color frames occur in this open_device  
    def Open_device(self):
        if not self.b_open_device:
            if self.n_connect_num < 0:
                return MV_E_CALLORDER

            # Select device and create handle
            nConnectionNum = int(self.n_connect_num)
            stDeviceList = cast(self.st_device_list.pDeviceInfo[int(nConnectionNum)],
                                POINTER(MV_CC_DEVICE_INFO)).contents
            self.obj_cam = MvCamera()
            ret = self.obj_cam.MV_CC_CreateHandle(stDeviceList)
            if ret != 0:
                self.obj_cam.MV_CC_DestroyHandle()
                return ret

            ret = self.obj_cam.MV_CC_OpenDevice()
            if ret != 0:
                return ret
            print("open device successfully!")
            self.b_open_device = True
            self.b_thread_closed = False

            # If GigE, set packet size
            if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.obj_cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                    if ret != 0:
                        print("warning: set packet size fail! ret[0x%x]" % ret)
                else:
                    print("warning: set packet size fail! ret[0x%x]" % nPacketSize)

            # Trigger mode off
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print("set trigger mode fail! ret[0x%x]" % ret)

            # ---- PixelFormat: prefer COLOR ----
            ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_RGB8_Packed)
            if ret == 0:
                print("PixelFormat set to RGB8_Packed ✅")
                self.pixel_format = PixelType_Gvsp_RGB8_Packed
            else:
                print("RGB8_Packed not supported, trying BayerRG8...")
                ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_BayerRG8)
                if ret == 0:
                    print("PixelFormat set to BayerRG8 ✅")
                    self.pixel_format = PixelType_Gvsp_BayerRG8
                else:
                    print("Trying BayerBG8...")
                    ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_BayerBG8)
                    if ret == 0:
                        print("PixelFormat set to BayerBG8 ✅")
                        self.pixel_format = PixelType_Gvsp_BayerBG8
                    else:
                        print("⚠️ Fallback: Mono8 (grayscale only).")
                        ret = self.obj_cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_Mono8)
                        if ret != 0:
                            print(f"Set PixelFormat failed, ret=0x{ret:x}")
                            return ret
                        self.pixel_format = PixelType_Gvsp_Mono8

            # Try to enable auto white balance (on color cams)
            try:
                self.obj_cam.MV_CC_SetEnumValue("BalanceWhiteAuto", 2)  # 2=Continuous
                print("Auto white balance enabled")
            except:
                pass
            
            #region YOLO_MODEL
            # ---- YOLO load once ----       
            try:                                  
                                                           
                # self.yolo_model = YOLO("C:\\Users\\manoj\\Downloads\\FIT\\duro_bng\\runs\\detect\\foam_single_3\\weights\\best.pt")                                              
                # self.yolo_model = YOLO(r"C:\Users\manoj\Downloads\FIT\model\duroflex_seg.pt")                                              
                # self.yolo_model = YOLO(r"C:\Users\manoj\OneDrive\Desktop\HIS\main\runs\detect\fridge-doors-v13\weights\best.pt")                                              
                self.yolo_model = YOLO(r"C:\Users\manoj\OneDrive\Desktop\HIS\main\runs\detect\train16\weights\best.pt")                                              
                # self.yolo_model = YOLO(r"C:\Users\manoj\Downloads\FIT\model\duroflex_detect.pt")                                              
                self.yolo_model.to(self.yolo_device)
                print(self.yolo_device)
                print(f"YOLO loaded on {self.yolo_device}")
                
            except Exception as e:
                print(f"YOLO load failed : {e}")
                self.yolo_model = None
            
            self.configure_reject_output(line_index=1,pulse_us=30_000,invert=False)

            return MV_OK


    #region Start_grabbing 
    def Start_grabbing(self, winHandle):
        if not self.b_start_grabbing and self.b_open_device:
            self.b_exit = False
            ret = self.obj_cam.MV_CC_StartGrabbing()
            if ret != 0:
                return ret
            self.b_start_grabbing = True
            print("start grabbing successfully!")
            try:
                thread_id = random.randint(1, 10000)
                self.h_thread_handle = threading.Thread(target=CameraOperation.Work_thread, args=(self, winHandle),daemon=True)
                self.h_thread_handle.start()
                self.b_thread_closed = True
            finally:
                pass
            return MV_OK

        return MV_E_CALLORDER

    
    def get_expected_size(self,pixel_type, width, height):
        """
        Returns the expected byte size of an image frame based on pixel format.
        """
        if pixel_type == PixelType_Gvsp_Mono8 or pixel_type == PixelType_Gvsp_BayerRG8:
            return width * height  # 1 byte per pixel
        elif pixel_type == PixelType_Gvsp_RGB8_Packed or pixel_type == PixelType_Gvsp_YUV422_Packed:
            return width * height * 3  # 3 bytes per pixel (RGB)
        elif pixel_type == PixelType_Gvsp_YUV422_YUYV_Packed:
            return width * height * 2  # 2 bytes per pixel
        elif pixel_type == PixelType_Gvsp_Mono10 or pixel_type == PixelType_Gvsp_Mono12:
            return width * height * 2  # 10/12-bit raw = 2 bytes each
        elif pixel_type in (
            PixelType_Gvsp_Mono10_Packed,
            PixelType_Gvsp_Mono12_Packed,
            PixelType_Gvsp_BayerGR10_Packed,
            PixelType_Gvsp_BayerRG10_Packed,
            PixelType_Gvsp_BayerGB10_Packed,
            PixelType_Gvsp_BayerBG10_Packed,
            PixelType_Gvsp_BayerGR12_Packed,
            PixelType_Gvsp_BayerRG12_Packed,
            PixelType_Gvsp_BayerGB12_Packed,
            PixelType_Gvsp_BayerBG12_Packed,
        ):
            return int(width * height * 1.5)  # Packed formats ~12 bits per pixel
        else:
            print(f"[WARNING] Unknown pixel type: {hex(pixel_type)}. Assuming 3 bytes per pixel.")
            return width * height * 3  # Default fallback
        
        
    def Get_frame(self):
        """Returns the latest frame as a NumPy BGR image for inference."""
        if not self.buf_save_image or not self.st_frame_info:
            return None

        self.buf_lock.acquire()
        try:
            width = self.st_frame_info.nWidth
            height = self.st_frame_info.nHeight
            pixel_type = self.st_frame_info.enPixelType
            frame_len = self.st_frame_info.nFrameLen
            data = bytes(bytearray(self.buf_save_image[:frame_len]))

            # if Is_mono_data(pixel_type):
            #     image = Mono_numpy(data, width, height)
            #     image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            #     image = cv2.cvtColor(image , cv2.COLOR_BAYER_BGGR2RGB)
            # elif Is_color_data(pixel_type):
            #     image = Color_numpy(data, width, height)
            # else:
            #     print("Unsupported pixel format:", hex(pixel_type))
            #     return None
            if pixel_type == PixelType_Gvsp_Mono8:
        # Mono image
                image = Mono_numpy(data, width, height)
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif pixel_type == PixelType_Gvsp_BayerRG8:
                # Bayer image
                mono_image = Mono_numpy(data, width, height)
                if mono_image is None :
                    return None
                image = cv2.cvtColor(mono_image, cv2.COLOR_BayerRG2BGR)
            else:
                print(f"Unsupported pixel format: {hex(pixel_type)}")
                image = None    
                return None

        finally:
            self.buf_lock.release()
            if pixel_type == PixelType_Gvsp_Mono8 or pixel_type == PixelType_Gvsp_BayerRG8:
                expected_size = width * height
            else:
                expected_size = width * height * 3

            expected_size = self.get_expected_size(pixel_type, width, height)
            print(f"Pixel Type: {hex(pixel_type)} Size: {frame_len} Expected: {expected_size}")
            return image
    
    #region Stop_grabbing
    def Stop_grabbing(self):
        if self.b_start_grabbing and self.b_open_device:
             # signal thread to exit adn join it 
            self.b_exit = True
            self.obj_cam.MV_CC_StopGrabbing()
            
            if self.h_thread_handle is not None :
                self.h_thread_handle.join(timeout=2.0)
                self.h_thread_handle = None
            # ret =  self.obj_cam.MV_CC_StopGrabbing()
            # if ret!=0 :
                # return ret
            print("Stop Grabbing successfuly !!")
            self.b_start_grabbing = False
            return MV_OK
        return MV_E_CALLORDER
        # if self.b_thread_closed:
        #         Stop_thread(self.h_thread_handle)
        #         self.b_thread_closed = False
        #     ret = self.obj_cam.MV_CC_StopGrabbing()
        #     if ret != 0:
        #         return ret
        #     print("stop grabbing successfully!")
        #     self.b_start_grabbing = False
        #     self.b_exit = True
        #     return MV_OK
        # else:
        #     return MV_E_CALLORDER

    # 关闭相机
    def Close_device(self):
        if self.b_open_device:
            # 退出线程
            
            # stop/exit thread cleanly
            self.b_exit = True
            if self.h_thread_handle is not None:
                self.h_thread_handle.join(timeout=2.0)
                self.h_thread_handle = None
            ret = self.obj_cam.MV_CC_CloseDevice()
            if ret != 0:
                return ret
            # if self.b_thread_closed:
            #     Stop_thread(self.h_thread_handle)
            #     self.b_thread_closed = False
            # ret = self.obj_cam.MV_CC_CloseDevice()
            # if ret != 0:
            #     return ret

        # ch:销毁句柄 | Destroy handle
        self.obj_cam.MV_CC_DestroyHandle()
        self.b_open_device = False
        self.b_start_grabbing = False
        self.b_exit = True
        print("close device successfully!")

        return MV_OK

    # 设置触发模式
    # def Set_trigger_mode(self, is_trigger_mode):
    #     if not self.b_open_device:
    #         return MV_E_CALLORDER

    #     if not is_trigger_mode:
    #         ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", 0)
    #         if ret != 0:
    #             return ret
    #     else:
    #         ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", 1)
    #         if ret != 0:
    #             return ret
    #         ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource", 7)
    #         if ret != 0:
    #             return ret

    #     return MV_OK
    
    
    #region Software_trigger
    def Set_trigger_mode(self, enable, source='software',
                     activation='RisingEdge',
                     selector='FrameBurstStart',
                     burst_count=1):
        """
        enable=True  -> trigger ON
        source='line0' or 'software'
        activation='RisingEdge' | 'FallingEdge' | 'AnyEdge'
        selector='FrameBurstStart' (preferred) falls back to 'FrameStart'
        burst_count=1 -> one frame per pulse
        """
        if not self.b_open_device:
            print("[MODE] camera not open; cannot change trigger mode")
            return MV_E_CALLORDER

        try:
            if not enable:
                # ---- CONTINUOUS (free-run) ----
                print("[MODE] switching to CONTINUOUS mode")
                try:
                    # keep acquisition continuous when trigger is off
                    self.obj_cam.MV_CC_SetEnumValueByString("AcquisitionMode", "Continuous")
                except Exception:
                    pass

                ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
                if ret != 0:
                    print(f"[MODE] set continuous fail: 0x{ret:x}")
                    return ret

                self.is_trigger_mode = False
                print("[MODE] now in CONTINUOUS mode")
                return MV_OK

            # ---- TRIGGERED ACQUISITION ----
            src_lower = (source or "software").lower()
            print(f"[MODE] switching to TRIGGER mode "
                f"(src={src_lower}, activation={activation}, selector={selector}, burst={burst_count})")

            # Make sure we are in continuous acquisition (most MVS cams expect this for trigger)
            try:
                self.obj_cam.MV_CC_SetEnumValueByString("AcquisitionMode", "Continuous")
            except Exception:
                pass

            # Choose selector (FrameBurstStart preferred; fallback to FrameStart)
            ok_selector = False
            for sel in (selector, "FrameStart"):
                try:
                    self.obj_cam.MV_CC_SetEnumValueByString("TriggerSelector", sel)
                    ok_selector = True
                    selector = sel  # record the actual used selector
                    break
                except Exception:
                    continue
            if not ok_selector:
                # ignore if not supported on your model
                pass

            # If using burst, set count
            if selector == "FrameBurstStart":
                try:
                    self.obj_cam.MV_CC_SetIntValue("AcquisitionBurstFrameCount", int(burst_count))
                except Exception:
                    pass

            # Turn trigger ON
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_ON)
            if ret != 0:
                print(f"[MODE] set trigger mode fail: 0x{ret:x}")
                return ret

            # Trigger source: hardware Line0 or Software
            try:
                if src_lower in ("line0", "hardware", "ext", "external"):
                    self.obj_cam.MV_CC_SetEnumValueByString("TriggerSource", "Line0")
                else:
                    self.obj_cam.MV_CC_SetEnumValueByString("TriggerSource", "Software")
            except Exception:
                # Fallback numeric (common mapping on Hikrobot: Line0=0, Software=7)
                self.obj_cam.MV_CC_SetEnumValue("TriggerSource",
                                                0 if src_lower in ("line0", "hardware", "ext", "external") else 7)

            # Edge activation
            try:
                self.obj_cam.MV_CC_SetEnumValueByString("TriggerActivation", activation)
            except Exception:
                act_map = {"risingedge": 0, "fallingedge": 1, "anyedge": 2}
                self.obj_cam.MV_CC_SetEnumValue("TriggerActivation", act_map.get(activation.lower(), 0))

            # Make exposure deterministic in trigger mode
            try:
                self.obj_cam.MV_CC_SetEnumValueByString("ExposureMode", "Timed")
                self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 0)  # Off
            except Exception:
                pass

            self.is_trigger_mode = True
            print(f"[MODE] now in TRIGGER mode "
                f"(src={'Line0' if src_lower in ('line0','hardware','ext','external') else 'Software'}, "
                f"activation={activation}, selector={selector}, burst={burst_count})")
            return MV_OK

        except Exception as e:
            print(f"[Trigger] config error: {e}")
            return MV_E_PARAMETER


    # 软触发一次
    def Trigger_once(self):
        if self.b_open_device:
            return self.obj_cam.MV_CC_SetCommandValue("TriggerSoftware")
    
    

    # 获取参数
    def Get_parameter(self):
        if self.b_open_device:
            stFloatParam_FrameRate = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
            stFloatParam_exposureTime = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_exposureTime), 0, sizeof(MVCC_FLOATVALUE))
            stFloatParam_gain = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_gain), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatParam_FrameRate)
            if ret != 0:
                return ret
            self.frame_rate = stFloatParam_FrameRate.fCurValue

            ret = self.obj_cam.MV_CC_GetFloatValue("ExposureTime", stFloatParam_exposureTime)
            if ret != 0:
                return ret
            self.exposure_time = stFloatParam_exposureTime.fCurValue

            ret = self.obj_cam.MV_CC_GetFloatValue("Gain", stFloatParam_gain)
            if ret != 0:
                return ret
            self.gain = stFloatParam_gain.fCurValue

            return MV_OK

    # 设置参数
    def Set_parameter(self, frameRate, exposureTime, gain):
        if '' == frameRate or '' == exposureTime or '' == gain:
            print('show info', 'please type in the text box !')
            return MV_E_PARAMETER
        if self.b_open_device:
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 0)
            time.sleep(0.2)
            ret = self.obj_cam.MV_CC_SetFloatValue("ExposureTime", float(exposureTime))
            if ret != 0:
                print('show error', 'set exposure time fail! ret = ' + To_hex_str(ret))
                return ret

            ret = self.obj_cam.MV_CC_SetFloatValue("Gain", float(gain))
            if ret != 0:
                print('show error', 'set gain fail! ret = ' + To_hex_str(ret))
                return ret

            ret = self.obj_cam.MV_CC_SetFloatValue("AcquisitionFrameRate", float(frameRate))
            if ret != 0:
                print('show error', 'set acquistion frame rate fail! ret = ' + To_hex_str(ret))
                return ret

            print('show info', 'set parameter success!')

            return MV_OK

    
    #region MODBUS READ
    def read_modbus_data(self):
        """Read width/depth/length/status from PLC. Returns {} on failure."""
        try:
            client = ModbusTcpClient('192.168.1.1', port=502,timeout=1)
            if not client.connect():
                print("[Modbus] connect failed")
                return {}
            width  = round(client.read_holding_registers(address=204, count=1).registers[0] / 25.4, 1)
            depth  = round(client.read_holding_registers(address=208, count=1).registers[0] / 25.4, 1)
            length = round(client.read_holding_registers(address=200, count=1).registers[0] / 25.4, 1)
            status_reg = client.read_holding_registers(address=216, count=1).registers[0]
            # client.close()
            return {
                'width': width,
                'depth': depth,
                'length': length,
                'status': 'Running' if status_reg == 1 else 'Stopped'
            } 
        except Exception as e:
            print(f"[Modbus] error: {e}")
            return {}
        finally :
            try:
                client.close()
            except Exception as e:
                pass
        
    #region Telemetry
    def _post_telemetry(self, detected_names, jpg_bytes=None):
        """Runs in a background thread to avoid blocking the grab loop."""
        current = set(detected_names)
        # # Only send if changed
        # if current == self.last_sent_names:
        #     return
        
        # In Trigger Mode ,send on every trigger (no debounce).
        # In continuos mode , keep the old debounce
        if (not self.is_trigger_mode) and (current == self.last_sent_names) :
            return

        modbus = self.read_modbus_data()
        if modbus :
        #     depth = modbus.get('depth',None)
            if 'PROPEL' in current :
                current.remove('PROPEL') #Remove "Propel"
                current.add('PROP') # Add 'PROPPL'
            elif 'BOLT' in current :
                current.remove('BOLT')
                current.add('BOL')
            
        # Only send if changed 
        if (not self.is_trigger_mode) and (current == self.last_sent_names) :
            return 

        if not modbus or modbus.get('status') != 'Running':
            print("[Telemetry] Modbus not Running/available; will retry on next change.")
            return

        obj = next(iter(current)) if current else 'None'
        payload = {'object': obj, **modbus}
        tel_url = f"{self.telemetry_host}/api/v1/{self.access_token}/telemetry"
        headers = {'Content-Type': 'application/json'}
        try:
            r = requests.post(tel_url, json=payload, headers=headers, timeout=5)
            if r.ok:
                print("[Telemetry] telemetry sent")
                # self.last_sent_names = current
                # Only update debounce state in continuos mode
                if not self.is_trigger_mode :
                    self.last_sent_names = current
                    
                # optional: send snapshot attribute
                if jpg_bytes:
                    img_b64 = base64.b64encode(jpg_bytes).decode('utf-8')
                    attr_url = f"{self.telemetry_host}/api/v1/{self.access_token}/attributes?scope=CLIENT_SCOPE&key=snapshot"
                    r2 = requests.post(attr_url, json={"Image": img_b64}, timeout=5)
                    if r2.ok:
                        print("[Telemetry] image attribute sent")
                    else:
                        print(f"[Telemetry] attr err: {r2.status_code} {r2.text}")
                        print(f"OK STATUS FOR TELEMETRY !! ")
            else:
                print(f"[Telemetry] http err: {r.status_code} {r.text}")
        except Exception as e:
            print(f"[Telemetry] exception: {e}")
            
    def send_detection(self, detected_names, frame_bgr=None):
        """Public, non-blocking: spawns a thread that posts telemetry + optional snapshot."""
        # Optional snapshot as JPEG (only when we have a frame and change)
        jpg_bytes = None
        if frame_bgr is not None:
            try:
                ok, buf = cv2.imencode('.jpg', frame_bgr)
                if ok:
                    jpg_bytes = buf.tobytes()
            except Exception:
                pass
        t = threading.Thread(target=self._post_telemetry, args=(detected_names, jpg_bytes), daemon=True)
        t.start()
        
    
    #region O/P Trigger 
    def configure_reject_output(self,line_index=1,pulse_us=30_000,invert=False):
        pass
    #     """
    #     Prepare a camera digital output line for software pulses.
    #     works with Hikrobot MVS-Style nodes.
    #     - line_index : 1 or 2
    #     - pulse_us : pulse width in microseconds(camera must support these nodes)
        
    #     """
    #     if not self.b_open_device:
    #         return MV_E_CALLORDER
        
    #     # Select the physical line 
    #     ret = self.obj_cam.MV_CC_SetEnumValue("LineSelector",line_index)
    #     if ret!=0:
    #         print(f"[I/O] LineSelector({line_index}) fail : 0x{ret:x}")
    #         return ret
        
    #     # Put the line in output/strobe mode (value 8 was used in single_reject1)
    #     #  Some models use "LineMode" (0=Input, 8=Strobe/Output).
    #     ret = self.obj_cam.MV_CC_SetEnumValue("LineMode",8)
    #     if ret!=0 :
    #         print(f"[I/O] LineMode(Output) fail : 0x{ret:x}")
            
    #      # Optional: invert polarity
    #     try:
    #         self.obj_cam.MV_CC_SetBoolValue("LineInverter", bool(invert))
    #     except Exception:
    #         pass

    #     # Optional: set pulse width (microseconds) if supported
    #     # On many cams this is "StrobePulseWidth" or "LinePulseWidth".
    #     for node in ("StrobePulseWidth", "LinePulseWidth"):
    #         try:
    #             self.obj_cam.MV_CC_SetIntValue(node, int(pulse_us))
    #             break
    #         except Exception:
    #             continue

    #     # Some cameras require enabling strobes
    #     for node in ("StrobeEnable", "LineStrobeEnable"):
    #         try:
    #             self.obj_cam.MV_CC_SetBoolValue(node, True)
    #             break
    #         except Exception:
    #             continue
            
    #     print(f"[I/O] Line {line_index} configured for output pulse (~{pulse_us}) us")
    #     return MV_OK 
    
    
    def Reject_pulse_line_trigger(self, line_index=1):
        pass
    #     """Pulse the configured LineX via LineTriggerSoftware."""
    #     if not self.b_open_device:
    #         return MV_E_CALLORDER
    #     ret = self.obj_cam.MV_CC_SetEnumValue("LineSelector", line_index)
    #     if ret != 0:
    #         print(f"[I/O] LineSelector({line_index}) fail: 0x{ret:x}")
    #         return ret
    #     ret = self.obj_cam.MV_CC_SetCommandValue("LineTriggerSoftware")
    #     if ret != 0:
    #         print(f"[I/O] LineTriggerSoftware fail: 0x{ret:x}")
    #         return ret
    #     print(f"[I/O] Reject pulse fired on Line {line_index}")
    #     return MV_OK
    
    def Reject_once_debounced(self, line_index=1):
        pass
    #     now = time.time() * 1000
    #     with self._reject_lock:
    #         if now - self._last_reject_ts < self._reject_cooldown_ms:
    #             return
    #         # Try LineTriggerSoftware first
    #         ret = self.Reject_pulse_line_trigger(line_index=line_index)
    #         if ret != 0:
    #             # fallback to user output #0
    #             self.Reject_pulse_user_output(user_index=0, on_ms=30)
    #         self._last_reject_ts = now
    
 


    # region Work Thread
    def Work_thread(self, winHandle):
        import cv2
        from ultralytics.utils.plotting import Annotator, colors  # for thick boxes + labels

        stOutFrame = MV_FRAME_OUT()
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))

        while True:
            ret = self.obj_cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
            if ret == 0:
                # copy image bytes to our persistent buffer
                if self.buf_save_image is None:
                    self.buf_save_image = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
                self.st_frame_info = stOutFrame.stFrameInfo
                
                # trigger reception notification
                if self.is_trigger_mode:
                    try:
                        fn = self.st_frame_info.nFrameNum
                    except Exception:
                        fn = -1
                    print(f"[TRIGGER] external trigger frame received (FrameNum={fn})")

                self.buf_lock.acquire()
                cdll.msvcrt.memcpy(byref(self.buf_save_image), stOutFrame.pBufAddr, self.st_frame_info.nFrameLen)
                self.buf_lock.release()

                # release SDK buffer asap
                self.obj_cam.MV_CC_FreeImageBuffer(stOutFrame)
            else:
                # continue
                if self.b_exit :
                    break
                continue
            
            # BEFORE conversion
            t0 = time.perf_counter()
            # ---- Convert to BGR8 -> YOLO -> draw thick boxes -> display ----
            w = self.st_frame_info.nWidth
            h = self.st_frame_info.nHeight
            need_size = w * h * 3
            if (self.buf_bgr is None) or (self.buf_bgr_size != need_size):
                self.buf_bgr = (c_ubyte * need_size)()
                self.buf_bgr_size = need_size

            # Convert ANY incoming pixel format to BGR8
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = w
            stConvertParam.nHeight = h
            stConvertParam.pSrcData = cast(self.buf_save_image, POINTER(c_ubyte))
            stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
            stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType
            stConvertParam.enDstPixelType = PixelType_Gvsp_BGR8_Packed
            stConvertParam.pDstBuffer = cast(self.buf_bgr, POINTER(c_ubyte))
            stConvertParam.nDstBufferSize = self.buf_bgr_size

            ret_conv = self.obj_cam.MV_CC_ConvertPixelType(stConvertParam)
            if ret_conv != 0:
                # fallback to raw display if conversion fails
                stDisplayParam = MV_DISPLAY_FRAME_INFO()
                memset(byref(stDisplayParam), 0, sizeof(stDisplayParam))
                stDisplayParam.hWnd = int(winHandle)
                stDisplayParam.nWidth = w
                stDisplayParam.nHeight = h
                stDisplayParam.enPixelType = self.st_frame_info.enPixelType
                stDisplayParam.pData = self.buf_save_image
                stDisplayParam.nDataLen = self.st_frame_info.nFrameLen
                self.obj_cam.MV_CC_DisplayOneFrame(stDisplayParam)
            else:
                # Wrap BGR buffer as NumPy view (no copy)
                np_bgr = np.ctypeslib.as_array(self.buf_bgr, shape=(self.buf_bgr_size,))
                np_bgr = np_bgr.reshape(h, w, 3)
                t1 = time.perf_counter()  # after BGR8 conversion (preprocess done)
                
                # Run YOLO and draw with thick lines + class id + name
                if self.yolo_model is not None:
                    try:
                        start_time = time.time()
                        results = self.yolo_model.predict(
                            source=np_bgr,
                            verbose=False,
                            conf=0.70,
                            device=self.yolo_device,
                            imgsz=640
                        )
                        t2 = time.perf_counter() #after inference
                        detection_duration = time.time() - start_time
                        
                        # emit detection time signal to UI
                        self.detection_time_signal.emit(detection_duration)
                        
                        # print speeds (prefer perf_counter for ms)
                        if self.is_trigger_mode:
                            pre_ms  = (t1 - t0) * 1000.0
                            infer_ms = (t2 - t1) * 1000.0
                            tot_ms = (t2 - t0) * 1000.0
                            print(f"[SPEED] preprocess: {pre_ms:.1f} ms | inference: {infer_ms:.1f} ms | total: {tot_ms:.1f} ms")
                                                
                        
                        r = results[0]
                        names = r.names  # dict or list of class names

                        # line width scales with image size (nice & chunky)
                        lw = max(2, round(min(h, w) / 200))
                        annotator = Annotator(np_bgr, line_width=lw, example=str(names))
                        detected_names = set()

                        if r.boxes is not None and len(r.boxes) > 0:
                            for b in r.boxes:
                                x1, y1, x2, y2 = map(float, b.xyxy[0].tolist())
                                cls_id = int(b.cls[0])
                                conf = float(b.conf[0]) if getattr(b, "conf", None) is not None else 1.0
                                name = names[cls_id] if isinstance(names, (list, tuple)) else names.get(cls_id, str(cls_id))
                                
                                #----Reject Unknown or low-confidence detections ---
                                CONF_THRESHOLD = 0.30
                                KNOWN_CLASSES = set(names.values())
                                if conf < CONF_THRESHOLD or name not in KNOWN_CLASSES :
                                    print(f"[INFO] Unknown or low-confidence detection ({conf:.2f}) ")
                                    name = "None"                                
                                
                                
                                label = f"{name} ({cls_id}) {conf:.2f}"

                                # Print to terminal
                                print(f"Detected: {label}")
                                
                                detected_names.add(name)  # collecting unique name
                                # Thick colored box + label
                                if name != "None":
                                    annotator.box_label([x1, y1, x2, y2], label, color=colors(cls_id, bgr=True))

                        # annotator writes directly into np_bgr (same buffer we display)
                        _ = annotator.result()
                        # after you built detected_names_set (unique names in this frame)
                        is_ok = len(detected_names) > 0
                        

                                # Call UI callback only on change (debounce)
                        if self._last_ok_flag is None or self._last_ok_flag != is_ok:
                            self._last_ok_flag = is_ok                                    
                            self.status_changed.emit(is_ok)
                            
                            #region fire trigger
                            # fire reject on transition to NG
                            # if not is_ok:
                            #     # choose which line to use 
                            #     self.Reject_once_debounced(line_index=1)
                                
                                
                        self.send_detection(sorted(detected_names),frame_bgr=np_bgr)

                    except Exception as e:
                        print("YOLO error:", e)
                        
                rgb = cv2.cvtColor(np_bgr, cv2.COLOR_BGR2RGB)
                qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888).copy()  # .copy() to own the memory
                self.signal.emit(QPixmap.fromImage(qimg))

                # # Display annotated BGR8
                # stDisplayParam = MV_DISPLAY_FRAME_INFO()
                # memset(byref(stDisplayParam), 0, sizeof(stDisplayParam))
                # stDisplayParam.hWnd = int(winHandle)
                # stDisplayParam.nWidth = w
                # stDisplayParam.nHeight = h
                # stDisplayParam.enPixelType = PixelType_Gvsp_BGR8_Packed
                # stDisplayParam.pData = self.buf_bgr
                # stDisplayParam.nDataLen = self.buf_bgr_size
                # self.obj_cam.MV_CC_DisplayOneFrame(stDisplayParam)

            # Exit handling
            if self.b_exit:
                if self.buf_save_image is not None:
                    del self.buf_save_image
                break


        # Save JPG image
    # def Save_jpg(self):

    #     if not self.buf_save_image:
    #         return MV_E_PARAMETER 

    #     # Acquire buffer lock
    #     self.buf_lock.acquire()
    #     try :
            
    #         print(f"Image Path: {file_path}")
    #         file_path = f"{self.st_frame_info.nFrameNum}.jpg"
    #         if not file_path.isascii() :
    #             return MV_E_PARAMETER # File name must be ascii 
    #         # c_file_path = file_path.encode('ascii')
    #         # stSaveParam = MV_SAVE_IMAGE_PARAM_EX()
    #         stSaveParam = MV_SAVE_IMG_TO_FILE_PARAM()
    #         print(f"PixelType: {hex(stSaveParam.enPixelType)}")
    #         stSaveParam.enPixelType = self.st_frame_info.enPixelType  # Camera pixel type
    #         print(f"Width: {stSaveParam.nWidth}, Height: {stSaveParam.nHeight}, DataLen: {stSaveParam.nDataLen}")
    #         stSaveParam.nWidth = self.st_frame_info.nWidth            # Width
    #         stSaveParam.nHeight = self.st_frame_info.nHeight          # Height
    #         stSaveParam.nDataLen = self.st_frame_info.nFrameLen
    #         stSaveParam.pData = cast(self.buf_save_image, POINTER(c_ubyte))
    #         stSaveParam.enImageType = MV_Image_Jpeg                   # Image format to save
    #         stSaveParam.nQuality = 80
    #         stSaveParam.pcImagePath = ctypes.create_string_buffer(file_path.encode('ascii'))
    #         stSaveParam.iMethodValue = 2
            
    #         ret = self.obj_cam.MV_CC_SaveImageToFile(stSaveParam)
    #     finally :
    #         self.buf_lock.release()
    #     return ret


    def Save_jpg(self):
        if not self.buf_save_image:
            return MV_E_PARAMETER
        self.buf_lock.acquire()
        try:
            file_path = f"{self.st_frame_info.nFrameNum}.jpg"
            # print(f"Image Path: {file_path}")  # optional

            if not file_path.isascii():
                return MV_E_PARAMETER

            stSaveParam = MV_SAVE_IMG_TO_FILE_PARAM()
            stSaveParam.enPixelType = self.st_frame_info.enPixelType
            stSaveParam.nWidth = self.st_frame_info.nWidth
            stSaveParam.nHeight = self.st_frame_info.nHeight
            stSaveParam.nDataLen = self.st_frame_info.nFrameLen
            stSaveParam.pData = cast(self.buf_save_image, POINTER(c_ubyte))
            stSaveParam.enImageType = MV_Image_Jpeg
            stSaveParam.nQuality = 80
            stSaveParam.pcImagePath = ctypes.create_string_buffer(file_path.encode('ascii'))
            stSaveParam.iMethodValue = 2

            ret = self.obj_cam.MV_CC_SaveImageToFile(stSaveParam)
            return ret
        finally:
            self.buf_lock.release()

    # Save BMP image
    def Save_Bmp(self):

        if 0 == self.buf_save_image:
            return

        # Acquire buffer lock
        self.buf_lock.acquire()

        file_path = str(self.st_frame_info.nFrameNum) + ".bmp"
        c_file_path = file_path.encode('ascii')

        stSaveParam = MV_SAVE_IMG_TO_FILE_PARAM()
        stSaveParam.enPixelType = self.st_frame_info.enPixelType  # Camera pixel type
        stSaveParam.nWidth = self.st_frame_info.nWidth            # Width
        stSaveParam.nHeight = self.st_frame_info.nHeight          # Height
        stSaveParam.nDataLen = self.st_frame_info.nFrameLen
        stSaveParam.pData = cast(self.buf_save_image, POINTER(c_ubyte))
        stSaveParam.enImageType = MV_Image_Bmp                    # Image format to save
        stSaveParam.nQuality = 8
        stSaveParam.pcImagePath = ctypes.create_string_buffer(c_file_path)
        stSaveParam.iMethodValue = 2
        ret = self.obj_cam.MV_CC_SaveImageToFile(stSaveParam)

        self.buf_lock.release()

        return ret
