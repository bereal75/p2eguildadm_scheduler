
from bdb import effective
import requests
import json
from decimal import Decimal
from datetime import datetime
import time

from config import settings



# get the wallets from the p2eguildadm_api
def get_walletaddresses():
    response = ""
    url = "http://{0}:{1}/wallets".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port)
    response = requests.get(url)

    wallets = json.loads(response.text)

    return wallets

# get the list of interesting tokens in respect to the guild. Can be extended in the crypto_token table in the guild database
def get_cryptotokens():
    response = ""
    url = "http://{0}:{1}/cryptotokens".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port)
    response = requests.get(url)

    tokens = json.loads(response.text)

    return tokens


# def get_tokenbalance(contractaddress: str, walletaddress :str ):
def tokenbalancefunc():

    wallets = get_walletaddresses()
    tokens = get_cryptotokens()

    for wallet in wallets:
        for token in tokens:
            # wallet details
            walletid = wallet['walletid']
            walletaddress = wallet['walletaddress']
            # token details
            crypto_tokenid = token['crypto_tokenid']
            contractaddress = token['contractaddress']

            # get balance for every wallet and every token retrieved earlier from the p2eguildadm_api
            baseurl = "https://api.bscscan.com/api?module=account&tag=latest&action=tokenbalance"
            url = "{0}&contractaddress={1}&address={2}&apikey={3}".format(baseurl, contractaddress,walletaddress, settings.bscscan_api_key)
            response = requests.get(url)

            data = json.loads(response.text)

            balance = int(data['result']) / pow(10, token['decimalpoints'])
            balance_dts = str(datetime.now())

            # a free bscscan api key can query 5 x second at the maximum therefore let's wait a second to make sure we do not over-extend our subscription
            time.sleep(1)

            # post the new tokenbalance to the p2eguildam_api
            post_tokenbalance(walletid = walletid,crypto_tokenid= crypto_tokenid, balance= balance, balance_dts= balance_dts)

            # print("contractaddress {0} in walletid {1} wallet {2} - balance: {3} ".format(contractaddress, walletid, walletaddress, data['result']))
    print('{0}: tokenbalance update finished'.format(str(datetime.now())))
    return 



# the token balances we retrieved from the BSC blockain are posted back into the guild database for analysis purposes
def post_tokenbalance(walletid: int, crypto_tokenid: int, balance: Decimal, balance_dts: str ):
    response = ""
    url = "http://{0}:{1}/walletbalance".format(settings.p2eguildadm_api_host , settings.p2eguildadm_api_port)

    body = {'walletid': walletid, 'crypto_tokenid': crypto_tokenid,
            'balance': balance, 'balance_dts': balance_dts }

    response = requests.post(url, json=body)   

    return response


