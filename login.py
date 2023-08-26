import json
import random
import sys
import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

phone_number = ""
password = ""


def f():
    opt = webdriver.EdgeOptions()
    # headless
    opt.add_argument("--headless")
    browser = webdriver.Edge(options=opt)
    browser.get(
        "https://plogin.m.jd.com/login/login?")
    time.sleep(3)
    # report-eventid="MLoginRegister_SMSVerification"
    browser.find_element(By.CSS_SELECTOR, "[report-eventid='MLoginRegister_SMSVerification']").click()
    # class="policy_tip-checkbox"
    browser.find_element(By.CSS_SELECTOR, ".policy_tip-checkbox").click()
    # id="username"
    browser.find_element(By.CSS_SELECTOR, "[id='username']").send_keys(phone_number)
    browser.find_element(By.CSS_SELECTOR, "[id='pwd']").send_keys(password)
    # report-eventid="MLoginRegister_Login"
    browser.find_element(By.CSS_SELECTOR, "[report-eventid='MLoginRegister_Login']").click()

    for _ in range(10):
        time.sleep(5)
        # id="cpc_img"
        cpc_img = browser.find_element(By.CSS_SELECTOR, "[id='cpc_img']")
        # id="small_img"
        small_img = browser.find_element(By.CSS_SELECTOR, "[id='small_img']")
        # 保存图片
        cpc_base64 = cpc_img.get_attribute("src")
        small_base64 = small_img.get_attribute("src")

        # base64转图片
        import base64

        cpc_img = base64.b64decode(cpc_base64.split(",")[1])
        small_img = base64.b64decode(small_base64.split(",")[1])
        with open("./cpc_img.png", "wb") as f:
            f.write(cpc_img)
        with open("./small_img.png", "wb") as f:
            f.write(small_img)

        from PIL import Image
        import cv2
        import numpy as np

        a = Image.open("./cpc_img.png").convert("L")
        b = Image.open("./small_img.png").convert("L")
        a = np.array(a)
        b = np.array(b)
        a[a > 240] = 255
        a[a <= 240] = 0
        b[b > 240] = 255
        b[b <= 240] = 0
        a = a.astype(np.uint8)
        b = b.astype(np.uint8)

        min_mse = 100000
        min_index = 0
        Image.fromarray(a).save("./a_gray.png")
        Image.fromarray(b).save("./b_gray.png")
        for i in range(0, a.shape[1], 1):
            big_img = a[:, i:i + 30].copy()
            if big_img.shape[1] != 30:
                break
            small_img = b[:, 0:30].copy()
            big_img[small_img == 0] = 0
            mse = np.mean((big_img - small_img) ** 2)
            if mse < min_mse:
                min_mse = mse
                min_index = i
        a[:, min_index:min_index + 1] = 30
        Image.fromarray(a).save("./result.png")

        sp_msg = browser.find_element(By.CSS_SELECTOR, "[class='sp_msg'")
        sp_img = sp_msg.find_element(By.TAG_NAME, "img")

        # 滑动
        from selenium.webdriver import ActionChains

        time.sleep(3)
        # 向右
        ActionChains(browser).drag_and_drop_by_offset(sp_img, min_index + 65, 0).perform()
        # simulateDragX(browser, sp_img, min_index + 65)
        time.sleep(2)

        try:
            second_stage = browser.find_element(By.CSS_SELECTOR, "[class='tip']")
        except:
            continue
            pass

        for _ in range(20):
            cpc_img = browser.find_element(By.CSS_SELECTOR, "[id='cpc_img']")
            cpc_base64 = cpc_img.get_attribute("src")
            cpc_img = base64.b64decode(cpc_base64.split(",")[1])
            with open("./cpc_img.png", "wb") as f:
                f.write(cpc_img)

            img0 = Image.open("./cpc_img.png", mode="r").convert("RGB")
            img0 = np.array(img0)
            img0 = cv2.resize(np.array(img0), (420, 276), interpolation=cv2.INTER_LINEAR)
            ar = img0.copy()
            # 找到黄色
            ar[(ar[:, :, 0] > 200) & (ar[:, :, 1] > 200) & (ar[:, :, 2] < 100)] = [255, 0, 0]
            # 找到第一个值为[255, 0, 0]的点
            x, y = np.where((ar[:, :, 0] == 255) & (ar[:, :, 1] == 0) & (ar[:, :, 2] == 0))
            if len(x) == 0:
                submmit = browser.find_element(By.CSS_SELECTOR, "[class='sure_btn']")
                submmit.click()
                time.sleep(2)
                continue
            # 取出中间的一个点
            x = x[len(x) // 2]
            y = y[len(y) // 2]
            # print(x, y)
            # y是从左边开始数的点

            # 点击
            try:
                cpc_img = browser.find_element(By.CSS_SELECTOR, "[id='cpc_img']")
                ActionChains(browser).move_to_element_with_offset(cpc_img, y - 210, x - 138).click().perform()
                time.sleep(2)
                submmit = browser.find_element(By.CSS_SELECTOR, "[class='sure_btn']")
                submmit.click()
                time.sleep(3)

                # 获取cookie
                cookies = browser.get_cookies().__str__()
                # print(cookies)
                if cookies.index("pt_token") != -1:
                    return cookies
            except:
                # print("error")
                pass
            time.sleep(3)
    browser.close()


if __name__ == '__main__':
    phone_number = sys.argv[1]
    password = sys.argv[2]
    while True:
        try:
            ck = f()
            data = ck
            if data != "":
                data = data.replace("'", '"')
                data = data.replace("True", "true")
                data = data.replace("False", "false")
                data = data.replace("None", "null")
                j = json.loads(data)
                pt_key = ""
                pt_pin = ""
                for i in j:
                    if i["name"] == "pt_key":
                        pt_key = i["value"]
                    if i["name"] == "pt_pin":
                        pt_pin = i["value"]

                print(f"pt_key={pt_key};pt_pin={pt_pin};")
                break
        except:
            print("获取失败")
    exit(0)