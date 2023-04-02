import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup as BS


def get_flat_info(page_feed):
    '''
    Получаем список квартир на странице со всеми объектами
    Достаем из карточек страницы нужную инфу
    '''

    all_page_cards = page_feed.find('div', class_ = "_93444fe79c--wrapper--W0WqH").find_all('article', attrs={"data-name":"CardComponent"})

    offer = {}
    offers = []

    for flat in all_page_cards:

        offer['Link'] = flat.find('a')['href']
        offer['Price'] = flat.find('span', attrs={"data-mark":"MainPrice"}).text
        offer['Gallery'] = [i['src'] for i in flat.find_all('img') if ".jpg" in i['src']]

        offers += [offer]
        offer = {}

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

def proceed(driver, main_link):

    last_page = 1
    first_page_link = driver.current_url
    driver.get(main_link)
    offers = []

    while True:

        proceed_page_scrolling(driver)
        page_feed = BS(driver.page_source, 'lxml')

        offers += get_flat_info(page_feed)
        
        last_page = next_page(driver, main_link, last_page)

        if first_page_link == driver.current_url:
            break

    return offers