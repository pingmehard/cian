import platform
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup as BS


# configs and several default vars
with open("config.json", "r") as f:
    config = json.load(f)



def get_offer_create_date(offer_link):

    # adding options to chrome
    options = webdriver.ChromeOptions()
    for option in config['main_chrome_options']:
        options.add_argument(option)

    # откарываем карточку квартиры
    driver = webdriver.Chrome(config['chrome_web_driver'][platform.system()], options=options)

    driver.get(offer_link)
    time.sleep(.5)
    try:
        driver.find_element('xpath', '//a[@data-name="Link"]').click()
    except:
        try:
            driver.find_element('xpath', '//button[@data-name="OfferStats"]').click()
        except:
            driver.find_element('xpath', '//button[@data-name="OfferMeta"]').click()

    time.sleep(.2)
    page_feed = BS(driver.page_source, 'lxml')
    creation_date = page_feed.find('div', class_ = "a10a3f92e9--information--JQbJ6").find('div').text.split()[-1]
    print(creation_date)
    return creation_date


def get_flat_info(page_feed, offers_load_status, offer_links):
    '''
    Получаем список квартир на странице со всеми объектами
    Достаем из карточек страницы нужную инфу
    '''

    all_page_cards = page_feed.find('div', class_ = "_93444fe79c--wrapper--W0WqH").find_all('article', attrs={"data-name":"CardComponent"})

    offer = {}
    offers = []

    print(f"Количество загруженных квартир из Циан {len(all_page_cards)}")

    for flat in all_page_cards:

        offer['Link'] = flat.find('a')['href']

        # проверяем загружалась ли эта квартира уже в бэкап
        if offers_load_status:
            if offer['Link'] in offer_links:
                continue
        
        offer['Price'] = flat.find('span', attrs={"data-mark":"MainPrice"}).text
        offer['Images'] = [i['src'] for i in flat.find_all('img') if ".jpg" in i['src']]
        try:
            offer['FirstHistoryDate'] = get_offer_create_date(flat.find('a')['href'])
        except Exception as e:
            print(e)
            print(offer['Link'])

        offers += [offer]
        
        offer = {}

    print(f"Количество исключенных из выдачи квартир {len(all_page_cards)-len(offers)}")

    return offers

# Прокручиваем страницу

def proceed_page_scrolling(driver):

    for i in range(3):
        ActionChains(driver).key_down(Keys.END).perform()
        time.sleep(.5)

# Листаем страницы

def next_page(driver, main_link, last_page):

    driver.get(main_link + f'&p={last_page + 1}')

    return last_page + 1        

def proceed(driver, main_link, offers_load_status, offer_links):

    last_page = 1
    driver.get(main_link)
    page_feed = BS(driver.page_source, 'lxml')

    first_flat_link = page_feed.find('div', class_ = '_93444fe79c--wrapper--W0WqH').find('a')['href']

    offers = []

    while True:

        proceed_page_scrolling(driver)        

        offers += get_flat_info(page_feed, offers_load_status, offer_links)
        
        last_page = next_page(driver, main_link, last_page)
        page_feed = BS(driver.page_source, 'lxml')

        if first_flat_link == page_feed.find('div', class_ = '_93444fe79c--wrapper--W0WqH').find('a')['href']:
            break

    return offers