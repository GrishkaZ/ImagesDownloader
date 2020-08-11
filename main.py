import json
import os
import re
import requests  # to sent GET requests
from bs4 import BeautifulSoup  # to parse HTML

# user can input a topic and a number
# download first n images from google image search

GOOGLE_IMAGE = \
    'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

YANDEX_IMAGE = 'https://yandex.ru/images/search?text='

# The User-Agent request header contains a characteristic string 
# that allows the network protocol peers to identify the application type, 
# operating system, and software version of the requesting software user agent.
# needed for google search

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


def download_images():
    # ask for user input
    data = input('What are you looking for? ')
    n_images = int(input('How many images do you want? '))
    #max_wh = list(input('How max size? (w,h)'))
    #min_wh = list(input('How min size? (w,h)'))

    print('Start searching...')

    #searchurl = GOOGLE_IMAGE + 'q=' + data
    searchurl = YANDEX_IMAGE + data.strip()
    print('Search URL: ',searchurl)

    #response = requests.get(searchurl, headers=usr_agent)
    response = requests.get(searchurl)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.prettify())

    results = soup.findAll('div', {'class':re.compile('serp-item serp-item_type_search serp-item_group_search serp-item_pos_\d+ serp-item_scale_yes justifier__item i-bem')}, limit=n_images)

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

    print(f'found {len(imagelinks)} images')
    print('Start downloading...')

    for i, imagelink in enumerate(imagelinks):
        response = requests.get(imagelink)
        imagename = SAVE_FOLDER + '/' + data + str(i + 1) + '.jpg'
        with open(imagename, 'wb') as file:
            file.write(response.content)
    print('Done')


if __name__ == '__main__':
    main()