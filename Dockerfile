FROM python

COPY ./bot.py .
COPY ./main.py .
COPY ./requirements.txt .
COPY ./specified_main.py .
COPY ./utils.py .
COPY ./webdriver/ .
COPY ./saved_models .
COPY ./data/ .

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]