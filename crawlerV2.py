from requests import Session
import time
import sys

count = 1861800
skip = 0
limit = 100
attemptLimit = 10
urlString = 'http://state-api.otcgo.cn/api/v1/mainnet/public/graphql'
sessionHead = 'http://state-api.otcgo.cn'
sessionHeadGet = 'https://api.neoscan.io'
tokenHash = '45d493a6f73fa5f404244a5fb8472fc014ca5885'
stakeThreshhold = 20000

session = Session()
session.head(sessionHead)
data = dict()

def getBalance(session, url, addressString, attempt):
	reqJson = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
	if tokenHash in reqJson.text:
		try:
			data = reqJson.json()
			for balance in data['balance']:
				if balance['asset_hash'] == tokenHash and float(balance['amount'] >= stakeThreshhold):
					data.update({addressString : str(balance['amount'])})
					print(addressString + ' : ' + str(balance['amount']))
		except:
			if attempt <= attemptLimit:
				print('Error... will retry')
				print(data)
				time.sleep(1)
				getBalance(session, url, addressString, attempt + 1)
			else:
				print('Attempt limit reached. Will abort.')

for iterations in range(0, count, 100):
	print('Finished: ' + str(round((skip/count * 100) , 2)) +'%')
	response = session.post(
		url = urlString,
		data={
			'query': 
			'{'+
				'AddressQuery (skip:' + str(skip) +', limit:' + str(limit) +') {'+
				'count,'+
				'rows {'+
				  ' address '+
				'}'+
			  '}'+
			'}'
		},
		headers={
			'Referer': urlString
		}
	)
	sessionGet = Session()
	sessionGet.head(sessionHeadGet)
	for address in response.json()['data']['AddressQuery']['rows']:
		addressString = address['address']
		addressUrl = 'https://api.neoscan.io/api/main_net/v1/get_balance/' + addressString
		getBalance(sessionGet, addressUrl, addressString, 0)
	skip = skip + 100
	limit = limit + 100

with open('balances.csv', 'w') as file:
	w = csv.writer(file)
	w.writerows(data.items())
	
sys.exit()
