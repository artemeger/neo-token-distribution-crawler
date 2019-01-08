from requests import Session
import time
import datetime
import sys
import csv

attemptLimit = 10
urlString = 'http://state-api.otcgo.cn/api/v1/mainnet/public/graphql'
sessionHead = 'http://state-api.otcgo.cn'
sessionHeadGet = 'https://api.neoscan.io'
tokenHash = '45d493a6f73fa5f404244a5fb8472fc014ca5885'
stakeThreshhold = 20000

sessionGet = Session()
sessionGet.head(sessionHeadGet)

session = Session()
session.head(sessionHead)

headerDict = dict()
headerDict.update({'Address' : 'Stake'})
with open('balances2.csv', 'w') as file:
	w = csv.writer(file)
	w.writerows(headerDict.items())

def getBalance(url, addressString, attempt):
	reqJson = sessionGet.get(url, headers={'Referer': sessionHeadGet})
	if tokenHash in reqJson.text:
		try:
			dataJson = reqJson.json()
			for balance in dataJson['balance']:
				if balance['asset_hash'] == tokenHash and float(balance['amount'] >= stakeThreshhold):
					print(addressString + ' : ' + str(balance['amount']))
					with open('balances2.csv', 'a') as file:
						dataDict = dict()
						w = csv.writer(file)
						dataDict.update({addressString : str(balance['amount'])})
						w.writerows(dataDict.items())
					break
		except:
			if attempt <= attemptLimit:
				print('Error... will retry')
				time.sleep(1)
				getBalance(url, addressString, attempt + 1)
			else:
				print('Attempt limit reached. Will abort.')
#get address count
payloadCount = {'query':'{SystemQuery{rows {addressNum}}}'}
responseCount = session.post(
	url = urlString,
	data = payloadCount,
	headers={'Referer': urlString}
)
count = int(responseCount.json()['data']['SystemQuery']['rows']['addressNum'])

#comment that in if you want a fixed count
#count = 200

print('There are ' + str(count) + ' addresses to fetch. This will take some time')

#get all addresses
payloadAddresses = {'query':'{AddressQuery (skip:1 limit:' + str(count)+'){rows {address}}}'}
responseAddresses = session.post(
	url = urlString,
	data = payloadAddresses,
	headers={'Referer': urlString}
)

row = responseAddresses.json()['data']['AddressQuery']['rows']

counter = 0
#lookup every address
for address in row:
	addressString = address['address']
	addressUrl = 'https://api.neoscan.io/api/main_net/v1/get_balance/' + addressString
	getBalance(addressUrl, addressString, 0)
	if counter % 100 == 1:
		print('Finished: ' + str(round((counter/count * 100) , 2)) +'%' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
	counter += 1

print('Finished: 100%')
sys.exit()
