import pandas as pd
import numpy as np
import csv
import datetime
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn import tree
from sklearn.neural_network import MLPRegressor

# 训练数据集时间跨度为145day,测试数据集跨度为37day
# training:[2016-02-01 / 2016-06-24]
# testing:[2016-06-25 / 2016-07-31]

pluno_key = [22, 23, 25, 27]
data = pd.read_csv('new_trade.csv')
feature_i = pd.read_csv('feature_i.csv')
feature_iv = pd.read_csv('feature_iv.csv')
feature_ii = pd.read_csv('feature_ii.csv')
feature_v = pd.read_csv('feature_v.csv')
feature_iii = pd.read_csv('feature_iii.csv')
feature_vi = pd.read_csv('feature_vi.csv')


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


def is_weekday(date_str):
    date = datetime.datetime.strptime(date_str,'%Y-%m-%d').weekday()
    if date + 1 < 6:
        return True
    else:
        return False


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


def get_pluno_level_dict(lev):
    dicts = {}
    date_list = get_date_list()
    # 遍历源数据
    for index, row in data.iterrows():
        pluno = int(row['pluno'] / lev)
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


def get_bndno_dict():
    dicts = {}
    date_list = get_date_list()
    # 遍历源数据
    for index, row in data.iterrows():
        bndno = int(row['pluno'] / 1000)
        date_str = row['sldatime'][0:10]
        qty = row['qty']
        if bndno in dicts:
            dicts[bndno][date_str] += qty
        else:
            dicts[bndno] = {}
            for date in date_list:
                if date_str == date:
                    dicts[bndno][date_str] = qty
                else:
                    dicts[bndno][date] = 0.0
    return dicts


