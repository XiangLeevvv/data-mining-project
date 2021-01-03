import pandas as pd
import numpy as np
import datetime
from sklearn.metrics import mean_squared_error


data = pd.read_csv('trade_new.csv')


def min_date():
    mindate = datetime.datetime.now()
    for index, row in data.iterrows():
        date_str = row['sldatime'][0:10]
        date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if date_time < mindate:
            mindate = date_time
    return mindate


def max_date():
    maxdate = min_date()
    for index, row in data.iterrows():
        date_str = row['sldatime'][0:10]
        date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if date_time > maxdate:
            maxdate = date_time
    return maxdate


def get_date_list():
    start_date = min_date()
    end_date = max_date()
    date_list = []
    date_list.append(datetime.datetime.strftime(start_date, '%Y-%m-%d'))
    while start_date < end_date:
        start_date += datetime.timedelta(days=1)
        date_str = datetime.datetime.strftime(start_date, '%Y-%m-%d')
        date_list.append(date_str)
    return date_list


def get_pluno_dict():
    dicts = {}
    date_list = get_date_list()
    # 遍历源数据
    for index, row in data.iterrows():
        pluno = row['pluno']
        date_str = row['sldatime'][0:10]
        qty = row['qty']
        if pluno in dicts:
            dicts[pluno][date_str] += qty
        else:
            dicts[pluno] = {}
            for date in date_list:
                if date_str == date:
                    dicts[pluno][date_str] = qty
                else:
                    dicts[pluno][date] = 0.0
    return dicts


def RSE():
    # SVM DecisionTree RandomForest MLP
    result_i = pd.read_csv('MLP/forecast_i.csv')
    result_i_iv = pd.read_csv('MLP/forecast_i_iv.csv')
    result_i_ii_iv_v = pd.read_csv('MLP/forecast_i_ii_iv_v.csv')
    result_all = pd.read_csv('MLP/forecast_all.csv')
    start = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
    pluno_dict = get_pluno_dict()
    mean_y = 0
    predict_y = []
    true_y = []
    count = 0
    for index, row in result_all.iterrows():
        # 获取预测数据
        i = 3
        while i < len(row):
            predict_y.append(row[i])
            i += 1
        # 获取真实数据
        pluno = row['pluno']
        interval = row['time']
        date_time = start + datetime.timedelta(days=interval)
        end_time = start + datetime.timedelta(days=interval + 6)
        while date_time <= end_time:
            date_str = datetime.datetime.strftime(date_time, '%Y-%m-%d')
            true_y.append(pluno_dict[pluno][date_str])
            date_time += datetime.timedelta(days=1)
        # 计算销量平均值
        mean_y += row['qty']
        count += 1
    mean_y /= count
    # 计算RMSE
    RMSE = np.sqrt(mean_squared_error(true_y, predict_y))
    # 求标准偏差
    Variance = 0
    num = 0
    for index, row in result_all.iterrows():
        Variance += np.square(row['qty'] - mean_y)
        num += 1
    Variance = np.sqrt(Variance / num)
    # 利用公式RSE = RMSE / Variance求解RSE
    if Variance == 0:
        print("no way!")
        res = float('inf')
    else:
        res = RMSE / Variance
    print(res)


if __name__ == '__main__':
    RSE()