import requests, datetime, json, re, sys
from random import randint
from geopy.distance import vincenty
from .models import *

# keys
C1_API_KEY = '6a2564321f202a3858b39c09ce0402d1' # Capital One
WA_APP_ID = '73XYQT-HGLXWX3Y79' # Wolfrapm Alpha App ID
G_API_KEY = 'AIzaSyCFok0F3AEK5D22e1RW0WneLtQrHa_y2VM' # Google Maps

machineLearningAPI_URL = 'https://www.open.wolframcloud.com/objects/b805272a-5d33-4a35-b213-1221d1646a43'


def get_account_info(customer_id):
	"""get account id and balance"""
	request_url = 'http://api.reimaginebanking.com/customers/' + customer_id + '/accounts?key=' + C1_API_KEY
	content = requests.get(request_url).json()
	print(content)
	return content[0]['_id'], content[0]['balance']


def get_customer_state_city(customer_id):
	"""get the state and city of a customer"""
	request_url = 'http://api.reimaginebanking.com/customers/' + customer_id + '?key=' + C1_API_KEY
	content = requests.get(request_url).json()
	return content['address']['state'], content['address']['city']


def get_customer_state(customer_id):
	"""get only state"""
	return get_customer_state_city(customer_id)[0]


def get_merchant_list(state, city):
	"""get all merchants in a city and state"""
	request_url = 'http://api.reimaginebanking.com/enterprise/merchants?key=' + C1_API_KEY
	content = requests.get(request_url).json()['results']
	state_list, city_list = [],[]
	for d in content: 
		if 'address' in d: 
			if 'state' in d['address']:
				if d['address']['state'] == state: 
					state_list.append(d)
				if 'city' in d['address']: 
					if d['address']['city'] == city:
						city_list.append(d)
	return state_list, city_list


def load_transactions(customer_id):
	"""load transactions from API and put in db"""
	account_id = get_account_info(customer_id)[0]
	request_url = 'http://api.reimaginebanking.com/accounts/' + account_id + '/purchases?key=' + C1_API_KEY
	content = requests.get(request_url).json()
	profile = Profile.objects.filter(customer_id = customer_id)[0]
	current_balance = profile.balance
	for t in content:
		tr, created = Transaction.objects.get_or_create(t_id = t['_id'], merchant = Merchant.objects.filter(merchant_id = t['merchant_id'])[0], 
					payer = profile, amount = t["amount"])
		if created:
			tr.available_balance = current_balance
			tr.save()
			current_balance -= t["amount"]
			profile.balance = current_balance
	profile.save()


def create_transactions(customer_id, merchant_ids):
	"""Given a list of merchant ids, creates one purchase for each merchant"""
	account_id, account_balance = get_account_info(customer_id)
	request_url = 'http://api.reimaginebanking.com/accounts/' + account_id + '/purchases?key=' + C1_API_KEY
	count = 0
	current_day = 12
	for m_id in merchant_ids:
		if count == 2:
			current_day += 1
			count = 0
		else:
			count += 1
		data = {
		  "merchant_id": m_id,
		  "medium": "balance",
		  "purchase_date": str(datetime.date(2015,9,current_day)),
		  "amount": randint(5, 20), # amount of the purchase is a random int between 5 and 50
		  "status": "completed"
		}

		# submit this as a post request
		r = requests.post(request_url, json.dumps(data), headers = {'content-type': 'application/json'})
		
		print(r.json())

# WARNING: UNDEFINED BEHAVIOR IF UNEMPLOYMENT NUMBERS HAVE NOT COME OUT FOR CURRENT MONTH
def get_data(base_query, split_on, num_months = 12):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	current_month = datetime.datetime.now().month - 1
	current_year = datetime.datetime.now().year

	data = {}

	for i in range(num_months):
		year = str(current_year)
		if current_month - i < 0:
			year = str(current_year - 1)		

		# add month and year to base_query and submit get request
		query = base_query + months[current_month - i] + ' ' + year
		request_url = 'http://api.wolframalpha.com/v2/query?input=' + query + '&appid=' + WA_APP_ID
		r = requests.get(request_url)
		
		# add stuff to dict. example January2014
		data[months[current_month - i] + year] = r.text.split('%')[1][-3:]

	return data

