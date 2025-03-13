from dataset_creator_functions import *
from model_training import *
import pickle

##################################################
####### Compiling validation files to create dataset 
##################################################

wd= '/Users/username/Documents/Hotel_sale_pred/'

demand_data_training = pd.read_csv(wd+'validation_demand_data.csv',header=None,
		names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])
date_parsing_fn(demand_data_training)

txn_data_training = pd.read_csv(wd+'validation_txn_data.csv',header=None,
	names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])

######## booking data aggregation commands

hotel_list = list(txn_data_training['hotelid'].unique())

booking_aggregated = txn_data_aggregator(txn_data_training, hotel_list)

######## demand data aggregation commmands

demand_data_aggregator(booking_aggregated,demand_data_training,'prediction')

######## compilation of booking and demand data commands

with open('agg_city_var_pred.pickle', 'rb') as handle:
	city_df = pickle.load(handle)

with open('agg_hotel_var_pred.pickle', 'rb') as handle:
	hotel_df = pickle.load(handle)

txn_demand_data_compiler(booking_aggregated, city_df, hotel_df,'prediction')


####################################################
####### loading model and predicting daily values
####################################################

def dummy_creator(given_str, str_to_find):
	if given_str == str_to_find:
		return 1
	else:
		return 0

data = pd.read_csv(wd+'model/final_data_pred.csv',header=0)

# with open('max_rooms_fr_hotel.pickle', 'rb') as handle:
# 	max_rooms_fr_hotel = pickle.load(handle)

# with open('avg_rooms_fr_hotel.pickle', 'rb') as handle:
# 	avg_rooms_fr_hotel = pickle.load(handle)

with open('city_lookup.pickle', 'rb') as handle:
	city_lookup_df = pickle.load(handle)

city_varibales = []
for each in data.columns:
	if each.find('new_city') != -1:
		city_varibales.append(each)

# data.drop(['max_room_booked', 'avg_room_booked'], axis =1, inplace = True)
data.drop(city_varibales, axis =1, inplace = True)


# data = pd.merge(data,max_rooms_fr_hotel,how = 'left', on=['hotelid'])
# data = pd.merge(data,avg_rooms_fr_hotel,how = 'left', on=['hotelid'])
data = pd.merge(data,city_lookup_df,how = 'left', on=['cityid'])

for each in city_varibales:
	temp = each.replace('new_city_','')
	data[each] = data.new_city.apply(lambda x: dummy_creator(x, temp))

data.drop('new_city', axis =1, inplace = True)

# data.max_room_booked.fillna(max_rooms_fr_hotel['max_room_booked'].mean(),inplace =True)
# data.avg_room_booked.fillna(avg_rooms_fr_hotel['avg_room_booked'].mean(),inplace =True)

df = data
df = df.loc[:,'rooms_booked':list(data.columns)[-1:][0]]

y = df['rooms_booked']
X = df[[each for each in df.columns if each != 'rooms_booked']]

with open('model.pickle', 'rb') as handle:
	model = pickle.load(handle)

predicted = model.predict(X)
predicted = np.round(predicted)
predicted =[each if each > 0 else 0 for each in predicted]

data['rooms_predicted'] = predicted
data = data[['Dates', 'hotelid', 'cityid', 'rooms_booked', 'rooms_predicted']]
result = model_evaluation(data['rooms_booked'],data['rooms_predicted'])
print('score: ',result[0])

data.to_csv(wd+'model/result.csv',index=False)


    