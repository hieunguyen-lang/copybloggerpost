from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup,NavigableString
import time
from googletrans import Translator
from create_blog import CreatePost
from datetime import datetime,timedelta, timezone
import requests
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from rich.progress import Progress
from rich.console import Console
import logging
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
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
TIME_CRAW = data_input['time_craw_minus']
CHROME_DRIVER_PATH =data_input['chrome_driver_path']
TEXT_LINK_FANPAGE=data_input['text_link_fanpage']
TEXT_LINK_GROUP=data_input['text_link_group']
chrome_options = Options()
chrome_options.add_argument("--disable-usb")
profile_path = "C:/Users/Admin/AppData/Local/Google/Chrome/User Data/Profile 1"  # Thay đổi đường dẫn nếu cần
chrome_options.add_argument(f"user-data-dir={profile_path}")
service = Service()
console = Console()
scheduler = BlockingScheduler()
def wait_with_loading(minutes):
    console.print(f"[cyan]Đang chờ {minutes} phút để quét bài viết lần tiếp theo...[/cyan]")
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
        #is_today(date_release)
        if not is_today(date_release):
            result = dict()
            result["url"] = link_href
            result["date"] = date_release
            result["title"] = title_text
            list_post_datetime.append(result)
    print(f"Bài viết ngày hôm nay: {len(list_post_datetime)}")

    driver.quit()
    return list_post_datetime
def create_div_with_link(soup, link_text, link_url):
    new_div = soup.new_tag('div')
    
    # Tạo thẻ a với thuộc tính href
    new_link = soup.new_tag('a', href=link_url)

    # Thêm thẻ strong cho bold và thẻ em cho nghiêng
    bold_italic_text = soup.new_tag('em')  # Tạo thẻ em cho kiểu chữ nghiêng
    bold_text = soup.new_tag('strong')      # Tạo thẻ strong cho kiểu chữ đậm
    bold_text.string = link_text             # Thêm nội dung cho thẻ strong
    bold_italic_text.append(bold_text)      # Thêm thẻ strong vào thẻ em

    new_link.append(bold_italic_text)        # Thêm thẻ em vào thẻ a
    new_div.append(new_link)                  # Thêm thẻ a vào trong thẻ div
    return new_div
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
        new_div = create_new_div(soup,CONTENT_1)
        new_div_body = create_new_div(soup,CONTENT_2)
        new_div_invite_to_page=create_div_with_link(soup,TEXT_LINK_FANPAGE, LINK_FANPAGE)
        new_div_invite_to_group=create_div_with_link(soup,TEXT_LINK_GROUP, LINK_FANPAGE)
        divs_with_style[0].insert_after(new_div)
        divs_with_style[0].insert_after(new_div_body)
        divs_with_style[0].insert_after(new_div_invite_to_page)
        divs_with_style[0].insert_after(new_div_invite_to_group)
        add_more_tag =soup.find('h2', class_ = 'post-title entry-title')
        a_tag_truncated_text = soup.find('h2', class_ ='post-title entry-title').find('a')
        text_title_tag = a_tag_truncated_text.get_text()
        a_tag_truncated_text.decompose()
        if add_more_tag:
            # Thêm <span style="display: none;">...</span> sau phần tử <h2>
            add_more_tag.insert_after(soup.new_tag('span', style='display: none;'))
            add_more_tag.find_next_sibling('span').string = '<!-- more -->'
        aauthor_tag =soup.find('div', class_ = 'post_author_date date updated vcard')
        if aauthor_tag:
            aauthor_tag.decompose()
        if divs_with_style:
            for item in divs_with_style:
                item.decompose()
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
        
        author_div = div_content.find('div', id="author-info")
        if author_div:
            author_div.decompose()

        for element in div_content.find_all(string=True):
            if element.strip():
                translated_text = translator.translate(element.get_text(), dest='en').text
                # Thay thế nội dung gốc bằng nội dung đã dịch
                element.replace_with(translated_text)
        translator = Translator()
        text_title_tag_en = translator.translate(text_title_tag, src='vi', dest='en')   
        with open("result.html", 'w+', encoding='utf-8') as output_file:
                output_file.writelines(text_title_tag_en.text + '<!-- more -->')
                output_file.writelines(str(div_content))
        span_tags = div_content.find_all('span', itemprop='title')
        
        tag_titles = [span.get_text(strip=True) for span in span_tags]
        with open('result.html', 'r', encoding='utf-8') as file:
            content = file.read()
    driver.quit()            
    return  content,tag_titles,title_translated


def main():
    specific_date = datetime(2024, 10, 20)
    today = datetime.now()
    # So sánh hai ngày
    if today > specific_date:
        logging.error(f"Đã Kết thúc quá trình demmo, tool không thể sử dụng nữa!!")
        raise Exception("Đã Kết thúc quá trình demmo, tool không thể sử dụng nữa!!")
    list_post_datetime = get_url_new_post(chrome_options, service)
    if len(list_post_datetime) >0:
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
                published_datetime = datetime.now(timezone.utc).isoformat(timespec='seconds')
                post = {
                        'kind': 'blogger#post',
                        'blog': {
                            'id': TEST_BLOG_ID  # ID của blog
                        },
                        'content': text_html,
                        'title': title_add_share,
                        'labels': list_tag,
                        'published': published_datetime
                    }
                print("Bắt đầu đăng bài...")
                # create_blog_selenium.create_post(text_html,title_add_share)
                response = CreatePost.create_blogger(post,TEST_BLOG_ID)
# minutes=1   ,hours=24  
def job_listener(event):
    if event.exception:
        console.print(f"Job {event.job_id} gặp lỗi!", style="bold red")
    else:
        console.print(f"Job {event.job_id} đã hoàn thành!", style="bold blue") 
scheduler.add_job(lambda: wait_with_loading(int(TIME_CRAW)), 'interval', minutes=5)
scheduler.add_job(main, 'interval', minutes=5, next_run_time=datetime.now() + timedelta(minutes=int(TIME_CRAW)))
scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

try:
    text = "TOOL BY HIEU  NGUYEN"
    print(text)
    print("Starting tool!!")
    main()
    scheduler.start()
    
except (KeyboardInterrupt, SystemExit):
    pass