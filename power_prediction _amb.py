import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
import pprint
import time
from time import sleep
import random
import datetime
import glob
import MySQLdb

db = MySQLdb.connect(host="localhost", user="root", passwd="", db="prediction_amb")
cur = db.cursor()

def listToString(s):
    # initialize an empty string
    str1 = "" 
    # traverse in the string  
    for ele in s:
        str1 += ele
    # return string  
    return str1

while True:
    def fxn():
        warnings.warn("deprecated", DeprecationWarning)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fxn()

    df = pd.read_csv(r"C:\Users\pakiy\Downloads\Ambattur 2016-2020.csv")
    df = df.fillna(0)
    nonzero_mean = df[df != 0].mean()

    cols = [0, 1, 2, 3, 4]
    X = df[df.columns[cols]].values

    cols = [5]
    Y_temp = df[df.columns[cols]].values

    cols = [6]
    Y_ghi = df[df.columns[cols]].values

    from sklearn.model_selection import train_test_split
    x_train, x_test, y_temp_train, y_temp_test = train_test_split(X, Y_temp, random_state=42)
    x_train, x_test, y_ghi_train, y_ghi_test = train_test_split(X, Y_ghi, random_state=42)

    # Convert y to 1D array to avoid warnings
    y_temp_train = y_temp_train.ravel()
    y_temp_test = y_temp_test.ravel()
    y_ghi_train = y_ghi_train.ravel()
    y_ghi_test = y_ghi_test.ravel()

    from sklearn.ensemble import RandomForestRegressor

    rfc1 = RandomForestRegressor()
    rfc2 = RandomForestRegressor()

    rfc1.fit(x_train, y_temp_train)
    rfc2.fit(x_train, y_ghi_train)

    time_now = datetime.datetime.now() + datetime.timedelta(minutes=15)
    time_str = time_now.strftime("%Y-%m-%d %H:%M")
    print(time_str)

    next_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
    now = next_time.strftime("%Y,%m,%d,%H,%M")
    now = now.split(",")
    now = list(map(int, now))
    print(now)
    temp = rfc1.predict([now])
    ghi = rfc2.predict([now])

    f = 0.18 * 7.4322 * ghi
    insi = temp - 25
    midd = 0.95 * insi

    power = f * midd
    power = power.tolist()
    power = ''.join(map(str, power))
    power = float(power)
    print("Power: ", power)
    print(type(power))

    temp = temp.tolist()
    temp = ''.join(map(str, temp))
    temp = float(temp)
    print("Temperature:", temp)
    ghi = ghi.tolist()
    ghi = ''.join(map(str, ghi))
    ghi = float(ghi)
    print("GHI:", ghi)
    print(type(ghi), type(temp))

    sql = ("""INSERT INTO power_prediction (time_updated, Temperature, GHI, power) VALUES (%s, %s, %s, %s)""", (time_str, temp, ghi, power))

    try:
        print("Writing to the database...")
        cur.execute(*sql)
        db.commit()
        print("Write complete")
    except:
        db.rollback()
        print("We have a problem")

    import time
    time.sleep(1)
