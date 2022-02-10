from datetime import datetime
import time
import os
import requests
import json
from decimal import Decimal

from config import settings
from tokenbalalances import tokenbalancefunc
from tokensupply import tokensupplyfunc
from gamelogsr import gamelogsrfunc, gamelogsrsnapshotfunc

from apscheduler.schedulers.background import BackgroundScheduler




if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    # scheduler.add_job(train_model, 'interval', seconds=15)
    scheduler.add_job(tokenbalancefunc, trigger='cron', hour='*/1', minute='2')
    scheduler.add_job(tokensupplyfunc, trigger='cron', hour='*/1', minute='4')
    scheduler.add_job(gamelogsrfunc, trigger='cron', second='*/45')
    scheduler.add_job(gamelogsrsnapshotfunc, trigger='cron', hour="1", minute="3")

    
    scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    # print(get_walletaddresses())

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()