# WARNING: UNDEFINED BEHAVIOR IF UNEMPLOYMENT NUMBERS HAVE NOT COME OUT FOR CURRENT MONTH
def get_unemployment(state):
	return get_data('unemployment ' + state + ' ', 'split("%")[1][-3:]')


def load_merchants(customer_id = '56489490bb8cb2120087e4bd'):
	"""this function loads merchants from a customer's city or state into db.
	default customer id is our customer from Cambridge. adds lat_dec and lng_dec"""
	state, city = get_customer_state_city(customer_id) # our customer from Cambridge
	state_list, city_list = get_merchant_list(state, city)
	
	# pick the appropriate list of merchants (if any in the city, use that)
	merchants = state_list
	if city_list:
		merchants = city_list

	# create merchant objects for every merchant in the list
	for merchant in merchants:
		m = Merchant.objects.get_or_create(merchant_id = merchant['_id'], name = merchant['name'], lat = merchant["geocode"]["lat"], lng = merchant["geocode"]["lng"],
				city = merchant["address"]["city"], state = merchant["address"]["state"])
		m[0].lat_dec = merchant["geocode"]["lat"]
		m[0].lng_dec = merchant["geocode"]["lng"]
		m[0].save()


# assigns each merchant into 0 or more categories: cafe, food, nightlife, grocery, clothing, educational, medical
# each merchant has a string of 7 bits, where if the i-th bit is 1, that means the merchant is in the i-th category (in the order above)
def add_cats(categories):
	"""categories is a list of lists of the indexes of the categories that match
	the corresponding merchant"""
	if Merchant.objects.count() == len(categories):
		c = 0
		for m in Merchant.objects.all():
			temp = ''
			for i in range(7):
				if i in categories[c]:
					temp += '1'
				else:
					temp += '0'
			m.cats = temp
			m.save()
			c += 1


def load_lat_lng(customer_id):
	"""Uses the Google Maps API to get Lat and Lng of user based on address"""
	p = Profile.objects.filter(customer_id = customer_id)
	if len(p) == 1:
		# get customer's address
		request_url = 'http://api.reimaginebanking.com/customers/' + customer_id + '?key=' + C1_API_KEY
		content = requests.get(request_url).json()
		address_dict = content["address"]
		address = address_dict["street_number"] + ' ' + address_dict["street_name"] + ', '
		address += address_dict["city"] + ', ' + address_dict["state"] + address_dict["zip"]	
		
		# request Google Maps and get geolocation
		request_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + G_API_KEY
		content = requests.get(request_url).json()
		geolocation = content['results'][0]['geometry']['location']

		# load into db
		p[0].lat = geolocation['lat']
		p[0].lng = geolocation['lng']
		p[0].lat_dec = geolocation['lat']
		p[0].lng_dec = geolocation['lng']
		p[0].save()


def get_distance(customer_profile, merchant):
	"""calculates the distance between a customer and a merchant"""
	c_geolocation = customer_profile.lat_dec, customer_profile.lng_dec
	m_geolocation = merchant.lat_dec, merchant.lng_dec
	return vincenty(c_geolocation, m_geolocation).miles


