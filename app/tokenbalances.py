
from bdb import effective
import requests
import json
from decimal import Decimal
from datetime import datetime
import time
from operator import indexOf
from web3 import Web3

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

# get the list of all recruitments for a wallet
def get_walletrecruitments(walletid: int):
    response = ""
    url = "http://{0}:{1}/recruitments/listids/{2}".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port, walletid)
    response = requests.get(url)

    recruitments= []
    if response.status_code == 200:
        for value in json.loads(response.text):
            recruitments.append(value['recruitmentid'])

    return recruitments


# def get_tokenbalance(contractaddress: str, walletaddress :str ):
def tokenbalancefunc():

    wallets = get_walletaddresses()
    tokens = get_cryptotokens()

    for wallet in wallets:
        walletid = wallet['walletid']
        walletaddress = wallet['walletaddress']

        # post tokenbalance
        for token in tokens:
            # wallet details

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
        
        # post missions

        # delete missions not completed
        cleanup_recruitments(walletid=walletid)

        # get all existing missions
        existingsrecruitments = get_walletrecruitments(walletid=walletid)
        print('existing recruitments: ', len(existingsrecruitments))
        


        web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
        recruiting_contract = '0x44fc245b59678792d8b0eb57b4a6861d6e1353a3'
        myaddress = web3.toChecksumAddress(recruiting_contract)
        recruiting_abi = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"adr","type":"address"},{"indexed":false,"internalType":"string","name":"permissionName","type":"string"},{"indexed":false,"internalType":"uint256","name":"permissionIndex","type":"uint256"}],"name":"AuthorizedFor","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"message","type":"string"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"DebugLog","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"from","type":"address"},{"indexed":false,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"permissionName","type":"string"},{"indexed":false,"internalType":"uint256","name":"permissionIndex","type":"uint256"},{"indexed":false,"internalType":"uint64","name":"expiryTime","type":"uint64"}],"name":"PermissionLocked","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"permissionName","type":"string"},{"indexed":false,"internalType":"uint256","name":"permissionIndex","type":"uint256"}],"name":"PermissionUnlocked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"uint256","name":"missionId","type":"uint256"}],"name":"RecruitmentFinished","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256[]","name":"cardIds","type":"uint256[]"},{"indexed":true,"internalType":"uint256","name":"missionId","type":"uint256"}],"name":"RecruitmentStarted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"adr","type":"address"},{"indexed":false,"internalType":"string","name":"permissionName","type":"string"},{"indexed":false,"internalType":"uint256","name":"permissionIndex","type":"uint256"}],"name":"UnauthorizedFor","type":"event"},{"inputs":[{"internalType":"address","name":"adr","type":"address"},{"internalType":"string","name":"permissionName","type":"string"}],"name":"authorizeFor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"adr","type":"address"}],"name":"authorizeForAllPermissions","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"adr","type":"address"},{"internalType":"string[]","name":"permissionNames","type":"string[]"}],"name":"authorizeForMultiplePermissions","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getAllMissionsOfUser","outputs":[{"components":[{"internalType":"uint256","name":"missionId","type":"uint256"},{"internalType":"uint256[]","name":"cardIds","type":"uint256[]"},{"internalType":"uint40","name":"startTimestamp","type":"uint40"},{"internalType":"uint32","name":"duration","type":"uint32"},{"internalType":"bool","name":"retrieved","type":"bool"},{"internalType":"address","name":"owner","type":"address"}],"internalType":"struct SamuraiRecruiting.OutputMission[]","name":"missions_","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"missionId","type":"uint256"}],"name":"getIdsAsArray","outputs":[{"internalType":"uint256[]","name":"arr","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"cardIds","type":"uint256[]"}],"name":"getIdsAsSingleUint","outputs":[{"internalType":"uint72","name":"ids","type":"uint72"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"ids","type":"uint256[]"}],"name":"getInfCost","outputs":[{"internalType":"uint256","name":"infCost","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"ids","type":"uint256[]"}],"name":"getLockDuration","outputs":[{"internalType":"uint32","name":"dur","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"getMission","outputs":[{"components":[{"internalType":"uint256","name":"missionId","type":"uint256"},{"internalType":"uint256[]","name":"cardIds","type":"uint256[]"},{"internalType":"uint40","name":"startTimestamp","type":"uint40"},{"internalType":"uint32","name":"duration","type":"uint32"},{"internalType":"bool","name":"retrieved","type":"bool"},{"internalType":"address","name":"owner","type":"address"}],"internalType":"struct SamuraiRecruiting.OutputMission","name":"mission_","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"permissionName","type":"string"}],"name":"getPermissionNameToIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"permissionName","type":"string"}],"name":"getPermissionUnlockTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"missionId","type":"uint256"}],"name":"getUnlockTime","outputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"infAdr","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"infCostBase","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"infCostBaseGeneral","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"infCostPerUsage","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"infCostPerUsageGeneral","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"adr","type":"address"},{"internalType":"enum Permission","name":"permission","type":"uint8"}],"name":"isAuthorizedFor","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"adr","type":"address"},{"internalType":"string","name":"permissionName","type":"string"}],"name":"isAuthorizedFor","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"permissionName","type":"string"}],"name":"isLocked","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isOwner","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lockDurationBase","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lockDurationBaseGeneral","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lockDurationPerUsage","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lockDurationPerUsageGeneral","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"permissionName","type":"string"},{"internalType":"uint64","name":"time","type":"uint64"}],"name":"lockPermission","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"maxUsages","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxUsagesGeneral","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"missionOwnerships","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"missions","outputs":[{"internalType":"uint72","name":"cardIds","type":"uint72"},{"internalType":"uint40","name":"startTimestamp","type":"uint40"},{"internalType":"uint32","name":"duration","type":"uint32"},{"internalType":"bool","name":"retrieved","type":"bool"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"bytes","name":"","type":"bytes"}],"name":"onERC721Received","outputs":[{"internalType":"bytes4","name":"","type":"bytes4"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"ids","type":"uint256[]"}],"name":"recruit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"retrieveBNB","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"missionId","type":"uint256"}],"name":"retrieveSamurai","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"retrieveTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rsunAdr","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rsunCost","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"samuraiAdr","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"inf_","type":"address"}],"name":"setInfAdr","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"base","type":"uint256"},{"internalType":"uint256","name":"perUsage","type":"uint256"},{"internalType":"uint256","name":"baseGeneral","type":"uint256"},{"internalType":"uint256","name":"perUsageGeneral","type":"uint256"}],"name":"setInfCosts","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"base","type":"uint256"},{"internalType":"uint256","name":"perUsage","type":"uint256"},{"internalType":"uint256","name":"baseGeneral","type":"uint256"},{"internalType":"uint256","name":"perUsageGeneral","type":"uint256"}],"name":"setLockDurations","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"normal","type":"uint256"},{"internalType":"uint256","name":"general","type":"uint256"}],"name":"setMaxUsages","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"rsun_","type":"address"}],"name":"setRsunAdr","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newCost","type":"uint256"}],"name":"setRsunCost","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"samuraiAdr_","type":"address"}],"name":"setSamuraiAdr","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"num","type":"uint256"}],"name":"setStopIncreasingAt","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"stopIncreasingAt","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"adr","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"adr","type":"address"},{"internalType":"string","name":"permissionName","type":"string"}],"name":"unauthorizeFor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"adr","type":"address"}],"name":"unauthorizeForAllPermissions","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"adr","type":"address"},{"internalType":"string[]","name":"permissionNames","type":"string[]"}],"name":"unauthorizeForMultiplePermissions","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"permissionName","type":"string"}],"name":"unlockPermission","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"usages","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'

        contract = web3.eth.contract(address=myaddress, abi=recruiting_abi)
        recruting_missions = contract.functions.getAllMissionsOfUser(walletaddress).call()


        i = 0
        if len(recruting_missions) > 0:
            for index, m in enumerate(recruting_missions):
                recruitmentid = m[0]
                recruitingsamurais = m[1]
                blockno = m[2]
                missionduration = m[3]
                missioncomplete = m[4]
                # walletaddress = m[5]
                # print('index: ', index, '- recruitmentid: ', recruitmentid, ' - on mission:', recruitingsamurais, ' - mission accomplished: ', missioncomplete, 'wallet: ', walletaddress )
                # print('found: ', recruitmentid in existingsrecruitments.values())
                

                if len(existingsrecruitments) > 0:
                    if not recruitmentid in existingsrecruitments:
                        sams = ','.join([str(elem) for elem in recruitingsamurais]) 
                        resp = post_recruitments(recruitmentid=recruitmentid, walletid=walletid, walletaddress=walletaddress, recruitingsamurais=sams, blockno=blockno,
                                    missionduration=missionduration, missioncomplete=missioncomplete)
                        i += 1
                        if not resp.status_code == 201:
                            print(resp.content, ' for recruitmentid: ', recruitmentid)
                else:
                    sams = ','.join([str(elem) for elem in recruitingsamurais]) 
                    resp = post_recruitments(recruitmentid=recruitmentid, walletid=walletid, walletaddress=walletaddress, recruitingsamurais=sams, blockno=blockno,
                            missionduration=missionduration, missioncomplete=missioncomplete)
                    i += 1
                    if not resp.status_code == 201:
                        print(resp.content, ' for recruitmentid: ', recruitmentid)

            print(i, ' recruiting missions posted for wallet ', walletaddress)



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

def post_recruitments(recruitmentid: int, walletid: int, walletaddress: str, recruitingsamurais: str, blockno: int, missioncomplete: bool, missionduration: int ):
    response = ""
    url = "http://{0}:{1}/recruitments".format(settings.p2eguildadm_api_host , settings.p2eguildadm_api_port)

    body = {'recruitmentid': recruitmentid, 'walletid': walletid, 'walletaddress' : walletaddress, 'recruitingsamurais' : recruitingsamurais, 'blockno': blockno,
            'missioncomplete': missioncomplete, 'missionduration': missionduration }

    response = requests.post(url, json=body)   
    return response

def cleanup_recruitments(walletid: int):
    response = ""
    url = "http://{0}:{1}/recruitments/cleanup/{2}".format(settings.p2eguildadm_api_host , settings.p2eguildadm_api_port, walletid )


    response = requests.delete(url)   
    return response


