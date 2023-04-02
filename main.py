import urllib.request
import time
import pickle
import datetime
from collections import Counter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup as BS

from tensorflow.keras.models import load_model

import numpy as np

import utils
import parser_utils



dict_convert = {
        0 : "remont edition",
        1 : "neponal nah",
        2 : "babka edition",
        3 : "ebat` berem"
    }

def make_conclusion(preds_vector):

    '''
    Выводим предсказанный класс квартиры
    '''

    global dict_convert

    preds = [np.argmax(i) for i in preds_vector]

    count_preds = Counter(preds)

    max_index = max(count_preds.items(), key = lambda x: x[1])

    if count_preds[0] > 3:
        return dict_convert[0]

    return dict_convert[max_index[0]]


def proceed_flats():

    global dict_convert
    # основная ссылка с параметрами поиска
    main_link = "https://www.cian.ru/cat.php?bbox=55.591607686181845%2C36.88460471249996%2C55.91919224422818%2C38.20296408749994&center=55.75574535023922%2C37.54378439999995&currency=2&deal_type=sale&engine_version=2&in_polygon[0]=37.4074853_55.8688097%2C37.3985589_55.8606737%2C37.3930657_55.8517629%2C37.3930657_55.8420772%2C37.3930657_55.8323915%2C37.3916924_55.8230932%2C37.3903191_55.813795%2C37.3868859_55.8044967%2C37.3820794_55.7955859%2C37.3745263_55.7870625%2C37.3683465_55.7781517%2C37.3690331_55.7688534%2C37.3683465_55.7595552%2C37.3683465_55.7498695%2C37.3710931_55.7405712%2C37.3745263_55.7304981%2C37.3779595_55.7208124%2C37.384826_55.712289%2C37.3964989_55.7057028%2C37.4033654_55.6967919%2C37.4102319_55.6882685%2C37.4150384_55.6789703%2C37.4219048_55.6704469%2C37.4287713_55.6619235%2C37.439071_55.6545624%2C37.4459374_55.6456515%2C37.4569238_55.6386778%2C37.4672234_55.6313167%2C37.4747765_55.6227933%2C37.4823296_55.6142699%2C37.4988091_55.6138825%2C37.5091088_55.6212436%2C37.5159753_55.629767%2C37.5214684_55.6386778%2C37.5297082_55.6468138%2C37.5413811_55.6534001%2C37.5564873_55.6491384%2C37.5722802_55.6456515%2C37.5873864_55.6413898%2C37.6038659_55.6402276%2C37.6203454_55.6413898%2C37.6203454_55.6510755%2C37.621032_55.6603738%2C37.6361382_55.6646355%2C37.6526177_55.6657978%2C37.6677239_55.669672%2C37.6835168_55.672384%2C37.6993096_55.6754834%2C37.7109826_55.6820697%2C37.7041161_55.6905931%2C37.6883233_55.6936925%2C37.6732171_55.6979542%2C37.6663506_55.7064776%2C37.6780236_55.7130639%2C37.6917565_55.7184879%2C37.7068627_55.7227496%2C37.7013696_55.7316604%2C37.6972497_55.7409587%2C37.6958764_55.7502569%2C37.6848901_55.7572306%2C37.6876366_55.7665289%2C37.6958764_55.7746648%2C37.698623_55.7839631%2C37.6993096_55.7932613%2C37.7137292_55.7979105%2C37.7192223_55.8068213%2C37.7089227_55.8141824%2C37.6945031_55.8188315%2C37.6780236_55.8184441%2C37.6629174_55.8223184%2C37.6498711_55.8281298%2C37.6587975_55.8362658%2C37.6670373_55.8444017%2C37.6622308_55.8533126%2C37.663604_55.8626108%2C37.6663506_55.8719091%2C37.6684106_55.8812073%2C37.6690972_55.8905056%2C37.6533044_55.8932176%2C37.6368249_55.8947673%2C37.6203454_55.896317%2C37.6038659_55.8970919%2C37.5873864_55.8967044%2C37.5709069_55.8951547%2C37.5537408_55.8951547%2C37.5372613_55.8947673%2C37.5200951_55.8947673%2C37.5036156_55.8920553%2C37.4878228_55.888181%2C37.47203_55.8843068%2C37.4562371_55.8815948%2C37.4397576_55.8788828%2C37.4246514_55.8750085%2C37.4116051_55.8688097%2C37.4074853_55.8688097&maxprice=28000000&min_house_year=2005&minfloor=10&mintarea=50&object_type[0]=1&offer_type=flat&only_flat=1&origin=map&polygon_name[0]=%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%20%D0%BF%D0%BE%D0%B8%D1%81%D0%BA%D0%B0&totime=-2&wp=1&zoom=11"
    cian_link = "https://www.cian.ru/"

    # загружаем обученную модель для предсказания класса изображений
    model_path = "./saved_models/model_v3/"
    try:
        model = load_model(model_path)
    except:
        model = load_model("./model_v3/")

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=600,1000")
    options.add_argument("--disable-dev-shm-usage")


    driver = webdriver.Remote(
        command_executor="http://172.17.0.2:4444/wd/hub",
        options=options
   )

    # driver = webdriver.Chrome("./webdriver/chromedriver", options=options)

    # загружаем ссылки на дамп офферов из циан
    offers_load_status = False

    try:
        # open a file for binary writing
        with open('./data/offers.pickle', 'rb') as f:
            # dump the data to the file
            backup_offers = pickle.load(f)
            offers_load_status = True

        offer_links = [offer['Link'] for offer in backup_offers]
    except:
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

            image_name = f"./cian_images/{image_link.split('/')[-1]}"

            try:
                urllib.request.urlretrieve(image_link, image_name)
                data = utils.get_image_vector(380, image_name)
                data_images += [data]
            except:
                pass

        # предсказываем класс изображения
        preds = model.predict(np.array(data_images))
        # сохраняем предсказанный класс в атрибуты изображения
        offer['Predicts'] = preds

        # создаем итоговый вектор с предсказанной бизнес-категорией
        offer['Result'] = make_conclusion(offer['Predicts'])

        # для бота создаем атрибут даты, чтобы иметь возможность 
        # выгружать последние определенные квартиры с определенным результатом
        # Check проставляем для отметки просмотра
        offer['LoadDate'] = datetime.datetime.today().strftime('%Y-%m-%d')
        offer['ViewedInBot'] = 0

    # сохраняем полученные данные по изображениям
    # если бэкап уже был, то добавляем к бэкапу новые загруженные квартиры
    if offers_load_status:
        backup_offers += offers
        with open('./data/offers.pickle', 'wb') as f:
            pickle.dump(backup_offers, f, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        # иначе сохраняем первые офферы квартир
        with open('./data/offers.pickle', 'wb') as f:
            pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)

    return len(offers)

if __name__ == '__main__':
    proceed_flats()