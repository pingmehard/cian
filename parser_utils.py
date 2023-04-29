import time
import datetime

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup as BS


month_map = {
    "янв" : "01",
    "фев" : "02",
    "мар" : "03",
    "апр" : "04",
    "май" : "05",
    "июн" : "06",
    "июл" : "07",
    "авг" : "08",
    "сен" : "09",
    "окт" : "10",
    "ноя" : "11",
    "дек" : "12",
}



def get_offer_create_date(driver, offer_link):

    # откарываем карточку квартиры
    driver.get(offer_link)
    page_feed = BS(driver.page_source, 'lxml')
    # Находим класс всплывашки история цены, затем находим все указанные в ней цены и берем последнюю, так как она и самая первая цена
    first_price = page_feed.find('div', class_ = "a10a3f92e9--container--y2J5W").find_all('tr', class_ = "a10a3f92e9--history-event--xUQ_P")[-1]
    # получаем первую дату из текста
    first_date = first_price.find('td', class_ = "a10a3f92e9--event-date--BvijC").text

    splitted_first_date = first_date.split()
    try:
        day = int(splitted_first_date[0])
        month = int(month_map[splitted_first_date[1]])
        year = int(splitted_first_date[2])
    except:
        return ''

    # first_date_pythonic = datetime.date(year, month, day)
    # return first_date_pythonic

    return ".".join([year, month, day])


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

        # проверяем загружалась ли эта квартира уже в бэкап
        if offers_load_status:
            if offer['Link'] in offer_links:
                continue

        offer['Link'] = flat.find('a')['href']
        offer['Price'] = flat.find('span', attrs={"data-mark":"MainPrice"}).text
        offer['Images'] = [i['src'] for i in flat.find_all('img') if ".jpg" in i['src']]
        offer['FirstHistoryDate'] = get_offer_create_date(offer['Link'])

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