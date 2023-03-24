import schedule
import time
import main

def job():
    main.proceed_flats()

schedule.every().day.at("16:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)