# finds recommendations for the user given by customer_id
# WARNING: UNDEFINED BEHAVIOR IF UNEMPLOYMENT NUMBERS HAVE NOT COME OUT FOR CURRENT MONTH
# TODO: toss out transactions with distance from user above 95 percentile
def makeRecommendations(customer_id):
	# make all old recommendations obsolete
	Recommendation.objects.filter(profile__customer_id=customer_id).update(obsolete=True)
	
	# list of recommendations
	recommendations = []
	 
	# create design matrix and response vector
	designMatrix = []
	responseVector = []
	
	# dictionary to store unemployment data that we've already looked up
	unemployment_data = {}
	
	# get all non-medical transactions for user in the last year
	for transaction in Transaction.objects.filter(payer__customer_id=customer_id).exclude(merchant__cats='0000001'):
		if (datetime.date.today() - transaction.date).days <= 365:
			# create current row of design matrix (each transaction gets a row)
			row = []
			# get account balance right before transaction
			row.append(transaction.available_balance+transaction.amount)
			# unemployment rate in user's state for month of transaction
			if transaction.date.strftime("%B")+str(transaction.date.year) in unemployment_data.keys():
				row.append(float(unemployment_data[transaction.date.strftime("%B")+str(transaction.date.year)]))
			else:
				row.append(float(get_unemployment(get_customer_state(transaction.payer.customer_id))[transaction.date.strftime("%B")+str(transaction.date.year)]))
				unemployment_data[transaction.date.strftime("%B")+str(transaction.date.year)] = row[-1]
			# distance from user to merchant
			row.append(get_distance(transaction.payer,transaction.merchant))
			# get the number of transactions involving related but different merchants
			number_related = 0
			for transaction2 in Transaction.objects.filter(payer__customer_id=customer_id).exclude(merchant__cats='0000001',merchant=transaction.merchant):
				if int(transaction.merchant.cats,2)&int(transaction2.merchant.cats,2):
					number_related += 1
			row.append(number_related)
			# find out if user bought from this merchant at least 3 times for the response vector
			if Transaction.objects.filter(payer__customer_id=customer_id,merchant=transaction.merchant).count() >= 5:
				responseVector.append(1)
			else:
				responseVector.append(0)
			# add row to design matrix
			designMatrix.append(row)
	# if we find no transactions that can be used for training, stop
	if designMatrix == [] or responseVector == []:
		sys.exit("There are no transactions that can be used for training.")
	# convert design matrix and response vector to mathematica expressions
	print(designMatrix)
	designMatrixString = '{'
	for row in designMatrix:
		designMatrixString += '{'
		for entry in row:
			designMatrixString += str(entry) + ','
		designMatrixString = designMatrixString[:-1] + '},'
	designMatrixString = designMatrixString[:-1] + '}'
	# now response vector
	print(responseVector)
	responseVectorString = '{'
	for entry in responseVector:
		responseVectorString += str(entry) + ','
	responseVectorString = responseVectorString[:-1] + '}'
	# now iterate over all merchants that the user has never bought from before
	current_unemployment = float(get_unemployment(get_customer_state(customer_id))[datetime.date.today().strftime("%B%Y")]) # store user's unemployment rate to optimize
	for merchant in Merchant.objects.exclude(transactions__in=Transaction.objects.filter(payer__customer_id=customer_id)):
		# create list to store input
		input = []
		# get account balance 
		input.append(Profile.objects.get(customer_id=customer_id).balance)
		# current unemployment rate in user's state 
		input.append(current_unemployment)
		# distance from user to merchant
		input.append(get_distance(Profile.objects.get(customer_id=customer_id),merchant))
		# get the number of transactions involving related but different merchants
		number_related = 0
		for transaction in Transaction.objects.filter(payer__customer_id=customer_id).exclude(merchant__cats='0000001',merchant=merchant):
			if int(merchant.cats,2)&int(transaction.merchant.cats,2):
				number_related += 1
		input.append(number_related)
		# now convert input list to mathematica expression
		inputString = '{'
		for entry in input:
			inputString += str(entry) + ','
		inputString = inputString[:-1] + '}'
		# now use the Wolfram API!
		response = requests.get(machineLearningAPI_URL + '?X=' + designMatrixString + '&Y=' + responseVectorString + '&Input=' + inputString + '&appid=' + WA_APP_ID)
		# if Wolfram throws an error, stop
		if 'API Web Error Report' in response.text or '$Failed' in response.text:
			sys.exit("Inputs were invalid according to Wolfram Alpha.")
		print(re.split('1 -> |\|', response.text))
		answer = re.split('1 -> |\|', response.text)[2]
		answer = answer.split('*^')
		print(answer)
		if len(answer) == 1:
			answer = float(answer[0])
		else:
			answer = float(answer[0]) * 10**float(answer[1])
		if len(recommendations) < 5:
			recommendations.append((merchant,answer))
		elif answer > recommendations[0][1]:
			recommendations[0] = (merchant,answer)
			sorted(recommendations,key=lambda x: x[1])
	# now make recommendations
	for rec in recommendations:
		Recommendation(merchant=rec[0],profile=Profile.objects.get(customer_id=customer_id),score=round(100*rec[1])).save()
