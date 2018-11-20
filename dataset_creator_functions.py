from init_probe import *
import pickle

def txn_data_aggregator(data, list_hotel_id):

	#### handling dates
	date_parsing_fn(data)
	txn_df = pd.DataFrame()
	print(len(list_hotel_id))
	counter = 0
	for hotel_id in list_hotel_id:
		print(counter)
		txn_data = data_subset_fn(data, 'pass','pass',hotel_id)

		### evaluating min and max checkin date
		min_date = txn_data['checkin'].min().date()
		max_date = txn_data['checkin'].max().date()

		#### creation of all the runing dates
		list_future_dates = []
		list_future_dates.append(min_date)

		next_date = min_date + datetime.timedelta(days = 1)

		while next_date <= max_date:
			list_future_dates.append(next_date)
			next_date += datetime.timedelta(days = 1)

		city_id = txn_data['cityid'].unique()[0]
		df = pd.DataFrame()

		df['Dates'] = list_future_dates
		df['hotelid'] = hotel_id
		df['cityid'] = city_id
		df['rooms_booked'] = 0

		for dates in df['Dates']:
			temp = txn_data[(txn_data['checkin'] <= dates) & (txn_data['checkout']> dates)] 
			if temp.shape[0] > 0:
				df.loc[df['Dates']== dates,'rooms_booked'] = temp['num_rooms'].sum()
		txn_df = txn_df.append(df,ignore_index=True)
		counter+=1
		# df.to_csv('/Users/ankitsrivastava/Documents/Sales prediction assignment/testing2/booking_agg_data.csv',mode = 'a', index=False, header = False)

	return txn_df

def demand_data_aggregator(txn_data_agg, demand_data,flag='training'):

	start_date = txn_data_agg['Dates'].min()
	end_date = txn_data_agg['Dates'].max()

	list_future_dates = []
	list_future_dates.append(start_date)

	next_date = start_date + datetime.timedelta(days = 1)

	while next_date <= end_date:
		list_future_dates.append(next_date)
		next_date += datetime.timedelta(days = 1)

	city_specfic_df = pd.DataFrame()
	hotel_specific_df = pd.DataFrame()
	print(len(list_future_dates))
	counter =0
	for each in list_future_dates:
		print(counter)
		temp_df = data_subset_fn(demand_data,each,'pass','pass')
		df = temp_df.groupby('cityid').userid.agg(['count','nunique']).reset_index()
		df['Dates'] = each
		city_specfic_df = city_specfic_df.append(df,ignore_index=True)
		df = temp_df.groupby('hotelid').userid.agg(['count','nunique']).reset_index()
		df['Dates'] = each
		hotel_specific_df = hotel_specific_df.append(df,ignore_index=True)
		counter+=1

	if flag != 'training':
		string = '_pred' 
	else:
		string = ''
	
	with open('agg_city_var'+string+'.pickle','wb') as handle:
		pickle.dump(city_specfic_df, handle, protocol=pickle.HIGHEST_PROTOCOL)

	with open('agg_hotel_var'+string+'.pickle','wb') as handle:
		pickle.dump(hotel_specific_df, handle, protocol=pickle.HIGHEST_PROTOCOL)


def txn_demand_data_compiler(txn_data_agg, city_var_df, hotel_var_df, flag ='training'):

	cols = list(city_var_df.columns)
	cols = cols[-1:] +cols[:-1]
	city_var_df = city_var_df[cols]
	city_var_df.rename(columns ={'count':'city_search','nunique':'user_fr_city'}, inplace=True)

	cols = list(hotel_var_df.columns)
	cols = cols[-1:] +cols[:-1]
	hotel_var_df = hotel_var_df[cols]
	hotel_var_df.rename(columns ={'count':'hotel_search','nunique':'user_fr_hotel'}, inplace=True)

	result = pd.merge(txn_data_agg,city_var_df,how = 'left', on=['Dates','cityid'])

	result = pd.merge(result,hotel_var_df,how = 'left', on=['Dates','hotelid'])

	result['day_of_week'] = result['Dates'].astype('datetime64[D]').dt.weekday

	#### getting max rooms booked

	df = result.groupby('hotelid').rooms_booked.max().reset_index()
	df.rename(columns={'rooms_booked': 'max_room_booked'},inplace=True)
	result = pd.merge(result,df,how = 'left', on=['hotelid'])

	if flag == 'training':
		with open('max_rooms_fr_hotel.pickle','wb') as handle:
			pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)

	#### getting average rooms booked

	df = result.groupby('hotelid').rooms_booked.mean().reset_index()
	df.rename(columns={'rooms_booked': 'avg_room_booked'},inplace=True)
	result = pd.merge(result,df,how = 'left', on=['hotelid'])

	if flag == 'training':
		with open('avg_rooms_fr_hotel.pickle','wb') as handle:
			pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)


	#### creating dummy variables for city

	city_array = result['cityid'].unique()
	city_modifier =[]
	counter = 1
	for each in city_array:
		new_city = 'city_'+str(counter)
		city_modifier.append([each,new_city])
		counter+=1

	city_modifier = pd.DataFrame(city_modifier)
	city_modifier.columns = ['cityid','new_city']

	if flag == 'training':
		with open('city_lookup.pickle','wb') as handle:
			pickle.dump(city_modifier, handle, protocol=pickle.HIGHEST_PROTOCOL)

	result = pd.merge(result,city_modifier,how = 'left', on=['cityid'])

	result = pd.get_dummies(result, columns = ['new_city'], drop_first = True)

	result.fillna(0, inplace = True)

	if flag != 'training':
		string = '_pred'
	else:
		string = ''

	result.to_csv('/Users/ankitsrivastava/Documents/Sales prediction assignment/model/final_data'+string+'.csv',index=False)

