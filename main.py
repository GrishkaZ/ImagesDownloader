import json
import os
import re
import sys
import traceback
from tqdm import tqdm
import requests  # to sent GET requests
from bs4 import BeautifulSoup  # to parse HTML
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


GOOGLE_IMAGE = \
    'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

YANDEX_IMAGE = 'https://yandex.ru/images/search?text='

CHROME_DRIVER = 'chromedriver.exe'


"""usr_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}
"""

usr_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 OPR/67.0.3575.115',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}


SAVE_FOLDER = 'images'

def main():
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)
    download_images()


# Download Page for more than 30 images
def download_extended_page(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--headless")

    try:
        browser = webdriver.Chrome(CHROME_DRIVER, chrome_options=options)
    except Exception as e:
        print("Looks like Chromedriver does not exist. Perhaps directory is specified not correctly. (exception: %s)" % e)
        sys.exit()
    browser.set_window_size(1024, 768)

    # Open the link
    browser.get(url)
    time.sleep(1)
    print("Getting you a lot of images. This may take a few moments...")

    element = browser.find_element_by_tag_name("body")
    # Scroll down
    for i in range(30):
        element.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)

    try:
        browser.find_element_by_id("smb").click()
        for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)  # bot id protection
    except:
        for i in range(10):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)  # bot id protection

    print("Reached end of Page.")
    time.sleep(0.5)

    source = browser.page_source #page source
    #close the browser
    browser.close()

    return source




def download_images():
    # ask for user input
    data = input('What are you looking for? ')
    n_images = int(input('How many images do you want? '))
    #max_wh = list(input('How max size? (w,h)'))
    #min_wh = list(input('How min size? (w,h)'))

    print('Start searching...')

    #searchurl = GOOGLE_IMAGE + 'q=' + data
    searchurl = YANDEX_IMAGE + data.strip().replace(' ','%20')
    print('Search URL: ',searchurl)

    #response = requests.get(searchurl, headers=usr_agent)
    if n_images >30:
        html = download_extended_page(searchurl)
    else:
        html = requests.get(searchurl).text

    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.prettify())

    results = soup.findAll('div',{'class':re.compile('serp-item serp-item_type_search serp-item_group_search serp-item_pos_\d+ serp-item_scale_yes justifier__item i-bem')},limit=n_images)

    #'class':"serp-item serp-item_type_search serp-item_group_search serp-item_pos_1 serp-item_scale_yes justifier__item i-bem"

    imagelinks = []
    for teg in results:
        try:
            text = teg['data-bem']
        except(KeyError):
            continue
        text_dict = json.loads(text)
        try:
            link = text_dict['serp-item']['preview'][0]['origin']['url']
            width = text_dict['serp-item']['preview'][0]['origin']['w']
            height = text_dict['serp-item']['preview'][0]['origin']['h']
            print(f'width {width}, height {height}')
            imagelinks.append(link)
        except(KeyError):
            continue

    img_count = len(imagelinks)
    print(f'found {img_count} images')
    print('Start downloading...')

    errors_count = 0
    for i, imagelink in tqdm(enumerate(imagelinks),desc= 'Downloaded'):
        try:
            #print(imagelink)
            response = requests.get(imagelink)
            imagename = SAVE_FOLDER + '/' + data + str(i + 1) + '.jpg'
            with open(imagename, 'wb') as file:
                file.write(response.content)
        except:
            errors_count +=1
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
            continue
    print(f'Downloaded {img_count-errors_count}/{img_count} images')


if __name__ == '__main__':
    main()
