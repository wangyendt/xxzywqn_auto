#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: wangye(Wayne) 
@license: Apache Licence 
@file: MumuSimulator.py 
@time: 2024/01/20
@contact: wang121ye@hotmail.com
@site:  
@software: PyCharm 

# code is far away from bugs.
"""

import win32gui
# from pywayne.gui import GuiOperation
from Gui import GuiOperation
import pyautogui
import numpy as np
import win32ui
import win32con
from PIL import Image
import easyocr
import cv2
import pprint
import sys


class MumuSimulator:
    def __init__(self):
        self.gui = GuiOperation()
        windows = self.gui.find_window('MuMu模拟器12')
        if not windows: raise RuntimeError('No mumu simulator found!')
        self.mumu = windows[0]
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.w = 0
        self.h = 0
        self.screen_left = 0
        self.screen_right = 0
        self.screen_top = 0
        self.screen_bottom = 0
        self.screen_left_to_right = 0
        self.screen_top_to_bottom = 0

    def get_window_screenshot(self, hwnd):
        # 获取窗口的设备上下文（DC）
        window_dc = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(window_dc)
        cdc = dcObj.CreateCompatibleDC()

        # 获取窗口尺寸
        self.left, self.top, self.right, self.bot = win32gui.GetClientRect(hwnd)
        self.w = self.right - self.left
        self.h = self.bot - self.top

        # 获取窗口在屏幕上的位置
        rect = win32gui.GetWindowRect(hwnd)
        self.screen_left, self.screen_top, self.screen_right, self.screen_bottom = rect
        self.screen_left_to_right = self.screen_right - self.screen_left
        self.screen_top_to_bottom = self.screen_bottom - self.screen_top

        # 创建位图对象
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cdc.SelectObject(bmp)

        # 截图
        cdc.BitBlt((0, 0), (self.w, self.h), dcObj, (0, 0), win32con.SRCCOPY)

        # 将截图保存到PIL图像
        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        # 清理内存
        dcObj.DeleteDC()
        cdc.DeleteDC()
        win32gui.ReleaseDC(hwnd, window_dc)
        win32gui.DeleteObject(bmp.GetHandle())

        # 将PIL图像转换为NumPy数组
        im_np = np.array(im)
        # 转换颜色空间从BGR到RGB
        im_np = cv2.cvtColor(im_np, cv2.COLOR_BGR2RGB)

        return im_np


if __name__ == '__main__':

    name = sys.argv[1] if len(sys.argv) > 1 else '爱丽榭'

    print('programming start...')
    mumu_simulator = MumuSimulator()
    reader = easyocr.Reader(['ch_sim', 'en'])  # this needs to run only once to load the model into memory
    # cv2.namedWindow('313_ye', cv2.WINDOW_NORMAL)
    cur_state = 'main'
    inviting_cnt = 0
    auto_choose_cnt = 0
    while True:
        img = mumu_simulator.get_window_screenshot(mumu_simulator.mumu)
        result = reader.readtext(img)
        # pprint.pprint(result)
        result_dict = {r[1]: (r[0], r[2]) for r in result if r[1] and r[2] > 0.5}
        pprint.pprint(result_dict)
        # print(result[0])
        # print(mumu_simulator.left, mumu_simulator.right, mumu_simulator.top, mumu_simulator.bottom)
        if '邀请列表' in result_dict and '不接受非好友的组队邀请' in result_dict:
            cur_state = 'inviting'
        elif all(kw in result_dict for kw in (name, '挑战')):
            cur_state = 'main'
        elif all(k in kw for kw in result_dict for k in ('击杀怪物', '挑战时间', '伤害统计')) or '点击任意区域关闭' in result_dict:
            print('here')
            pyautogui.moveTo(mumu_simulator.screen_left + 360 * mumu_simulator.screen_left_to_right / (2331 - 1575),
                             mumu_simulator.screen_top + 200 * mumu_simulator.screen_top_to_bottom / (1418 - 33))
            pyautogui.click()
            auto_choose_cnt = 0
            continue
        elif any(k in kw for kw in result_dict for k in ('进度', '自动选择')):
            cur_state = 'fight'
        else:
            cur_state = 'main'
        print(f'{cur_state=}')
        print(f'{mumu_simulator.screen_left=},{mumu_simulator.screen_top=},{mumu_simulator.screen_right=},{mumu_simulator.screen_bottom=}')
        if cur_state == 'main':
            for k, v in result_dict.items():
                if '副本邀请' in k and v[1] > 0.5:
                    print(v)
                    rect = v[0]
                    coord = np.mean(rect, axis=0).astype(int)
                    print(coord)
                    mumu_simulator.gui.bring_to_top(mumu_simulator.mumu)
                    pyautogui.moveTo(mumu_simulator.screen_left + coord[0], mumu_simulator.screen_top + coord[1])
                    pyautogui.click()
                    cur_state = 'inviting'
        elif cur_state == 'inviting':
            mumu_simulator.gui.bring_to_top(mumu_simulator.mumu)
            pyautogui.moveTo(mumu_simulator.screen_left + 630 * mumu_simulator.screen_left_to_right / (2331 - 1575),
                             mumu_simulator.screen_top + 320 * mumu_simulator.screen_top_to_bottom / (1418 - 33))
            pyautogui.click()
            inviting_cnt += 1
            if inviting_cnt >= 6:
                mumu_simulator.gui.bring_to_top(mumu_simulator.mumu)
                pyautogui.moveTo(mumu_simulator.screen_left + 720 * mumu_simulator.screen_left_to_right / (2331 - 1575),
                                 mumu_simulator.screen_top + 180 * mumu_simulator.screen_top_to_bottom / (1418 - 33))
                pyautogui.click()
                inviting_cnt = 0
        elif cur_state == 'fight':
            for k, v in result_dict.items():
                if '自动选择' in k and v[1] > 0.5:
                    if auto_choose_cnt >= 1:
                        continue
                    auto_choose_cnt += 1
                    rect = v[0]
                    coord = np.mean(rect, axis=0).astype(int)
                    mumu_simulator.gui.bring_to_top(mumu_simulator.mumu)
                    pyautogui.moveTo(mumu_simulator.screen_left + coord[0] - 90 * mumu_simulator.screen_left_to_right / (2331 - 1575),
                                     mumu_simulator.screen_top + coord[1])
                    pyautogui.click()
        continue
        # for i, res in enumerate(result):
        #     coord = res[0]
        #     text = res[1]
        #     prob = res[2]
        #     # print(text, prob)
        #     if '%' in text:
        #         print(coord[0], coord[2], text)
        #     cv2.rectangle(img, (int(coord[0][0]), int(coord[0][1])), (int(coord[2][0]), int(coord[2][1])), (0, 0, 255, 255), 4, cv2.INTER_NEAREST)
        # cv2.resizeWindow('313_ye', mumu_simulator.w, mumu_simulator.h)
        # cv2.imshow('313_ye', img)
        # cv2.waitKey(1)
