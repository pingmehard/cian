import platform
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup as BS

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# configs and several default vars
with open("config.json", "r") as f:
    config = json.load(f)



# Прокручиваем страницу вниз
def proceed_page_scrolling(driver):

    for i in range(3):
        ActionChains(driver).key_down(Keys.END).perform()
        time.sleep(.5)

def get_house_info(page_feed):

    try:
        try:
            # получаем всю информацию о доме, берем правую колонку, выгружаем все строки из нее
            about_house = page_feed.find_all('div', attrs={"data-name" : "OfferSummaryInfoGroup"})[-1].find_all('div', attrs={"data-name" : "OfferSummaryInfoItem"})

            # для каждой строки данных получаем текст и заполняем список
            about_house_info = []
            for i in about_house:
                about_house_info += [[elem.text for elem in i.find_all('p')]]
        except: # в случае, когда карточка квартиры заполняется данными из БТИ
            # ищем выписку из БТИ от Циан, затем ищем все элементы описания по аналогии с обычным поиском
            about_house_bti = page_feed.find('div', attrs={'data-name':'BtiHouseData'}).find_all('div', attrs={'data-name':'Item'})
            about_house_info = []
            for i in about_house_bti:
                about_house_info += [[elem.text for elem in i.find_all('div')]]

        print(about_house_info) if config['dev_mode'] else None
        # отдаем словарь элементов
        return dict(about_house_info)
    except:
        return None

def get_offer_info(offer_link):

    try:

        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"
        # adding options to chrome
        options = webdriver.ChromeOptions()
        # options.add_argument("--disable-javascript")
        # options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})
        for option in config['specified_chrome_options']:
            options.add_argument(option)

        # откарываем карточку квартиры
        driver = webdriver.Chrome(config['chrome_web_driver'][platform.system()], options=options, desired_capabilities=capa)
        wait = WebDriverWait(driver, 5)
        driver.get(offer_link)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'a10a3f92e9--button--lyQVM')))

        try:
            driver.find_element('xpath', '//div[@data-name="OfferStats"]').click()
        except:
            driver.find_element('xpath', '//button[@data-name="OfferStats"]').click()

        time.sleep(.2)
        page_feed = BS(driver.page_source, 'lxml')

        # получаем данные о доме
        house_info = get_house_info(page_feed)

        driver.close()

        creation_date = page_feed.find('div', class_ = "a10a3f92e9--information--JQbJ6").find('div').text.split()[-1]
        print(creation_date) if config['dev_mode'] else None
        driver.close()
        return creation_date, house_info
    except:
        return None, None


def get_flat_info(page_feed, offers_load_status, offer_links):
    '''
    Получаем список квартир на странице со всеми объектами
    Достаем из карточек страницы нужную инфу
    '''

    # получаем все карточки квартир по карточке продавца
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
        offer['FirstHistoryDate'], offer['HouseInfo'] = get_offer_info(flat.find('a')['href'])
        offer['FlatSeller'] = flat.find('div', attrs={'data-name':'BrandingLevelWrapper'}).find_all('span')[1].text

        offers += [offer]
        offer = {}

    print(f"Количество исключенных из выдачи квартир {len(all_page_cards)-len(offers)}")

    return offers

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