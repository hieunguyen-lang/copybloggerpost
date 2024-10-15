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
from datetime import datetime,timedelta
import requests
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from rich.progress import Progress
from rich.console import Console
#from create_post_selenium import create_blog_selenium
with open('input.json', 'r', encoding='utf-8') as file:
    data_input = json.load(file)
LINK_POST_ELEMENT= '//*[@id="HTML10"]/div[1]/div/div/div[%s]/span/a'
TITLE_POST_ELEMENT = '//*[@id="HTML10"]/div[1]/div/div/div[%s]/span/a'
TEST_BLOG_ID = data_input['your_blog_id']
URL_CRAW=data_input['url_website_crawed']
LINK_GROUP=data_input['link_facebook_group']
LINK_FANPAGE = data_input['link_fanpage']
CONTENT_1 = data_input['content_1']
CONTENT_2 = data_input['content_2']

chrome_options = Options()
chrome_options.add_argument("--disable-usb")
profile_path = "C:/Users/Admin/AppData/Local/Google/Chrome/User Data/Profile 1"  # Thay đổi đường dẫn nếu cần
chrome_options.add_argument(f"user-data-dir={profile_path}")
service = Service('.\chromedriver.exe')
console = Console()
scheduler = BlockingScheduler()
def wait_with_loading(minutes):
    console.print(f"[cyan]Đang chờ {minutes} phút để chạy hàm main...[/cyan]")
    with Progress() as progress:
        task = progress.add_task("[cyan]Thời gian chờ...", total=minutes * 60)
        
        for _ in range(minutes * 60):
            time.sleep(1)  # Chờ 1 giây
            progress.update(task, advance=1)
def get_post_date(soup,link):
    a_tag = soup.find('a', href=link)

    # Lấy nội dung văn bản sau thẻ <a>
    if a_tag and a_tag.next_sibling:
        # Lấy đoạn văn bản sau thẻ <a>
        date_string = a_tag.next_sibling.strip()
        # Hiển thị ngày tháng
        
        date_string_cleaned = date_string.replace("Tháng", "").replace("-", "").strip()
        date_object = datetime.strptime(date_string_cleaned, "%d %m %Y")
        return date_object
def is_today(input_time):
    if input_time is not None:
        print(input_time)
        today = datetime.now().date()
        
        # So sánh ngày của input_time với ngày hôm nay
        return input_time.date() == today
    else:
        return False
def get_url_new_post(chrome_options, service):
    print("Bắt đầu lấy link post...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url=URL_CRAW
    driver.get(url)
    list_post_datetime = []
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    blog_div = soup.find_all('div', class_='bbrecpost2')
    for post in range(25):
        # Lấy link
        link_href = blog_div[post].find_all('a')[0]['href']
        title_text = blog_div[post].find_all('a')[0].text
        date_release = get_post_date(blog_div[post],link_href)
        if 1==1:
            result = dict()
            result["url"] = link_href
            result["date"] = date_release
            result["title"] = title_text
            list_post_datetime.append(result)
    print(f"Bài viết ngày hôm nay: {len(list_post_datetime)}")
    driver.quit()
    return list_post_datetime
def create_new_div(soup, text):
    new_div = soup.new_tag('div')
    new_div['class'] = 'new-class'
    bold_tag = soup.new_tag('b')
    bold_tag.string = str(text)
    new_div.append(bold_tag)
    return new_div
def translate_url(chrome_options, service, linkpost, title):
    print("Bắt đầu dịch trang....")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(linkpost)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div_content = soup.find('article', class_='post hentry')
    translator = Translator()
    title_translated = translator.translate(title, src='vi', dest='en')
    
    
    if div_content:
        divs_with_style = soup.select('div[style*="border: 0px; font-feature-settings: inherit; font-kerning: inherit; font-optical-sizing: inherit; font-stretch: inherit; font-style: inherit; font-variant: inherit; font-variation-settings: inherit; font-weight: inherit; line-height: inherit; margin: 0px; padding: 0px; text-align: justify; vertical-align: baseline;"]')
        if divs_with_style:
            new_div = create_new_div(soup,CONTENT_1)
            new_div_body = create_new_div(soup,CONTENT_2)
            divs_with_style[6].replace_with(new_div)
            divs_with_style[8].replace_with(new_div)
            divs_with_style[9].replace_with(new_div_body)
            divs_with_style[10].decompose()
            divs_with_style[11].decompose()
        old_div_tags = soup.find('div', class_='tags')
        if old_div_tags:
            old_div_tags.decompose()
        delete_next_post = soup.find('ul', class_='bl-pager')
        if delete_next_post:
            delete_next_post.decompose()
        specific_link = div_content.find_all('a', href=linkpost)  
        delete_social = soup.find('ul', class_='social-likes social-likes_visible') 
        if delete_social:
            delete_social.decompose()
        delete_social_share = soup.find('div', class_='stw') 
        if delete_social_share:
            delete_social_share.decompose()
        if specific_link:
            for a_tag in specific_link:
                del a_tag['href']

        tag_a=div_content.find_all('a', rel="tag")
        if tag_a:
            for a_tag in tag_a: 
                del a_tag['href']
        link_group= div_content.find_all('a', href="https://www.facebook.com/groups/700256606978414/permalink/1069740523363352/")
        for link in link_group:
            link['href'] = LINK_GROUP
        div_content2 = div_content
        link_follow= div_content2.find_all('a', href="https://goo.gl/ZETJYg")
        if link_follow:
            for link in link_follow:
                link['href'] = LINK_FANPAGE 
        div_content3 =div_content2 
        for element in div_content3.find_all(string=True):
            if element.strip():
                translated_text = translator.translate(element.get_text(), dest='en').text
                # Thay thế nội dung gốc bằng nội dung đã dịch
                element.replace_with(translated_text)
           
        with open("result.html", 'w+', encoding='utf-8') as output_file:
                output_file.write(str(div_content3))
        span_tags = div_content3.find_all('span', itemprop='title')
        
        tag_titles = [span.get_text(strip=True) for span in span_tags]
        
    driver.quit()            
    return  div_content3.prettify(),tag_titles,title_translated


def main():
    list_post_datetime = get_url_new_post(chrome_options, service)
    for link in list_post_datetime:
        translator = Translator()
        title_translated = translator.translate(link["title"], src='vi', dest='en')
        title_add_share="[Share]" + title_translated.text
        response = CreatePost.search(title_translated.text,TEST_BLOG_ID)
        if response.get('items'):
            print("Đã có bài đăng: %s" %(title_translated.text))
        else:
            print("Chưa có bài đăng này: %s"%(title_translated.text))
            text_html,list_tag,title_translated = translate_url(chrome_options, service, link["url"],link["title"])
            post = {
                    'kind': 'blogger#post',
                    'blog': {
                        'id': TEST_BLOG_ID  # ID của blog
                    },
                    'content': text_html,
                    'title': title_add_share,
                    'labels': list_tag
                }
            print("Bắt đầu đăng bài...")
            # create_blog_selenium.create_post(text_html,title_add_share)
            response = CreatePost.create_blogger(post,TEST_BLOG_ID)
# minutes=1   ,hours=24   
scheduler.add_job(lambda: wait_with_loading(5), 'interval', minutes=5)
scheduler.add_job(main, 'interval', minutes=5, next_run_time=datetime.now() + timedelta(minutes=5))

try:
    scheduler.start()
    
except (KeyboardInterrupt, SystemExit):
    pass