from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import pyperclip
from selenium.webdriver.common.action_chains import ActionChains
chrome_options = Options()
chrome_options.add_argument("--disable-usb")
profile_path = "C:/Users/Admin/AppData/Local/Google/Chrome/User Data/Profile 1"  # Thay đổi đường dẫn nếu cần
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

chrome_options.add_argument(f"user-data-dir={profile_path}")
service = Service('.\chromedriver.exe')

class create_blog_selenium:

    @staticmethod
    def create_post(html_code,title_add_share):
        
        #driver = webdriver.Chrome(service=service, options=chrome_options)
        driver = uc.Chrome(options=chrome_options)
        url="https://www.blogger.com/blog/posts/5192359981093929026?bpli=1&pli=1"
        driver.get(url)
        actions = ActionChains(driver)
        create_post_button = WebDriverWait(driver, 40).until(
                                EC.visibility_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/gm-raised-drawer/div/div[2]/div/c-wiz/div[3]/div/div/span'))
                            )
        create_post_button.click()
        input_field = WebDriverWait(driver, 40).until(
                                 EC.visibility_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/c-wiz/div/div[1]/div[1]/div[1]/div/div[1]/input'))
                                 )
        input_field.send_keys(title_add_share) 

        time.sleep(10)
        driver.execute_script("""
                                var editor = document.querySelector('.CodeMirror').CodeMirror;
                                editor.setValue(arguments[0]);
                                """, html_code)

        time.sleep(10)
        
        button = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz[3]/div/c-wiz/div/div[1]/div[2]/div[4]/span'))
                                )

        driver.execute_script("""
            var evt = new MouseEvent('mousedown', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            arguments[0].dispatchEvent(evt);
        """, button)

        driver.execute_script("""
            var evt = new MouseEvent('mouseup', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            arguments[0].dispatchEvent(evt);
        """, button)
        print("click xong")
        # Sau đó gọi click
        driver.execute_script("arguments[0].click();", button)
        time.sleep(5)
        confirm_button = WebDriverWait(driver, 40).until(
                                 EC.visibility_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/div[4]/div/div[2]/div[3]/div[2]/span/span'))
                                 )
        confirm_button.click
        time.sleep(40)
        driver.quit()
create_blog_selenium.create_post("ádf", "test")
