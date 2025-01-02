from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import ddddocr
import time
import json
def get_cookie():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.get("https://shuiyuan.sjtu.edu.cn")
    captcha_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "captcha-img"))
    )
    location = captcha_element.location
    size = captcha_element.size
    time.sleep(3)
    driver.save_screenshot("full_page.png")
    left = location['x']-10
    top = location['y']
    right = left + size['width']
    bottom = top + size['height']
    full_img = Image.open("full_page.png")
    captcha_img = full_img.crop((left, top, right, bottom))
    captcha_img.save("captcha.png")
    f=open("captcha.png",mode='rb')
    img=f.read()
    ocr =ddddocr.DdddOcr()
    result =ocr.classification(img)
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.ID, "input-login-user")))
    username_input.clear()
    username_input.send_keys("account")
    # 定位并填写密码
    password_input = wait.until(EC.presence_of_element_located((By.ID, "input-login-pass")))
    password_input.clear()
    password_input.send_keys("password")
    # 定位并填写验证码
    captcha_input = wait.until(EC.presence_of_element_located((By.ID, "input-login-captcha")))
    captcha_input.clear()
    captcha_input.send_keys(result)
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "submit-password-button")))
    login_button.click()
    print(result)
    print("登录成功！")
    time.sleep(5)
    # 获取所有 cookies
    cookies = driver.get_cookies()
    has_t_cookie = any(cookie['name'] == '_t' for cookie in cookies)
    if has_t_cookie:
        print('爬取成功')
    else:
        print('爬取失败，重新获取')
        driver.quit()
        return False
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

    with open('cookies.json', 'w', encoding='utf - 8') as f:
        json.dump(cookies_dict, f, ensure_ascii=False, indent=4)

    print("\nCookies 信息：")
    for name, value in cookies_dict.items():
        print(f"{name}: {value}")
    driver.quit()
    return True
