import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import csv

pagesToScan = 121000
hashToFilter = '45d493a6f73fa5f404244a5fb8472fc014ca5885'
data = dict()

for pageNumber in range (1, pagesToScan, 1):

        req = requests.get('https://neoscan.io/addresses/' + str(pageNumber), headers={'User-Agent': 'Mozilla/5.0'})
        req.encoding = 'UTF-8'
        soup = BeautifulSoup(req.text, 'html.parser')

        if(pageNumber % 10 == 0):
                print('Page number: ' + str(pageNumber))
        if soup is not None:
                for address in soup.find_all('a', attrs={'class':'large-blue-link col-4-width'}):
                        addressString = address.get_text()
                        reqJson = requests.get('https://api.neoscan.io/api/main_net/v1/get_balance/' + addressString, headers={'User-Agent': 'Mozilla/5.0'})
                        reqJson.encoding = 'UTF-8'
                        jsonData = json.loads(reqJson.text)

                        for balance in jsonData['balance']:
                                if(balance['asset_hash'] == hashToFilter):
                                        if(float(balance['amount']) >= 20000):
                                                data.update({addressString : str(balance['amount'])})
                                                if addressString not in data:
                                                        with open("log.txt", "a") as myfile:
                                                             myfile.write(addressString + ' : ' + str(balance['amount']))
                                                             print(addressString + ' : ' + str(balance['amount']))

with open('balances.csv', 'w') as file:
        w = csv.writer(file)
        w.writerows(data.items())

sys.exit()
