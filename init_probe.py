import pandas as pd
import numpy as np
import datetime
from timeit import default_timer as timer

wd= '/Users/username/Documents/Hotel_sale_pred/'

###### function to parse dates in the given data
def date_parsing_fn (data):
	data['bookingdate'] = data['bookingdate'].astype('datetime64[s]')
	data['checkin'] = data['checkin'].astype('datetime64[D]')
	data['checkout'] = data['checkout'].astype('datetime64[D]')

###### function to print the min max dates in the data
def dates_explorer_displayer(data):
	print('check-in: ',data['checkin'].min(),' - ',data['checkin'].max())
	print('booking date: ', data['bookingdate'].min(),' - ',data['bookingdate'].max())

###### function used to subset data based on the date, hotel and city
def data_subset_fn(data, checkin_date,city = 'pass',hotel = 'pass'):
	temp = data
	if str(checkin_date) != 'pass' :
		date_20days_bfr = checkin_date - datetime.timedelta(days = 20)
		temp = temp[(temp['bookingdate'] <= date_20days_bfr)]
		temp = temp[(temp['checkin'] <= checkin_date) & (temp['checkout']> checkin_date)] 
	if city != 'pass':
		temp = temp[(temp['cityid'] == city)]
	if hotel != 'pass':
		temp = temp[(temp['hotelid'] == hotel)]
	return temp

if __name__ == '__main__':


	#####################
	#### checking summary of the data provided
 	
 	data_demand = pd.read_csv('data_000.csv',header=None,
		names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])
 	date_parsing_fn(data_demand)
	
	data_txn = pd.read_csv('data_000 2.csv',header=None,
		names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])
	date_parsing_fn(data_txn)

	print(data_demand.info())
	print(data_demand.describe())
	print(data_demand.head())
	print(data_demand.dtypes)
	dates_explorer_displayer(data_demand)

	print(data_txn.info())
	print(data_txn.describe())
	print(data_txn.head())
	print(data_txn.dtypes)
	dates_explorer_displayer(data_txn)

	######################
	#### Checking whether the number of unique hotels is equal to the number of unqiue combination of hotel and city 
	#### i.e checking whether same hotelid is present for multiple city or not => False if this is true
	
	hotelid = []
	cityid = []
	with open("data_000.csv") as myfile:
		for line in myfile:
			hotelid.append(line.split(',')[1])
			cityid.append(line.split(',')[2])

	print(len(set(hotelid))==len(set(zip(hotelid,cityid))))

	#######################
	#### checking unique values of flavour

	flavour = []
	with open("data_000.csv") as myfile:
		for line in myfile:
			flavour.append(line.split(',')[5])

	print(set(flavour))

	#######################
	#### subsetting data to write booking data(data_txn) for one single hotel for going easier going through the data in excel

	data_sample_hotel = data_txn[data_txn['hotelid']=='2f53dfc7ce22c4c3a97ad3631a698e1303f84b10']

	data_sample_hotel.to_csv(wd+'sample hotel/txn_one_hotel.csv',index=False)


	#######################
	#### validation demand data and booking data
	#### checking checking min and max date of both checkin and booking date for both txn and demand data

	data_demand = pd.read_csv('validation_demand_data.csv',header=None,
		names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])

	data_txn = pd.read_csv('validation_txn_data.csv',header=None,
		names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])

	date_parsing_fn(data_demand)
	date_parsing_fn(data_txn)

	dates_explorer_displayer(data_demand)
	dates_explorer_displayer(data_txn)

