1. Для корректной работы образа требуется запустить контейнер с selenium chrome
Команда: docker run -d -p 4444:4444 --shm-size=2g selenium/standalone-chrome:3.141.59-20210607

2. Далее дополнить код с драйвером следующим вариантом кода:
options = webdriver.ChromeOptions()
driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4444/wd/hub",
        options=options
   )

options является обязательным компонентом для запуска сессии, в нем указывается что за драйвер будет использоваться

3. Запустить докер контейнер для запуска мероприятий в коде python
docker build . --no-cache -t bot-service:v100
docker run bot-service:v100

docker run -d selenium/standalone-chrome:3.141.59-20210607

docker run -d -p 4444:4444 --shm-size=2g selenium/standalone-chrome:3.141.59-20210607