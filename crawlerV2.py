from requests import Session
import time
import sys

count = 1861800
skip = 0
limit = 1000
attemptLimit = 10
urlString = 'http://state-api.otcgo.cn/api/v1/mainnet/public/graphql'
sessionHead = 'http://state-api.otcgo.cn'
sessionHeadGet = 'https://api.neoscan.io'
tokenHash = '45d493a6f73fa5f404244a5fb8472fc014ca5885'
stakeThreshhold = 20000

session = Session()
session.head(sessionHead)

sessionGet = Session()
sessionGet.head(sessionHeadGet)

dataDict = dict()

def getBalance(url, addressString, attempt):
	reqJson = sessionGet.get(url, headers={'Referer': sessionHeadGet})
	if tokenHash in reqJson.text:
		try:
			dataJson = reqJson.json()
			for balance in dataJson['balance']:
				if balance['asset_hash'] == tokenHash and float(balance['amount'] >= stakeThreshhold):
					if addressString not in dataDict:
						print(addressString + ' : ' + str(balance['amount']))
					dataDict.update({addressString : str(balance['amount'])})
					break
		except:
			if attempt <= attemptLimit:
				print('Error... will retry')
				time.sleep(1)
				getBalance(url, addressString, attempt + 1)
			else:
				print('Attempt limit reached. Will abort.')

for iterations in range(0, count, 1000):
	print('Finished: ' + str(round((skip/count * 100) , 2)) +'%')
	response = session.post(
		url = urlString,
		data={'query':
				'{'+
				'AddressQuery (skip:' + str(skip) +', limit:' + str(limit) +') {'+
				'count,'+
				'rows {'+
				'address '+
				'}'+
			  '}'+
			'}'
		},
		headers={
			'Referer': urlString
		}
	)
	for address in response.json()['data']['AddressQuery']['rows']:
		addressString = address['address']
		addressUrl = 'https://api.neoscan.io/api/main_net/v1/get_balance/' + addressString
		getBalance(addressUrl, addressString, 0)
	skip = skip + 1000
	limit = limit + 1000

with open('balances.csv', 'w') as file:
	w = csv.writer(file)
	w.writerows(dataDict.items())
	
sys.exit()
