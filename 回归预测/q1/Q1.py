import pandas as pd
import numpy as np
import csv
import datetime


class bndno:
    def __init__(self):
        self.data = pd.read_csv('trade_new.csv')
        self.start_date = ""
        self.end_date = ""

    def min_date(self):
        mindate = datetime.datetime.now()
        for index, row in self.data.iterrows():
            date_str = row['sldatime'][0:10]
            date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            if date_time < mindate:
                mindate = date_time
        return mindate

    def max_date(self):
        maxdate = self.min_date()
        for index, row in self.data.iterrows():
            date_str = row['sldatime'][0:10]
            date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            if date_time > maxdate:
                maxdate = date_time
        return maxdate

    def get_date_list(self):
        start_date = self.min_date()
        end_date = self.max_date()
        date_list = []
        date_list.append('bndno')
        date_list.append(datetime.datetime.strftime(start_date, '%Y-%m-%d'))
        while start_date < end_date:
            start_date += datetime.timedelta(days=1)
            date_str = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            date_list.append(date_str)
        return date_list

    def get_week_list(self):
        date_list = self.get_date_list()
        week_list = []
        week_list.append('bndno')
        # 将天划分为周
        i = 1
        while i < len(date_list):
            if (i % 7) == 1:
                self.start_date = date_list[i]
                # 最后一个周
                if (len(date_list) - i) < 7:
                    self.end_date = date_list[len(date_list) - 1]
                    week = self.start_date + "/" + self.end_date
                    week_list.append(week)
                    break
            elif (i % 7) == 0:
                self.end_date = date_list[i]
                week = self.start_date + "/" + self.end_date
                week_list.append(week)
                self.start_date = ""
                self.end_date = ""
            i += 1
        return week_list

    def get_month_list(self):
        month_list = ['bndno','2016-02-01/2016-02-29','2016-03-01/2016-03-31','2016-04-01/2016-04-30','2016-05-01/2016-05-31'
            ,'2016-06-01/2016-06-30','2016-07-01/2016-07-31']
        return month_list

    def create_bndno_day_csv(self):
        dicts = {}
        mindate = self.min_date()
        date_list = self.get_date_list()
        # 创建文件对象
        path = "bndno_matrix_day.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(date_list)
        # 遍历源数据
        for index, row in self.data.iterrows():
            if np.isnan(row['bndno']):
                bndno = int(row['pluno'] / 1000)
            else:
                bndno = int(row['bndno'])
            date_str = row['sldatime'][0:10]
            date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            qty = row['qty']
            if bndno in dicts:
                each_row = dicts[bndno]
                index = (date_time - mindate).days + 1
                each_row[index] += qty
            else:
                dicts[bndno] = []
                dicts[bndno].append(bndno)
                i = 1
                index = (date_time - mindate).days + 1
                while i < len(date_list):
                    if i == index:
                        dicts[bndno].append(qty)
                    else:
                        dicts[bndno].append(0.0)
                    i += 1

        # 创建每一行数据
        for key in sorted(dicts.keys()):
            csv_writer.writerow(dicts[key])
        # 关闭文件
        f.close()

    def create_bndno_week_csv(self):
        dicts = {}
        week_list = self.get_week_list()
        mindate = self.min_date()
        # 创建文件对象
        path = "bndno_matrix_week.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(week_list)
        # 遍历源数据
        for index, row in self.data.iterrows():
            if np.isnan(row['bndno']):
                bndno = int(row['pluno'] / 1000)
            else:
                bndno = int(row['bndno'])
            date_str = row['sldatime'][0:10]
            date_time = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            qty = row['qty']
            if bndno in dicts:
                each_row = dicts[bndno]
                index = (date_time - mindate).days + 1
                if index % 7 == 0:
                    index = int(index / 7)
                else:
                    index = int(index / 7) + 1
                each_row[index] += qty
            else:
                dicts[bndno] = []
                dicts[bndno].append(bndno)
                index = (date_time - mindate).days + 1
                if index % 7 == 0:
                    index = int(index / 7)
                else:
                    index = int(index / 7) + 1
                i = 1
                while i < len(week_list):
                    if i == index:
                        dicts[bndno].append(qty)
                    else:
                        dicts[bndno].append(0.0)
                    i += 1
        # 创建每一行数据
        for key in sorted(dicts.keys()):
            csv_writer.writerow(dicts[key])
        # 关闭文件
        f.close()

    def create_bndno_month_csv(self):
        dicts = {}
        month_list = self.get_month_list()
        # 创建文件对象
        path = "bndno_matrix_month.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(month_list)
        for index,row in self.data.iterrows():
            if np.isnan(row['bndno']):
                bndno = int(row['pluno'] / 1000)
            else:
                bndno = int(row['bndno'])
            month = int(row['sldatime'][5:7])
            qty = row['qty']
            if bndno in dicts:
                each_row = dicts[bndno]
                index = month - 1
                each_row[index] += qty
            else:
                dicts[bndno] = []
                dicts[bndno].append(bndno)
                index = month - 1
                i = 1
                while i < len(month_list):
                    if i == index:
                        dicts[bndno].append(qty)
                    else:
                        dicts[bndno].append(0.0)
                    i += 1
        # 创建每一行数据
        for key in sorted(dicts.keys()):
            csv_writer.writerow(dicts[key])
        # 关闭文件
        f.close()

    def create_new_trade(self):
        rows = []
        count = 0
        with open('trade_new.csv', 'r', encoding='UTF-8') as f:
            file = csv.reader(f)
            for line in file:
                if count > 0:
                    line[16] = int(float(line[16]) * 1000)
                rows.append(line)
                count += 1
        print(rows[1][16])
        with open('new_trade.csv', 'w', encoding='UTF-8', newline='') as f:
            file = csv.writer(f)
            file.writerows(rows)


if __name__ == '__main__':
    obj = bndno()
    # obj.create_bndno_day_csv()
    # obj.create_bndno_week_csv()
    # obj.create_bndno_month_csv()
    obj.create_new_trade()
