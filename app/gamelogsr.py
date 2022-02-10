import requests
import json
from decimal import Decimal
from datetime import datetime
import time
import hashlib

from config import settings


# get the wallets from the p2eguildadm_api
def get_walletaddresses():
    response = ""
    url = "http://{0}:{1}/wallets".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port)
    response = requests.get(url)

    wallets = json.loads(response.text)

    return wallets


def gamelogsrfunc():

    wallets = get_walletaddresses()
    i = 0

    for wallet in wallets:
        issnapshot = False
        # wallet details
        walletid = wallet['walletid']
        walletaddress = wallet['walletaddress']
    
        # get energy
        response = ""
        baseurl="http://api.risingsun.finance/energy/"
        url = "{0}/{1}".format(baseurl, walletaddress)
        response = requests.get(url)

        data = json.loads(response.text)

        current_energy = data['current_energy']
        max_energy = data['max_energy']

        response = ""
        baseurl="https://api.risingsun.finance/earnings/"
        url = "{0}/{1}".format(baseurl, walletaddress)
        response = requests.get(url)

        data = json.loads(response.text)

        today_earnings = data['today_earnings']
        total_earnings = data['total_earnings']


        changehash = hashlib.sha256()
        changehash.update(bytes(walletaddress, 'utf-8'))
        changehash.update(bytes(str(issnapshot), 'utf-8'))
        changehash.update(bytes(str(current_energy), 'utf-8'))
        changehash.update(bytes(str(max_energy), 'utf-8'))
        changehash.update(bytes(str(today_earnings), 'utf-8'))
        changehash.update(bytes(str(total_earnings), 'utf-8'))

        log_dts = str(datetime.now())

        if canstore_log(changehash.hexdigest()) == True:
            # post the new game log entry in the guild database
            post_gamelogsr(log_dts = log_dts, walletid = walletid, issnapshot=issnapshot , pending_earnings=today_earnings, total_earnings=total_earnings, current_energy=current_energy, max_energy=max_energy, changehash=changehash.hexdigest())
            i += 1
      
    print("{0}: gamelog finished.".format(str(datetime.now())))
    # print('{0} records written'.format(i))

    return 

def gamelogsrsnapshotfunc():

    wallets = get_walletaddresses()
    i = 0

    for wallet in wallets:
        issnapshot = True
        # wallet details
        walletid = wallet['walletid']
        walletaddress = wallet['walletaddress']
    
        # get energy
        response = ""
        baseurl="https://api.risingsun.finance/energy/"
        url = "{0}/{1}".format(baseurl, walletaddress)
        response = requests.get(url)

        data = json.loads(response.text)

        current_energy = data['current_energy']
        max_energy = data['max_energy']

        response = ""
        baseurl="https://api.risingsun.finance/earnings/"
        url = "{0}/{1}".format(baseurl, walletaddress)
        response = requests.get(url)

        data = json.loads(response.text)

        today_earnings = data['today_earnings']
        total_earnings = data['total_earnings']


        changehash = hashlib.sha256()
        changehash.update(bytes(walletaddress, 'utf-8'))
        changehash.update(bytes(str(issnapshot), 'utf-8'))
        changehash.update(bytes(str(current_energy), 'utf-8'))
        changehash.update(bytes(str(max_energy), 'utf-8'))
        changehash.update(bytes(str(today_earnings), 'utf-8'))
        changehash.update(bytes(str(total_earnings), 'utf-8'))

        log_dts = str(datetime.now())

        if canstore_log(changehash.hexdigest()) == True:
            # post the new game log entry in the guild database
            post_gamelogsr(log_dts = log_dts, walletid = walletid, issnapshot=issnapshot , pending_earnings=today_earnings, total_earnings=total_earnings, current_energy=current_energy, max_energy=max_energy, changehash=changehash.hexdigest())
            i += 1
    print("{0}: gamelog snapshot finished.".format(str(datetime.now())))
    #print('{0} records written'.format(i))
    return 



# the game log entries we retrieved from the rising sun api are posted back into the guild database for analysis purposes
def post_gamelogsr(log_dts : str, walletid: int, issnapshot: bool, pending_earnings: int, total_earnings: int, current_energy: int, max_energy: int, changehash: str):
    response = ""
    url = "http://{0}:{1}/gamelogsr".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port)

    body = {'log_dts': log_dts, 'walletid': walletid, 'issnapshot' : issnapshot,
            'pending_earnings': pending_earnings, 'total_earnings': total_earnings, 'current_energy' : current_energy , 'max_energy' : max_energy, 'changehash' : changehash }

    response = requests.post(url, json=body)   

    return response


def canstore_log(changehash: str):
    response = ""
    url = "http://{0}:{1}/gamelogsr/checkhash/{2}".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port, changehash)
    response = requests.get(url)

    if response.status_code == 200:
        return False
    else:
        return True