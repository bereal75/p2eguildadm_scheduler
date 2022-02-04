import requests
import json
from decimal import Decimal
from datetime import datetime
import time

from config import settings

# get the list of tokens we track the total supply. Can be extended in the crypto_token table in the guild database
def get_cryptotokens():
    response = ""
    url = "http://{0}:{1}/cryptotokens/tracktotalsupply".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port)
    response = requests.get(url)

    tokens = json.loads(response.text)

    return tokens


def tokensupplyfunc():

    tokens = get_cryptotokens()

    for token in tokens:

        # token details
        crypto_tokenid = token['crypto_tokenid']
        contractaddress = token['contractaddress']

        # example:
        # https://api.bscscan.com/api?module=stats&action=tokensupply&contractaddress=0xe9e7cea3dedca5984780bafc599bd69add087d56&apikey=YourApiKeyToken

        response = ""
        baseurl = "https://api.bscscan.com/api?module=stats&action=tokensupply"
        url = "{0}&contractaddress={1}&apikey={2}".format(baseurl, contractaddress, settings.bscscan_api_key)
        response = requests.get(url)

        data = json.loads(response.text)

        # convert the token supply to decimal (with removal of token decimal points)
        if token['decimalpoints'] == 0:
            tokensupply = int(data['result'])
        else:
            tokensupply = int(data['result']) / token['decimalpoints']

        tokensupply_dts = str(datetime.now())

        # a free bscscan api key can query 5 x second at the maximum therefore let's wait a second to make sure we do not over-extend our subscription
        time.sleep(1)

        # post the new tokensupply to the p2eguildam_api
        post_tokensupply(crypto_tokenid=crypto_tokenid, tokensupply=tokensupply, tokensupply_dts=tokensupply_dts)

        # print("contractaddress:  {0} - balance: {1} ".format(contractaddress, data['result']))
    print('{0}: tokensupply update finished'.format(str(datetime.now())))
    return 


# the token balances we retrieved from the BSC blockain are posted back into the guild database for analysis purposes
def post_tokensupply(crypto_tokenid: int, tokensupply: Decimal, tokensupply_dts: str ):
    response = ""
    url = f"http://{settings.p2eguildadm_api_host}:{settings.p2eguildadm_api_port}/tokensupply"

    body = {'crypto_tokenid': crypto_tokenid,
            'tokensupply': tokensupply, 'tokensupply_dts': tokensupply_dts }

    response = requests.post(url, json=body)   

    return response



