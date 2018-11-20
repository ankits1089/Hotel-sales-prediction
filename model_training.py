import pandas as pd
import numpy as np
import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn import model_selection
from sklearn import metrics
import pickle
import xgboost


def model_fit (algorithm, X , y , evaluation_fn):
    
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)

    algorithm.fit(x_train, y_train)
    y_predicted = algorithm.predict(x_test)
    y_predicted = np.round(y_predicted)
    y_predicted =[each if each > 0 else 0 for each in y_predicted]
    
    score = evaluation_fn(y_test, y_predicted)
    print("score :",score[0])

def model_evaluation(y_true, y_pred):
	a=np.array((y_true))
	b= np.array(y_pred)
	diff = np.absolute(a-b)
	first = 0
	second = 0
	for each in diff:
		if int(each) <= 1:
			first+=1
		elif int(each) > 1 and int(each)<=5:
			second+=1
	total = float(len(a))
	result = [np.round(first/total*100,2), np.round(second/total*100,2), np.round((total-(first+second))/total*100,2)]
	print('percentage prediction with error of atmost 1 rooms: ',result[0])
	print('percentage prediction with error of 2-5 rooms: ', result[1])
	print('percentage prediction with error of more than 5 rooms: ', result[2])
	return result

if __name__ == '__main__':

	data = pd.read_csv('/Users/ankitsrivastava/Documents/Sales prediction assignment/model/final_data.csv',header=0)

	df = data
	df = df.loc[:,'rooms_booked':list(data.columns)[-1:][0]]

	y = df['rooms_booked']
	X = df[[each for each in df.columns if each != 'rooms_booked']]

	reg = LinearRegression()
	
	model_fit(reg, X, y, model_evaluation)
	
	with open('model.pickle', 'wb') as handle:
		pickle.dump(reg, handle, protocol=pickle.HIGHEST_PROTOCOL)




