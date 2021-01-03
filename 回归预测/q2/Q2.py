import pandas as pd
import numpy as np
import csv
import datetime


# data = pd.read_csv('trade_new.csv')
pluno_key = [22,23,25,27]
# null = 0
# count = 0
# for index,row in data.iterrows():
#     if int(row['pluno'] / 1000000) in pluno_key:
#         if np.isnan(row['bndno']):
#             null += 1
#         count += 1


class feature_engineer:
    def __init__(self):
        self.data = pd.read_csv('new_trade.csv')
        for index, row in self.data.iterrows():
            row['qty'] = int(row['qty'] * 1000)

    def is_weekday(self,date_str):
        date = datetime.datetime.strptime(date_str,'%Y-%m-%d').weekday()
        if date + 1 < 6:
            return True
        else:
            return False

    def last_week_list(self,date_str):
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        week_list = []
        i = 0
        while i < 7:
            time = date - datetime.timedelta(days= (i + 1))
            date_time = datetime.datetime.strftime(time,'%Y-%m-%d')
            week_list.append(date_time)
            i += 1
        return week_list

    def past_week_list(self,date_str):
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
        date_list.append(datetime.datetime.strftime(start_date, '%Y-%m-%d'))
        while start_date < end_date:
            start_date += datetime.timedelta(days=1)
            date_str = datetime.datetime.strftime(start_date, '%Y-%m-%d')
            date_list.append(date_str)
        return date_list

    def get_pluno_dict(self):
        dicts = {}
        date_list = self.get_date_list()
        # 遍历源数据
        for index, row in self.data.iterrows():
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

    def get_bndno_dict(self):
        dicts = {}
        date_list = self.get_date_list()
        # 遍历源数据
        for index, row in self.data.iterrows():
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

    def get_pluno_level_dict(self, lev):
        dicts = {}
        date_list = self.get_date_list()
        # 遍历源数据
        for index, row in self.data.iterrows():
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

    def feature_i(self):
        result = {}  # 结果数组存储最终特征工程结果
        # 设置csv文件头部
        head = ['pluno','bndno','pluno1','pluno2','pluno3','pluno4','sldatime'
            ,'isweekday','qty','d-1','d-2','d-3','d-4','d-5','d-6','d-7']
        # 创建文件对象
        path = "feature_i.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(head)
        # 获取pluno,date二级字典用来查找相应数据
        history_dict = self.get_pluno_dict()
        # 遍历源数据
        for index,row in self.data.iterrows():
            pluno = row['pluno']
            pluno1 = int(pluno / 1000000)
            # 选取所有数据中的一个子集
            if pluno1 in pluno_key:
                # 我将bndno设置为第四季品类的理由是：
                # 这些没有bndno的商品都可以分为相应的商品类别，比如每一个苹果可能都没有bndno
                # 但是它们都是苹果就相当于一个品牌，给每一个苹果设置成一个品牌反而会给模型造成误解
                bndno = int(pluno / 1000)
                pluno2 = int(pluno / 100000)
                pluno3 = int(pluno / 10000)
                pluno4 = int(pluno / 1000)
                sldatime = row['sldatime'][0:10]
                # 判断是否是周末
                if self.is_weekday(sldatime):
                    isweekday = 1
                else:
                    isweekday = 0
                qty = row['qty']
                # 获取之前一周的日期
                weeklist = self.last_week_list(sldatime)
                if pluno in result:
                    if sldatime in result[pluno]:
                        result[pluno][sldatime][8] += qty
                    else:
                        result[pluno][sldatime] = [pluno, bndno, pluno1, pluno2, pluno3, pluno4, sldatime, isweekday, qty]
                else:
                    result[pluno] = {}
                    result[pluno][sldatime] = [pluno, bndno, pluno1, pluno2, pluno3, pluno4, sldatime, isweekday, qty]
                # 获取前一周内每天该商品的销量
                if pluno in result:
                    if sldatime in result[pluno]:
                        li = result[pluno][sldatime]
                        if len(li) == 9:
                            for date in weeklist:
                                min_date = datetime.datetime.strptime('2016-02-01','%Y-%m-%d')
                                this_date = datetime.datetime.strptime(date,'%Y-%m-%d')
                                # 当日期超出最早日期时该日期销量设为0
                                if this_date < min_date:
                                    li.append(0.0)
                                else:
                                    li.append(history_dict[pluno][date])
        # 创建每一行数据
        for key1 in sorted(result.keys()):
            dict1 = result[key1]
            for key2 in sorted(dict1.keys()):
                rec = dict1[key2]
                csv_writer.writerow(rec)
        # 关闭文件
        f.close()

    def feature_ii(self):
        result = {}
        head = ['pluno',' d-1', 'd-2', 'd-3', 'd-4', 'd-5', 'd-6', 'd-7']
        # 创建文件对象
        path = "feature_ii.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(head)
        # 遍历源数据
        history_dict = self.get_bndno_dict()
        for index, row in self.data.iterrows():
            pluno = row['pluno']
            pluno1 = int(pluno / 1000000)
            bndno = int(pluno / 1000)
            sldatime = row['sldatime'][0:10]
            if pluno1 in pluno_key:
                weeklist = self.last_week_list(sldatime)
                if pluno in result:
                    if sldatime in result[pluno]:
                        continue
                    else:
                        result[pluno][sldatime] = []
                        result[pluno][sldatime].append(pluno)
                else:
                    result[pluno] = {}
                    result[pluno][sldatime] = []
                    result[pluno][sldatime].append(pluno)
                # 添加数据
                if pluno in result:
                    if sldatime in result[pluno]:
                        li = result[pluno][sldatime]
                        if len(li) == 1:
                            for date in weeklist:
                                min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                                this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                                if this_date < min_date:
                                    li.append(0.0)
                                else:
                                    li.append(history_dict[bndno][date])
        # 创建每一行数据
        for key1 in sorted(result.keys()):
            dict1 = result[key1]
            for key2 in sorted(dict1.keys()):
                rec = dict1[key2]
                csv_writer.writerow(rec)
        # 关闭文件
        f.close()

    def feature_iii(self):
        result = {}
        head = ['pluno','4d-1', '4d-2', '4d-3', '4d-4', '4d-5', '4d-6', '4d-7',
                '3d-1', '3d-2', '3d-3', '3d-4', '3d-5', '3d-6', '3d-7',
                '2d-1', '2d-2', '2d-3', '2d-4', '2d-5', '2d-6', '2d-7',
                '1d-1', '1d-2', '1d-3', '1d-4', '1d-5', '1d-6', '1d-7']
        # 创建文件对象
        path = "feature_iii.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(head)
        # 遍历源数据
        pluno_level_dict = [self.get_pluno_level_dict(1000), self.get_pluno_level_dict(10000),
                            self.get_pluno_level_dict(100000), self.get_pluno_level_dict(1000000)]
        for index, row in self.data.iterrows():
            pluno = row['pluno']
            pluno_level = [int(pluno / 1000), int(pluno / 10000), int(pluno / 100000), int(pluno / 1000000)]
            sldatime = row['sldatime'][0:10]
            if pluno_level[3] in pluno_key:
                weeklist = self.last_week_list(sldatime)
                # 初始化结果字典
                if pluno in result:
                    if sldatime in result[pluno]:
                        continue
                    else:
                        result[pluno][sldatime] = []
                        result[pluno][sldatime].append(pluno)
                else:
                    result[pluno] = {}
                    result[pluno][sldatime] = []
                    result[pluno][sldatime].append(pluno)
                # 添加数据
                if pluno in result:
                    if sldatime in result[pluno]:
                        li = result[pluno][sldatime]
                        if len(li) == 1:
                            i = 0
                            while i < 4:
                                pluno_dict = pluno_level_dict[i]
                                pluno_id = pluno_level[i]
                                for date in weeklist:
                                    min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                                    this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                                    if this_date < min_date:
                                        li.append(0.0)
                                    else:
                                        li.append(pluno_dict[pluno_id][date])
                                i += 1
        # 创建每一行数据
        for key1 in sorted(result.keys()):
            dict1 = result[key1]
            for key2 in sorted(dict1.keys()):
                rec = dict1[key2]
                csv_writer.writerow(rec)
        # 关闭文件
        f.close()

    def feature_iv(self):
        result = {}  # 结果数组存储最终特征工程结果
        # 设置csv文件头部
        head = ['pluno', 'avg2', 'max2', 'min2', 'avg3', 'max3', 'min3', 'avg4',
                'max4', 'min4']
        # 创建文件对象
        path = "feature_iv.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(head)
        # 获取pluno,date二级字典用来查找相应数据
        history_dict = self.get_pluno_dict()
        # 遍历源数据
        for index, row in self.data.iterrows():
            pluno = row['pluno']
            pluno1 = int(pluno / 1000000)
            sldatime = row['sldatime'][0:10]
            if pluno1 in pluno_key:
                weeklist = self.past_week_list(sldatime)
                if pluno in result:
                    if sldatime in result[pluno]:
                        continue
                    else:
                        result[pluno][sldatime] = []
                        result[pluno][sldatime].append(pluno)
                else:
                    result[pluno] = {}
                    result[pluno][sldatime] = []
                    result[pluno][sldatime].append(pluno)
                # 添加数据
                if pluno in result:
                    if sldatime in result[pluno]:
                        li = result[pluno][sldatime]
                        if len(li) == 1:
                            avg = 0.0
                            max = 0.0
                            min = float('inf')
                            # 循环遍历前2、3、4周，获取每周的avg、max、min
                            for week in weeklist:
                                # 遍历一周中的每天
                                for date in week:
                                    min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                                    this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                                    # 因为早于最早日期的销量全是0，所以avg不需要加
                                    if this_date > min_date:
                                        avg += history_dict[pluno][date]
                                        if history_dict[pluno][date] > max:
                                            max = history_dict[pluno][date]
                                        if history_dict[pluno][date] < min:
                                            min = history_dict[pluno][date]
                                    else:
                                        min = 0.0
                                avg = avg / 7
                                li.append(avg)
                                li.append(max)
                                li.append(min)
                                # 重置avg、max、min
                                avg = 0.0
                                max = 0.0
                                min = float('inf')
        # 创建每一行数据
        for key1 in sorted(result.keys()):
            dict1 = result[key1]
            for key2 in sorted(dict1.keys()):
                rec = dict1[key2]
                csv_writer.writerow(rec)
        # 关闭文件
        f.close()

    def feature_v(self):
        result = {}
        head = ['pluno','avg2', 'max2', 'min2', 'avg3', 'max3', 'min3', 'avg4','max4', 'min4']
        # 创建文件对象
        path = "feature_v.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(head)
        # 遍历源数据
        history_dict = self.get_bndno_dict()
        for index, row in self.data.iterrows():
            pluno = row['pluno']
            pluno1 = int(pluno / 1000000)
            bndno = int(pluno / 1000)
            sldatime = row['sldatime'][0:10]
            if pluno1 in pluno_key:
                weeklist = self.past_week_list(sldatime)
                if pluno in result:
                    if sldatime in result[pluno]:
                        continue
                    else:
                        result[pluno][sldatime] = []
                        result[pluno][sldatime].append(pluno)
                else:
                    result[pluno] = {}
                    result[pluno][sldatime] = []
                    result[pluno][sldatime].append(pluno)
                # 添加数据
                if pluno in result:
                    if sldatime in result[pluno]:
                        li = result[pluno][sldatime]
                        if len(li) == 1:
                            avg = 0.0
                            max = 0.0
                            min = float('inf')
                            for week in weeklist:
                                for date in week:
                                    min_date = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
                                    this_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                                    if this_date > min_date:
                                        avg += history_dict[bndno][date]
                                        if history_dict[bndno][date] > max:
                                            max = history_dict[bndno][date]
                                        if history_dict[bndno][date] < min:
                                            min = history_dict[bndno][date]
                                    else:
                                        min = 0.0
                                avg = avg / 7
                                li.append(avg)
                                li.append(max)
                                li.append(min)
                                avg = 0.0
                                max = 0.0
                                min = float('inf')
        # 创建每一行数据
        for key1 in sorted(result.keys()):
            dict1 = result[key1]
            for key2 in sorted(dict1.keys()):
                rec = dict1[key2]
                csv_writer.writerow(rec)
        # 关闭文件
        f.close()

    def feature_vi(self):
        result = {}
        head = ['pluno', '4avg2', '4max2', '4min2', '4avg3', '4max3', '4min3', '4avg4', '4max4', '4min4',
                '3avg2', '3max2', '3min2', '3avg3', '3max3', '3min3', '3avg4', '3max4', '3min4',
                '2avg2', '2max2', '2min2', '2avg3', '2max3', '2min3', '2avg4', '2max4', '2min4',
                '1avg2', '1max2', '1min2', '1avg3', '1max3', '1min3', '1avg4', '1max4', '1min4']
        # 创建文件对象
        path = "feature_vi.csv"
        f = open(path, 'w', encoding='utf-8', newline='' "")
        # 基于文件对象构建 csv写入对象
        csv_writer = csv.writer(f)
        # 构建列表头
        csv_writer.writerow(head)
        # 遍历源数据
        pluno_level_dict = [self.get_pluno_level_dict(1000), self.get_pluno_level_dict(10000),
                            self.get_pluno_level_dict(100000), self.get_pluno_level_dict(1000000)]
        for index, row in self.data.iterrows():
            pluno = row['pluno']
            pluno_level = [int(pluno / 1000), int(pluno / 10000), int(pluno / 100000), int(pluno / 1000000)]
            sldatime = row['sldatime'][0:10]
            if pluno_level[3] in pluno_key:
                weeklist = self.past_week_list(sldatime)
                if pluno in result:
                    if sldatime in result[pluno]:
                        continue
                    else:
                        result[pluno][sldatime] = []
                        result[pluno][sldatime].append(pluno)
                else:
                    result[pluno] = {}
                    result[pluno][sldatime] = []
                    result[pluno][sldatime].append(pluno)
                # 添加数据
                if pluno in result:
                    if sldatime in result[pluno]:
                        li = result[pluno][sldatime]
                        if len(li) == 1:
                            avg = 0.0
                            max = 0.0
                            min = float('inf')
                            i = 0
                            while i < 4:
                                pluno_dict = pluno_level_dict[i]
                                pluno_index = pluno_level[i]
                                for week in weeklist:
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
                                    li.append(avg)
                                    li.append(max)
                                    li.append(min)
                                    avg = 0.0
                                    max = 0.0
                                    min = float('inf')
                                i += 1
        # 创建每一行数据
        for key1 in sorted(result.keys()):
            dict1 = result[key1]
            for key2 in sorted(dict1.keys()):
                rec = dict1[key2]
                csv_writer.writerow(rec)
        # 关闭文件
        f.close()


if __name__ == '__main__':
    obj = feature_engineer()
    # obj.feature_i()
    # obj.feature_ii()
    # obj.feature_iii()
    # obj.feature_iv()
    # obj.feature_v()
    obj.feature_vi()