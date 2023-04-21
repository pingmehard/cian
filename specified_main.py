import json
import os
import urllib.request
import pickle
import datetime
import platform

from selenium import webdriver

import utils
import parser_utils



# configs and several default vars
with open("config.json", "r") as f:
    config = json.load(f)

# dict_convert = config['dict_convert']
dict_convert = {
    0: 'remont edition',
    1: 'neponal nah',
    2: 'babka edition',
    3: 'ebat` berem'
    }



def proceed_specified_flats(main_link = None):

    global dict_convert

    if main_link is None:
        main_link = config['specified_link']

    options = webdriver.ChromeOptions()
    for option in config['specified_chrome_options']:
        options.add_argument(option)


    # try:
    #     driver = webdriver.Remote(
    #         command_executor="http://172.17.0.2:4444/wd/hub",
    #         options=options
    # )
    # except:
    driver = webdriver.Chrome(config['chrome_web_driver'][platform.system()], options=options)

    # загружаем ссылки на дамп офферов из циан
    offers_load_status = False

    if "specified_offers.pickle" in os.listdir(config['offers']):
        with open(config['offers'] + 'specified_offers.pickle', 'rb') as f:
            backup_offers = pickle.load(f)
            offers_load_status = True

        offer_links = [offer['Link'] for offer in backup_offers]
    else:
        offer_links = []
        print('Нет файла дампа загрузки, начинается новая процедура сохранения')
    
    # Парсер начинает загрузку квартир
    offers = parser_utils.proceed(
        driver=driver, 
        main_link=main_link, 
        offers_load_status=offers_load_status, 
        offer_links=offer_links,
        )

    driver.close()

    # загружаем все изображения по ссылкам и добавляем вектора от модели
    for offer in offers:

        data_images = []

        # создаем вектор изображения и добавляем в список
        for image_link in offer['Images']:

            image_name = config['cian_images_catalogue'] + f"{image_link.split('/')[-1]}"

            try:
                urllib.request.urlretrieve(image_link, image_name)
                data = utils.get_image_vector(380, image_name)
                data_images += [data]
            except:
                pass

        # для бота создаем атрибут даты, чтобы иметь возможность 
        # выгружать последние определенные квартиры с определенным результатом
        # Check проставляем для отметки просмотра
        offer['LoadDate'] = datetime.datetime.today().strftime('%Y-%m-%d')
        offer['ViewedInBot'] = 0

    # сохраняем полученные данные по изображениям
    # если бэкап уже был, то добавляем к бэкапу новые загруженные квартиры
    if offers_load_status:
        backup_offers += offers
        with open(config['offers'] + 'specified_offers.pickle', 'wb') as f:
            pickle.dump(backup_offers, f, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        # иначе сохраняем первые офферы квартир
        with open(config['offers'] + 'specified_offers.pickle', 'wb') as f:
            pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)

    return len(offers)



if __name__ == '__main__':
    proceed_specified_flats()
