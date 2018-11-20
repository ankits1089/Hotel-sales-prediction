from dataset_creator_functions import *
import pickle

demand_data_training = pd.read_csv('/Users/ankitsrivastava/Documents/Sales prediction assignment/data_000.csv',header=None,
		names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])
date_parsing_fn(demand_data_training)

txn_data_training = pd.read_csv('/Users/ankitsrivastava/Documents/Sales prediction assignment/data_000 2.csv',header=None,
	names=['bookingdate', 'hotelid', 'cityid', 'checkin', 'checkout', 'flavour', 'num_rooms', 'userid'])

######## booking data aggregation commands

hotel_list = list(txn_data_training['hotelid'].unique())

booking_aggregated = txn_data_aggregator(txn_data_training, hotel_list)

######## demand data aggregation commmands

demand_data_aggregator(booking_aggregated,demand_data_training)

######## compilation of booking and demand data commands

with open('agg_city_var.pickle', 'rb') as handle:
	city_df = pickle.load(handle)

with open('agg_hotel_var.pickle', 'rb') as handle:
	hotel_df = pickle.load(handle)

txn_demand_data_compiler(booking_aggregated, city_df, hotel_df)
