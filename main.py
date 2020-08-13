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
EXTENSIONS_LIST = ['png', 'jpg']


def main():

    download_images()


# Download Page for more than 30 images (based on code from "google-images-download")
def download_extended_page(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--headless")

    try:
        browser = webdriver.Chrome(options=options)
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
            print('!' * 60)
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


def get_raw_html_page(request_string, n_images, se = 'Yandex'):

    # searchurl = GOOGLE_IMAGE + 'q=' + data
    searchurl = YANDEX_IMAGE + request_string.strip().replace(' ', '%20')
    print('Search URL: ', searchurl)

    # html = requests.get(searchurl, headers=usr_agent).text

    if n_images > 30:
        return download_extended_page(searchurl)
    else:
        return requests.get(searchurl).text


def extract_images_urls(html, n_images, max_wh, min_wh):
    min_w = int(min_wh[0])
    min_h = int(min_wh[1])
    max_w = int(max_wh[0])
    max_h = int(max_wh[1])
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup.prettify())
    #find images-tegs
    results = soup.findAll('div',
                           {'class': re.compile(
                               'serp-item serp-item_type_search serp-item_group_search serp-item_pos_\d+ serp-item_scale_yes justifier__item i-bem')},
                           limit=n_images)

    #extract images urls from tegs
    images_urls = []
    for teg in results:
        try:
            text = teg['data-bem']
        except KeyError as e:
            continue
        text_dict = json.loads(text)
        try:
            images_dict = text_dict['serp-item']['preview']
            for i in range(len(images_dict)):
                #print(i)
                try:
                    width = images_dict[i]['origin']['w']
                    height = images_dict[i]['origin']['h']
                except KeyError:
                    continue
                #print(f'width {width}, height {height}')
                if (min_w < width) & (width < max_w) & (min_h < height) & (height< max_h):
                    link = images_dict[i]['origin']['url']
                    images_urls.append(link)
                    break
                """
                link = text_dict['serp-item']['preview'][0]['origin']['url']
                width = text_dict['serp-item']['preview'][0]['origin']['w']
                height = text_dict['serp-item']['preview'][0]['origin']['h']
                # print(f'width {width}, height {height}')
                images_urls.append(link)
                """
        except KeyError as e:
            continue
    return images_urls


def write_images(images_urls, img_name, extension = None):
    #func for making file image names
    make_imagename = make_file_name_func(extension)

    img_count = len(images_urls)
    print(f'found {img_count} images')
    print('Start downloading...')

    errors_count = 0
    for i, img_url in tqdm(enumerate(images_urls), desc='Downloaded'):
        try:
            # print(img_url)
            response = requests.get(img_url)
            file_name = SAVE_FOLDER + '/' + img_name + ' ' + str(i + 1)
            imagename = make_imagename(file_name,img_url)
            with open(imagename, 'wb') as file:
                file.write(response.content)
        except Exception as e:
            errors_count += 1
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
            print('\nImage wasn\'t downloaded: Exception %s' % e)
            continue
    print(f'Downloaded {img_count - errors_count}/{img_count} images')


def make_file_name_func(extension):
    if extension:
        if extension not in EXTENSIONS_LIST:
            raise TypeError(f'the extension can be equal to value from: {EXTENSIONS_LIST}')
        return lambda *args: args[0] + '.' + extension
    else:
        #split img url and take it's extension
        return lambda *args: args[0] + '.' + args[1].split('.')[-1]


def download_images():
    # ask for user input
    global SAVE_FOLDER
    request_string = input('What are you looking for? ')
    n_images = int(input('How many images do you want? '))

    #max_wh = input('How max size? (w,h)').split()
    #min_wh = input('How min size? (w,h)').split()
    max_wh = [10000,10000]
    min_wh = [10,10]

    extension = input(f'Which extension to convert to? {EXTENSIONS_LIST} ').lower()

    while True:
        save_folder = input('Select the download directory: ')
        if save_folder:
            if not os.path.exists(save_folder):
                try:
                    os.makedirs(save_folder)
                except Exception as e:
                    print(e)
                    continue
            SAVE_FOLDER = save_folder
            break
        elif not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)
            break

    print('Start searching...')
    html = get_raw_html_page(request_string, n_images)
    images_urls = extract_images_urls(html,n_images,max_wh,min_wh)
    with open(SAVE_FOLDER+'/downloaded urls log.txt','a') as file:
        for url in images_urls:
            file.write(url+'\n')
    write_images(images_urls, request_string, extension)



if __name__ == '__main__':
    main()
