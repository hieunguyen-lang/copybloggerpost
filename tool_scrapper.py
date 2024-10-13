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
from googletrans import Translator
from create_blog import CreatePost
NEW_POST_ELEMENT='//*[@id="HTML10"]/div[1]/div/div/div[%s]'
TEST_BLOG_ID = '4818145507962779412'
chrome_options = Options()
chrome_options.add_argument("--disable-usb")
service = Service('.\chromedriver.exe')

def get_url_new_post(NEW_POST_ELEMENT, chrome_options, service):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url="https://nhasachtinhoc.blogspot.com/"
    driver.get(url)
    linkpost =[]
    WebDriverWait(driver, 40).until(
                            EC.visibility_of_element_located((By.XPATH, '//*[@id="HTML10"]/div[1]/div/div/div[1]'))
                        )
    for post in range(25):
        element_click= NEW_POST_ELEMENT % str(post+1)
        link_post_new_elements = WebDriverWait(driver, 40).until(
                            EC.visibility_of_element_located((By.XPATH, element_click))
                        )
        link_post_new_elements.click()
        links = driver.find_elements(By.XPATH, '//*[@id="HTML10"]/div[1]/div/div/div[25]/span/a')
        link_href = links[0].get_attribute('href')
        linkpost.append(link_href)
    return linkpost


#listlinkpost = get_url_new_post(NEW_POST_ELEMENT, chrome_options, service)
listlinkpost='https://nhasachtinhoc.blogspot.com/2024/10/chia-se-khoa-hoc-recursion-backtracking-va-dynamic-programming-trong-java-6405.html#google_vignette'
def translate_url(chrome_options, service, listlinkpost):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(listlinkpost)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div_content = soup.find('article', class_='post hentry')
    translator = Translator()
    if div_content:
        for element in div_content.find_all(text=True):
            print("element: %s" % element)
            if element.strip():
                translated_text = translator.translate(element.get_text(), dest='en').text
                # Thay thế nội dung gốc bằng nội dung đã dịch
                element.replace_with(translated_text)
                print(element.string)
    return  div_content.prettify()

text_html = translate_url(chrome_options, service, listlinkpost)
post = {
        'kind': 'blogger#post',
        'blog': {
            'id': TEST_BLOG_ID  # ID của blog
        },
        'title': 'A test post',
        'content': text_html
    }
CreatePost.create_blogger(post,TEST_BLOG_ID)
