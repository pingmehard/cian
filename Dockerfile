FROM python

# ADD ./saved_models/ .
# ADD ./data/ .

# COPY ./bot.py .
# COPY ./main.py .
# COPY ./requirements.txt .
# COPY ./specified_main.py .
# COPY ./utils.py .
# COPY ./creds.py .

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]