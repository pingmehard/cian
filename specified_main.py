import os
import urllib.request
import pickle
import datetime
import platform

from selenium import webdriver

import utils
import parser_utils



dict_convert = {
        0 : "remont edition",
        1 : "neponal nah",
        2 : "babka edition",
        3 : "ebat` berem"
    }



def proceed_specified_flats(main_link = None):

    global dict_convert

    if main_link is None:
        main_link = "https://www.cian.ru/cat.php?bbox=55.780182774571%2C37.46535871177908%2C55.7820661916001%2C37.47331414371724&center=55.78112449451335%2C37.469336427748175&deal_type=sale&engine_version=2&in_polygon[0]=37.4704786_55.7820336%2C37.4702747_55.7820578%2C37.4700816_55.782079%2C37.4699475_55.7820971%2C37.4697007_55.7821243%2C37.4695184_55.7821425%2C37.4693681_55.7821576%2C37.469234_55.7821667%2C37.4690516_55.7821818%2C37.4689068_55.7821999%2C37.4687781_55.7822271%2C37.4686493_55.7822513%2C37.4685152_55.7822453%2C37.4684884_55.7821636%2C37.4684508_55.782073%2C37.4684347_55.7820004%2C37.4683918_55.7819067%2C37.4683435_55.7818371%2C37.4682953_55.7817585%2C37.468247_55.7816739%2C37.4682094_55.7815983%2C37.4681504_55.7815167%2C37.4681129_55.7814441%2C37.4680378_55.7813686%2C37.4679788_55.781296%2C37.4679466_55.7812144%2C37.4679412_55.7811237%2C37.4679251_55.7810149%2C37.4679037_55.7809362%2C37.4678715_55.7808425%2C37.4678447_55.7807579%2C37.4678232_55.7806702%2C37.4678017_55.7805765%2C37.4677856_55.7804949%2C37.4677535_55.7804193%2C37.467732_55.7803467%2C37.4678125_55.7802863%2C37.4679949_55.7802591%2C37.4681236_55.7802409%2C37.4682738_55.7802198%2C37.4684133_55.7802077%2C37.4685474_55.7802016%2C37.4686761_55.7801986%2C37.468821_55.7801895%2C37.4693842_55.7801805%2C37.4694433_55.780256%2C37.4694969_55.7803286%2C37.4695452_55.7803981%2C37.4696042_55.7804798%2C37.4696525_55.7805493%2C37.4696846_55.7806218%2C37.4697115_55.7806974%2C37.4697383_55.780773%2C37.4697651_55.7808546%2C37.4697973_55.7809393%2C37.4698188_55.7810209%2C37.4698724_55.7810995%2C37.469926_55.7811841%2C37.4699743_55.7812567%2C37.470028_55.7813383%2C37.470087_55.7814139%2C37.4701406_55.7815046%2C37.4701728_55.7815772%2C37.4702265_55.7816618%2C37.4702747_55.7817465%2C37.470323_55.781819%2C37.4703713_55.7818885%2C37.4704142_55.7819641%2C37.4704518_55.7820397%2C37.4704786_55.7820336&offer_type=flat&origin=map&polygon_name[0]=%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%20%D0%BF%D0%BE%D0%B8%D1%81%D0%BA%D0%B0&wp=1&zoom=18"

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1000,1000")
    options.add_argument("--disable-dev-shm-usage")

    # try:
    #     driver = webdriver.Remote(
    #         command_executor="http://172.17.0.2:4444/wd/hub",
    #         options=options
    # )
    # except:
    if platform.system() == 'Linux':
        driver = webdriver.Chrome("./webdriver/chromedriver", options=options)
    elif platform.system() == 'Windows':
        driver = webdriver.Chrome("./webdriver/chromedriver.exe", options=options)

    # загружаем ссылки на дамп офферов из циан
    offers_load_status = False

    if "specified_offers.pickle" in os.listdir('./data/'):
        # open a file for binary writing
        with open('./data/specified_offers.pickle', 'rb') as f:
            # dump the data to the file
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

            image_name = f"./cian_images/{image_link.split('/')[-1]}"

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
        with open('./data/specified_offers.pickle', 'wb') as f:
            pickle.dump(backup_offers, f, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        # иначе сохраняем первые офферы квартир
        with open('./data/specified_offers.pickle', 'wb') as f:
            pickle.dump(offers, f, protocol=pickle.HIGHEST_PROTOCOL)

    return len(offers)

if __name__ == '__main__':
    proceed_specified_flats()
