import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from one_target.model import build_model


#gets stock data from google finance, excludes some columns, then returns a dataframe
def get_stock_data(stock_name):
    print("GETTING STOCK DATA")
    url = "http://www.google.com/finance/historical?q=" + stock_name + "&startdate=Jul+10%2C+2010&enddate=Jul+27%2C+2017&num=30&ei=rCtlWZGSFN3KsQHwrqWQCw&output=csv"

    col_names = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    stocks = pd.read_csv(url, header=0, names=col_names)
    df = pd.DataFrame(stocks)
    df.drop(df.columns[[0, 3, 5]], axis=1, inplace=True)

    return df




#Loads in stock data from a dataframe and tra
def load_data(stock, seq_len, train_percent=.75):
    data = stock.as_matrix()

    # iterate so that we can also capture a sequence for a target
    sequence_length = seq_len + 1

    print("SPLITTING INTO TIMESERIES")

    # segment the data into timeseries (these will be overlapping)
    result = []
    for index in range(len(data) - sequence_length):
        time_series = data[index: index + sequence_length]
        result.append(time_series[:])

    # normalize
    reference_points = [] # for de-normalizing outside of the function
    for i in range(0, len(result)):
        reference_points.append(result[i][0][0])
        result[i] = (((result[i]) / (result[i][0][0])) - 1)

    result = np.asarray(result)

    # train test split
    print(result.shape[0])
    row = round(train_percent * result.shape[0])
    print(row)
    train = result[:int(row), :]
    test = result[int(row):, :]

    x_train = train[:, :-1]
    y_train = train[:, -1, -1]

    x_test = test[:, :-1]
    y_test = test[:, -1, -1]


    #In case we want to train on percent increase rather than a stock value
    # for i in range(0, len(train_target_timeseries)):
    #     start_price = x_train[i][-1][2]
    #     percent_increase = ((train_target_timeseries[i] - start_price) / start_price) * 100
    #     y_train.append(percent_increase)
    #
    # for i in range(0, len(test_target_timeseries)):
    #     start_price = x_test[i][-1][2]
    #     percent_increase = ((test_target_timeseries[i] - start_price) / start_price) * 100
    #     y_test.append(percent_increase)


    x_train = np.asarray(x_train)
    x_test = np.asarray(x_test)
    y_train = np.asarray(y_train)
    y_test = np.asarray(y_test)

    return [x_train, y_train, x_test, y_test, reference_points]



# MAIN()

stock_name = 'GOOGL'
df = get_stock_data(stock_name)

window = 10
train_percent = .9
X_train, y_train, X_test, y_test, ref = load_data(df[::-1], window, train_percent=train_percent)

print("X_train", X_train.shape)
print("y_train", y_train.shape)
print("X_test", X_test.shape)
print("y_test", y_test.shape)


model = build_model([3, window, 1])

model.fit(
    X_train,
    y_train,
    batch_size=512,
    epochs=1,
    validation_split=0.1,
    verbose=2)


trainScore = model.evaluate(X_train, y_train, verbose=100)
print('Train Score: %.2f MSE (%.2f RMSE) (%.2f)' % (trainScore[0], math.sqrt(trainScore[0]), trainScore[1]))

testScore = model.evaluate(X_test, y_test, verbose=100)
print('Test Score: %.2f MSE (%.2f RMSE) (%.2f)' % (testScore[0], math.sqrt(testScore[0]), testScore[1]))

p = model.predict(X_test)


# document results in file
file = open("rnn_output4.txt", "w")
for i in range(0, len(X_train)):
    for s in range(0, window):
        file.write(str(X_train[i][s]) + "\n")
    file.write("Target: " + str(y_train[i]) + "\n")
    file.write("\n")

for i in range(0, len(X_test)):
    for s in range(0, window):
        file.write(str(X_test[i][s]) + "\n")
    file.write("Target: " + str(y_test[i]) + "\n")
    file.write("Prediction: " + str(p[i]) + "\n")
    file.write("\n")


# de-normalize
print(len(ref))
row = round(train_percent * len(ref))
print(row)
print("reference: " + str(ref[row]))
print("p[0]: " + str(p[0]))
print("y_test[0]: " + str(y_test[0]))
print("prediction: " + str((p[0]+1) * ref[row]))
print("actual: " + str((y_test[0]+1) * ref[row]))
for i in range(0, len(p)):
    p[i] = (p[i] + 1) * ref[row + i]
    y_test[i] = (y_test[i] + 1) * ref[row + i]

# plot
plt.plot(p, color='red', label='prediction')
plt.plot(y_test, color='blue', label='y_test')
plt.legend(loc='upper left')
plt.show()