def last_week_list(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    week_list = []
    i = 0
    while i < 7:
        time = date - datetime.timedelta(days= (i + 1))
        date_time = datetime.datetime.strftime(time,'%Y-%m-%d')
        week_list.append(date_time)
        i += 1
    return week_list


def past_week_list(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    week_list = []
    weeks = []
    i = 7
    while i < 28:
        time = date - datetime.timedelta(days= (i + 1))
        date_time = datetime.datetime.strftime(time,'%Y-%m-%d')
        week_list.append(date_time)
        if (i + 1) % 7 == 0:
            weeks.append(week_list)
            week_list = []
        i += 1
    return weeks


def forecast_i():
    training_start = datetime.datetime.strptime('2016-02-08', '%Y-%m-%d')
    training_end = datetime.datetime.strptime('2016-06-25', '%Y-%m-%d')
    test_end = datetime.datetime.strptime('2016-07-25', '%Y-%m-%d')
    mindate = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
    # 设置训练集和测试集
    training_x = []
    training_y = []
    test_x = []
    test_y = []
    result = []
    for index, row in feature_i.iterrows():
        date_str = row['sldatime']
        date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        row['sldatime'] = (date_time - mindate).days
        if training_start < date_time < training_end:
            i = 0
            training_list = []
            while i < len(row):
                training_list.append(row[i])
                i += 1
            training_x.append(training_list)
            training_y.append(row['qty'])
        else:
            # 最后6天的测试数据不要
            if date_time < test_end:
                i = 0
                test_list = []
                while i < len(row):
                    test_list.append(row[i])
                    i += 1
                test_x.append(test_list)
                test_y.append(row['qty'])
    # 初始化result
    le = 0
    while le < len(test_x):
        result.append([])
        result[le].append(test_x[le][0])
        result[le].append(test_x[le][6])
        result[le].append(test_x[le][8] / 1000)
        le += 1
    # 预测7天的销量
    history_dict = get_pluno_dict()
    day = 0
    while day < 7:
        # 预测
        # clf = RandomForestClassifier()
        # linear,poly,rbf
        # clf = SVR(kernel="poly")
        # clf = tree.DecisionTreeClassifier(criterion='entropy')
        clf = MLPRegressor()
        clf.fit(training_x, training_y)
        predict_y = clf.predict(test_x)
        index = 0
        while index < len(test_x):
            # 将预测结果保存到结果数组中
            result[index].append(predict_y[index] / 1000)
            pluno = test_x[index][0]
            date_str = datetime.datetime.strftime(mindate + datetime.timedelta(days=test_x[index][6]), '%Y-%m-%d')
            test_x[index][8] = predict_y[index]
            # 将预测结果添加到训练集中
            # 预测d的销量其他特征不需要更新
            if day == 0:
                training_x.append(test_x[index])
                training_y.append(int(test_x[index][8]))
            if day > 0:
                # 更新时间序列字典
                history_dict[pluno][date_str] += predict_y[index]
                rec = test_x[index]
                # 更新特征d-1/d-7
                j = 0
                lastweek = last_week_list(date_str)
                for date in lastweek:
                    min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                    this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                    if this_date > min_date:
                        rec[9 + j] = history_dict[pluno][date]
                    else:
                        rec[9 + j] = 0.0
                    j += 1
                training_x.append(rec)
                training_y.append(int(rec[8]))
            index += 1
        # 更新测试集日期进行下一次预测
        i = 0
        while i < len(test_x):
            interval = test_x[i][6]
            test_x[i][6] += 1
            str = datetime.datetime.strftime(mindate + datetime.timedelta(days=interval), '%Y-%m-%d')
            if is_weekday(str):
                test_x[i][7] = 1
            else:
                test_x[i][7] = 0
            i += 1
        day += 1
    # 将预测结果写入csv
    head = ['pluno', 'time', 'qty', 'd', 'd+1', 'd+2', 'd+3', 'd+4', 'd+5', 'd+6']
    # 创建文件对象
    path = "MLP/forecast_i.csv"
    f = open(path, 'w', encoding='utf-8', newline='' "")
    # 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 构建列表头
    csv_writer.writerow(head)
    # 创建每一行数据
    for row in result:
        csv_writer.writerow(row)
    # 关闭文件
    f.close()


def forecast_i_iv():
    # 划分训练集和测试集的时间节点
    training_end = datetime.datetime.strptime('2016-06-25', '%Y-%m-%d')
    training_start = datetime.datetime.strptime('2016-02-29', '%Y-%m-%d')
    test_end = datetime.datetime.strptime('2016-07-25', '%Y-%m-%d')
    start = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
    all_data = []  # 存储合并之后的特征工程
    training_x = []
    training_y = []
    test_x = []
    test_y = []
    # 首先合并特征工程
    for i, row in feature_i.iterrows():
        row['sldatime'] = (datetime.datetime.strptime(row['sldatime'], '%Y-%m-%d') - start).days
        all_data.append([])
        j = 0
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_iv.iterrows():
        j = 0
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    # 划分训练集和测试集
    for row in all_data:
        time = start + datetime.timedelta(days=row[6])
        if training_start < time < training_end:
            training_x.append(row)
            training_y.append(row[8])
        elif training_end < time < test_end:
            test_x.append(row)
            test_y.append(row[8])
    # 初始化result
    result = []
    id = 0
    while id < len(test_x):
        result.append([])
        result[id].append(test_x[id][0])
        result[id].append(test_x[id][6])
        result[id].append(test_x[id][8] / 1000)
        id += 1
    history_dict = get_pluno_dict()
    # 重复预测7次
    day = 0
    while day < 7:
        # 预测
        # clf = RandomForestClassifier()
        # linear,poly,rbf
        # clf = SVR(kernel="poly")
        # clf = tree.DecisionTreeClassifier(criterion='entropy')
        clf = MLPRegressor()
        clf.fit(training_x, training_y)
        predict_y = clf.predict(test_x)
        i = 0
        while i < len(test_x):
            # 保存到结果字典result中
            pluno = test_x[i][0]
            date_str = datetime.datetime.strftime(start + datetime.timedelta(days=test_x[i][6]), '%Y-%m-%d')
            test_x[i][8] = predict_y[i]
            result[i].append(predict_y[i] / 1000)
            # 当预测的是当天时，其他特征量不用更新，直接添加到训练集中即可
            if day == 0:
                training_x.append(test_x[i])
                training_y.append(test_x[i][8])
            if day > 0:
                # 更新时间序列字典
                history_dict[pluno][date_str] += predict_y[i]
                rec = test_x[i]
                # 更新特征量d-1/d-7
                j = 0
                lastweek = last_week_list(date_str)
                for date in lastweek:
                    min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                    this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                    if this_date > min_date:
                        rec[9 + j] = history_dict[pluno][date]
                    else:
                        rec[9 + j] = 0.0
                    j += 1
                # 更新avg、max、min
                week_list = past_week_list(date_str)
                avg = 0.0
                max = 0.0
                min = float('inf')
                week_index = 0
                # 遍历前2、3、4周
                for week in week_list:
                    # 遍历一周中的每一天
                    for date in week:
                        min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                        this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                        if this_date > min_date:
                            avg += history_dict[pluno][date]
                            if history_dict[pluno][date] > max:
                                max = history_dict[pluno][date]
                            if history_dict[pluno][date] < min:
                                min = history_dict[pluno][date]
                        else:
                            min = 0.0
                    avg = avg / 7
                    rec[16 + 3 * week_index] = avg
                    rec[17 + 3 * week_index] = max
                    rec[18 + 3 * week_index] = min
                    avg = 0.0
                    max = 0.0
                    min = float('inf')
                    week_index += 1
                #     更新所有特征量添加到训练集中
                training_x.append(rec)
                training_y.append(rec[8])
            i += 1
        # 更新日期进行下次预测
        for row in test_x:
            row[6] += 1
            date = datetime.datetime.strftime(start + datetime.timedelta(days=row[6]), '%Y-%m-%d')
            if is_weekday(date):
                row[7] = 1
            else:
                row[7] = 0
        day += 1
    # 将预测结果写入csv
    head = ['pluno', 'time', 'qty', 'd', 'd+1', 'd+2', 'd+3', 'd+4', 'd+5', 'd+6']
    # 创建文件对象
    path = "MLP/forecast_i_iv.csv"
    f = open(path, 'w', encoding='utf-8', newline='' "")
    # 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 构建列表头
    csv_writer.writerow(head)
    # 创建每一行数据
    for row in result:
        csv_writer.writerow(row)
    # 关闭文件
    f.close()


def forecast_i_ii_iv_v():
    training_end = datetime.datetime.strptime('2016-06-25', '%Y-%m-%d')
    training_start = datetime.datetime.strptime('2016-02-29', '%Y-%m-%d')
    test_end = datetime.datetime.strptime('2016-07-25', '%Y-%m-%d')
    start = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
    all_data = []
    training_x = []
    training_y = []
    test_x = []
    test_y = []
    # 首先合并特征工程
    for i, row in feature_i.iterrows():
        row['sldatime'] = (datetime.datetime.strptime(row['sldatime'], '%Y-%m-%d') - start).days
        all_data.append([])
        j = 0
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_iv.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_ii.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_v.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    # 首先划分训练集和测试集
    for row in all_data:
        time = start + datetime.timedelta(days=row[6])
        if training_start < time < training_end:
            training_x.append(row)
            training_y.append(row[8])
        elif training_end < time < test_end:
            test_x.append(row)
            test_y.append(row[8])
    # 重复预测7次
    result = []
    id = 0
    # 初始化result
    while id < len(test_x):
        result.append([])
        result[id].append(test_x[id][0])
        result[id].append(test_x[id][6])
        result[id].append(test_x[id][8] / 1000)
        id += 1
    history_dict = get_pluno_dict()
    bndno_dict = get_bndno_dict()
    day = 0
    while day < 7:
        # 预测
        # clf = RandomForestClassifier()
        # linear,poly,rbf
        # clf = SVR(kernel="poly")
        # clf = tree.DecisionTreeClassifier(criterion='entropy')
        clf = MLPRegressor()
        clf.fit(training_x, training_y)
        predict_y = clf.predict(test_x)
        i = 0
        while i < len(test_x):
            # 保存到结果字典result中
            pluno = test_x[i][0]
            bndno = int(pluno / 1000)
            date_str = datetime.datetime.strftime(start + datetime.timedelta(days=test_x[i][6]), '%Y-%m-%d')
            test_x[i][8] = predict_y[i]
            result[i].append(predict_y[i] / 1000)
            if day == 0:
                training_x.append(test_x[i])
                training_y.append(test_x[i][8])
            # 从未来第一天开始更新
            if day > 0:
                # 更新时间序列字典
                history_dict[pluno][date_str] += predict_y[i]
                bndno_dict[bndno][date_str] += predict_y[i]
                rec = test_x[i]
                # 更新d-1/d-7
                j = 0
                lastweek = last_week_list(date_str)
                for date in lastweek:
                    min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                    this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                    if this_date > min_date:
                        rec[9 + j] = history_dict[pluno][date]
                        rec[25 + j] = bndno_dict[bndno][date]
                    else:
                        rec[9 + j] = 0.0
                        rec[25 + j] = 0.0
                    j += 1
                # 更新avg、max、min
                week_list = past_week_list(date_str)
                avg_pluno = avg_bndno = 0.0
                max_pluno = max_bndno =0.0
                min_pluno = min_bndno = float('inf')
                week_index = 0
                for week in week_list:
                    for date in week:
                        min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                        this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                        if this_date > min_date:
                            avg_pluno += history_dict[pluno][date]
                            avg_bndno += bndno_dict[bndno][date]
                            if history_dict[pluno][date] > max_pluno:
                                max_pluno = history_dict[pluno][date]
                            if bndno_dict[bndno][date] > max_bndno:
                                max_bndno = bndno_dict[bndno][date]
                            if history_dict[pluno][date] < min_pluno:
                                min_pluno = history_dict[pluno][date]
                            if bndno_dict[bndno][date] < min_bndno:
                                min_bndno = bndno_dict[bndno][date]
                        else:
                            min_pluno = 0.0
                            min_bndno = 0.0
                    avg_pluno = avg_pluno / 7
                    avg_bndno = avg_bndno / 7
                    rec[16 + 3 * week_index] = avg_pluno
                    rec[17 + 3 * week_index] = max_pluno
                    rec[18 + 3 * week_index] = min_pluno
                    rec[32 + 3 * week_index] = avg_bndno
                    rec[33 + 3 * week_index] = max_bndno
                    rec[34 + 3 * week_index] = min_bndno
                    avg_pluno = avg_bndno = 0.0
                    max_pluno = max_bndno = 0.0
                    min_pluno = min_bndno = float('inf')
                    week_index += 1
                training_x.append(rec)
                training_y.append(rec[8])
            i += 1
        # 更新日期
        for row in test_x:
            row[6] += 1
            date = datetime.datetime.strftime(start + datetime.timedelta(days=row[6]), '%Y-%m-%d')
            if is_weekday(date):
                row[7] = 1
            else:
                row[7] = 0
        day += 1
    # 将预测结果写入csv
    head = ['pluno', 'time', 'qty', 'd', 'd+1', 'd+2', 'd+3', 'd+4', 'd+5', 'd+6']
    # 创建文件对象
    path = "MLP/forecast_i_ii_iv_v.csv"
    f = open(path, 'w', encoding='utf-8', newline='' "")
    # 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 构建列表头
    csv_writer.writerow(head)
    # 创建每一行数据
    for row in result:
        csv_writer.writerow(row)
    # 关闭文件
    f.close()


def forecast_all():
    training_end = datetime.datetime.strptime('2016-06-25', '%Y-%m-%d')
    training_start = datetime.datetime.strptime('2016-02-29', '%Y-%m-%d')
    test_end = datetime.datetime.strptime('2016-07-25', '%Y-%m-%d')
    start = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
    all_data = []
    training_x = []
    training_y = []
    test_x = []
    test_y = []
    # 首先合并特征工程
    for i, row in feature_i.iterrows():
        row['sldatime'] = (datetime.datetime.strptime(row['sldatime'], '%Y-%m-%d') - start).days
        all_data.append([])
        j = 0
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_iv.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_ii.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_v.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_iii.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    for i, row in feature_vi.iterrows():
        j = 1
        while j < len(row):
            all_data[i].append(row[j])
            j += 1
    # 首先划分训练集和测试集
    for row in all_data:
        time = start + datetime.timedelta(days=row[6])
        if training_start < time < training_end:
            training_x.append(row)
            training_y.append(row[8])
        elif training_end < time < test_end:
            test_x.append(row)
            test_y.append(row[8])
    # 重复预测7次
    result = []
    id = 0
    # 初始化result
    while id < len(test_x):
        result.append([])
        result[id].append(test_x[id][0])
        result[id].append(test_x[id][6])
        result[id].append(test_x[id][8] / 1000)
        id += 1
    history_dict = get_pluno_dict()
    bndno_dict = get_bndno_dict()
    pluno_level_dict = [get_pluno_level_dict(1000), get_pluno_level_dict(10000),
                        get_pluno_level_dict(100000), get_pluno_level_dict(1000000)]
    day = 0
    while day < 7:
        # 预测
        # clf = RandomForestClassifier()
        # linear,poly,rbf
        # clf = SVR(kernel="poly")
        # clf = tree.DecisionTreeClassifier(criterion='entropy')
        clf = MLPRegressor()
        clf.fit(training_x, training_y)
        predict_y = clf.predict(test_x)
        print("predict ok")
        i = 0
        while i < len(test_x):
            # 保存到结果字典result中
            pluno = test_x[i][0]
            bndno = int(pluno / 1000)
            pluno_level = [int(pluno / 1000), int(pluno / 10000), int(pluno / 100000), int(pluno / 1000000)]
            date_str = datetime.datetime.strftime(start + datetime.timedelta(days=test_x[i][6]), '%Y-%m-%d')
            test_x[i][8] = predict_y[i]
            result[i].append(predict_y[i] / 1000)
            if day == 0:
                training_x.append(test_x[i])
                training_y.append(test_x[i][8])
            # 从未来第一天开始更新
            if day > 0:
                # 更新时间序列字典
                history_dict[pluno][date_str] += predict_y[i]
                bndno_dict[bndno][date_str] += predict_y[i]
                lev = 0
                while lev < 4:
                    id = pluno_level[lev]
                    pluno_level_dict[lev][id][date_str] += predict_y[i]
                    lev += 1
                rec = test_x[i]
                # 更新d-1/d-7
                j = 0
                lastweek = last_week_list(date_str)
                for date in lastweek:
                    min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                    this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                    if this_date > min_date:
                        rec[9 + j] = history_dict[pluno][date]
                        rec[25 + j] = bndno_dict[bndno][date]
                        rec[41 + j] = pluno_level_dict[0][pluno_level[0]][date]
                        rec[48 + j] = pluno_level_dict[1][pluno_level[1]][date]
                        rec[55 + j] = pluno_level_dict[2][pluno_level[2]][date]
                        rec[62 + j] = pluno_level_dict[3][pluno_level[3]][date]
                    else:
                        rec[9 + j] = 0.0
                        rec[25 + j] = 0.0
                        rec[41 + j] = 0.0
                        rec[48 + j] = 0.0
                        rec[55 + j] = 0.0
                        rec[62 + j] = 0.0
                    j += 1
                # 更新avg、max、min
                week_list = past_week_list(date_str)
                avg_pluno = avg_bndno = 0.0
                max_pluno = max_bndno =0.0
                min_pluno = min_bndno = float('inf')
                week_index = 0
                for week in week_list:
                    for date in week:
                        min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                        this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                        if this_date > min_date:
                            avg_pluno += history_dict[pluno][date]
                            avg_bndno += bndno_dict[bndno][date]
                            if history_dict[pluno][date] > max_pluno:
                                max_pluno = history_dict[pluno][date]
                            if bndno_dict[bndno][date] > max_bndno:
                                max_bndno = bndno_dict[bndno][date]
                            if history_dict[pluno][date] < min_pluno:
                                min_pluno = history_dict[pluno][date]
                            if bndno_dict[bndno][date] < min_bndno:
                                min_bndno = bndno_dict[bndno][date]
                        else:
                            min_pluno = 0.0
                            min_bndno = 0.0
                    avg_pluno = avg_pluno / 7
                    avg_bndno = avg_bndno / 7
                    rec[16 + 3 * week_index] = avg_pluno
                    rec[17 + 3 * week_index] = max_pluno
                    rec[18 + 3 * week_index] = min_pluno
                    rec[32 + 3 * week_index] = avg_bndno
                    rec[33 + 3 * week_index] = max_bndno
                    rec[34 + 3 * week_index] = min_bndno
                    avg_pluno = avg_bndno = 0.0
                    max_pluno = max_bndno = 0.0
                    min_pluno = min_bndno = float('inf')
                    week_index += 1
                avg = 0.0
                max = 0.0
                min = float('inf')
                start_index = 69
                lev = 0
                while lev < 4:
                    pluno_dict = pluno_level_dict[lev]
                    pluno_index = pluno_level[lev]
                    week_index = 0
                    for week in week_list:
                        for date in week:
                            min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                            this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                            if this_date > min_date:
                                avg += pluno_dict[pluno_index][date]
                                if pluno_dict[pluno_index][date] > max:
                                    max = pluno_dict[pluno_index][date]
                                if pluno_dict[pluno_index][date] < min:
                                    min = pluno_dict[pluno_index][date]
                            else:
                                min = 0.0
                            avg = avg / 7
                        rec[start_index + 3 * week_index] = avg
                        rec[start_index + 1 + 3 * week_index] = max
                        rec[start_index + 2 + 3 * week_index] = min
                        avg = 0.0
                        max = 0.0
                        min = float('inf')
                        week_index += 1
                    start_index += 9
                    lev += 1
                training_x.append(rec)
                training_y.append(rec[8])
            i += 1
        # 更新日期
        for row in test_x:
            row[6] += 1
            date = datetime.datetime.strftime(start + datetime.timedelta(days=row[6]), '%Y-%m-%d')
            if is_weekday(date):
                row[7] = 1
            else:
                row[7] = 0
        print(day)
        day += 1
    # 将预测结果写入csv
    head = ['pluno', 'time', 'qty', 'd', 'd+1', 'd+2', 'd+3', 'd+4', 'd+5', 'd+6']
    # 创建文件对象
    path = "MLP/forecast_all.csv"
    f = open(path, 'w', encoding='utf-8', newline='' "")
    # 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 构建列表头
    csv_writer.writerow(head)
    # 创建每一行数据
    for row in result:
        csv_writer.writerow(row)
    # 关闭文件
    f.close()


def RSE():
    result = pd.read_csv('MLP/forecast_all.csv')
    # result_i_iv = pd.read_csv('DecisionTree_forecast_i_iv.csv')
    # result_i_ii_iv_v = pd.read_csv('RandomForest_forecast_i_ii_iv_v.csv')
    # result_all = pd.read_csv('MLP_forecast_all.csv')
    mean_y = 0
    count = 0
    for index, row in result.iterrows():
        mean_y += row['qty']
        count += 1
    mean_y /= count
    top = bot = 0
    for index, row in result.iterrows():
        top += np.square(row['d'] - row['qty'])
        bot += np.square(row['qty'] - mean_y)
    if bot == 0:
        print("no way!")
        res = float('inf')
    else:
        top = np.sqrt(top)
        bot = np.sqrt(bot)
        res = top / bot
    print(res)


if __name__ == '__main__':
    forecast_i()
    forecast_i_iv()
    forecast_i_ii_iv_v()
    forecast_all()
    RSE()
    # lists = []
    # print(len(lists))
    # i = 0
    # error = 0
    # while i < len(predict_Y):
    #     if abs(predict_Y[i] - test_Y[i]) > 0.2:
    #         error += 1
    #     i += 1
    # print(error / len(test_Y))
