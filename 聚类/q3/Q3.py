import pandas as pd
import datetime as dt
import numpy as np
import random
import math
import matplotlib.pyplot as plt

def intervalTime(time):
    date1 = dt.datetime((int)(time[0:4]),(int)(time[5:7]),(int)(time[8:10]))
    date2 = dt.datetime(2016, 0o7, 31)
    interval = date2 - date1
    days = interval.days
    # print(days)
    if days <= 31:
        return 4
    elif days > 31 and days <= 61:
        return 3
    elif days > 61 and days <= 122:
        return 2
    else:
        return 1

def init_data(dataset):
    cusTree = {}
    for index, row in dataset.iterrows():
        id = row['vipno']
        division = 1000000.0  # 除数
        if not id in cusTree.keys():    #该用户还没有记录树
            cusTree[id] = []    #初始化用户树
            for i in range(4):
                cusTree[id].append({})
            lev = intervalTime(row['sldatime'])
            for i in range(lev):    #按时间等级添加结点
                plu = (int)(row['pluno'] / division)
                if plu in cusTree[id][i]:
                    cusTree[id][i][plu] += 1
                else:
                    cusTree[id][i][plu] = 1
                division /= 10
        else:
            lev = intervalTime(row['sldatime'])
            for i in range(lev):  # 按时间等级添加结点
                plu = (int)(row['pluno'] / division)
                if plu in cusTree[id][i]:
                    cusTree[id][i][plu] += 1
                else:
                    cusTree[id][i][plu] = 1
                division /= 10
    return cusTree

def IR(listA, listB):
    resTree = []
    for i in range(4):
        resTree.append({})
    for lev in range(4):
        if len(listA[lev]) > 0 and len(listB[lev]) > 0:
            for plu, freq in listA[lev].items():
                if plu in listB[lev]:
                    resTree[lev][plu] = freq + listB[lev][plu]
        else:
            break
    return resTree

def UR(listA, listB):
    resTree = []
    for i in range(4):
        resTree.append({})
    for lev in range(4):
        for plu, freq in listA[lev].items():
            if plu in listB[lev]:
                resTree[lev][plu] = freq + listB[lev][plu]
            else:
                resTree[lev][plu] = freq
        for key, value in listB[lev].items():
            if key not in listA[lev]:
                resTree[lev][key] = value
    return resTree

def Dist(IR, UR):
    Sim = np.zeros(4)
    count = np.zeros(4, dtype=np.int)
    SIM = 0
    freq0 = 0
    height = 0
    for plu, freq in UR[0].items():
        freq0 += freq
    for lev in range(4):
        if lev == 0:
            for plu, freq in IR[lev].items():
                Sim[lev] += freq / freq0
                count[lev] += 1
        else:
            for plu1, freq1 in IR[lev].items():
                freqU = 0
                for plu2, freq2 in UR[lev].items():     #计算freq(u)的和
                    if (int)(plu2 / 10) == (int)(plu1 / 10):
                        freqU += freq2
                Sim[lev] += freq1 / freqU
                count[lev] += 1
    for i in range(4):
        if count[i] != 0:
            Sim[i] = Sim[i] / count[i]
            height += 1
    if height == 0:
        # print("IR's height is 0")
        return 1
    total = 0
    for j in range(height):
        total += (j + 1)
    for i in range(4):
        SIM += ((i + 1) * Sim[i])
    return 1 - SIM / total

def nodeNum(tree):
    length = len(tree[0]) + len(tree[1]) + len(tree[2]) + len(tree[3])
    return length

def update(tree, freq):
    newTree = []
    for i in range(len(tree)):
        temp = {}
        for key, value in tree[i].items():
            if value > freq:
                temp[key] = value
        newTree.append(temp)
    return newTree

def GetCT(cluster):
    utree = []
    avgNode = 0
    for i in range(4):
        utree.append({})
    #暂时把cluster当作字典处理
    for key, list in cluster.items():    #创建unionTree
        temp = UR(utree, list)
        utree = temp
        avgNode += nodeNum(list)
    avgNode = avgNode / len(cluster)    #获取簇内用户的FTCTree的平均节点数
    freq = 1
    mindist = float('inf')
    freqStep = 0
    freqEnd = -1
    for plu, freq in utree[0].items():
        if freq > freqEnd:
            freqEnd = freq
    for i in range(4):
        for plu, freq in utree[i].items():
            freqStep += freq
    freqStep = freqStep / nodeNum(utree)
    while freq <= freqEnd:
        utree = update(utree, freq)
        if nodeNum(utree) < avgNode:
            break
        dist = 0
        for id, tree in cluster.items():
            ir = IR(tree, utree)
            ur = UR(tree, utree)
            dist += Dist(ir, ur)
        if dist < mindist:
            mindist = dist
        freq += freqStep
    return utree

def kmeans(cusTrees):
    # 初始化簇心
    index = random.sample(list(cusTrees.keys()), 2)
    center = []  # 中心点vector
    similar = []  # 中心点相似度
    similar.append(0)
    similar.append(1)
    dictA = {}
    dictB = {}
    iteratation = 0
    for i in index:
        center.append(cusTrees[i])
    # 根据中心点判断簇是否变化
    while (abs(similar[1] - similar[0]) > 0.01):
        if iteratation >= 30:
            break
        iteratation += 1
        dictA = {}
        dictB = {}
        simi = 0
        # 按最小距离分类
        for id, tree in cusTrees.items():
            classIndex = -1
            minDist = float('inf')
            for i, centerTree in enumerate(center):
                ir = IR(tree, centerTree)
                ur = UR(tree, centerTree)
                dist = Dist(ir, ur)
                if (dist < minDist):
                    classIndex = i
                    minDist = dist
            if classIndex == 0:
                dictA[id] = tree
            else:
                dictB[id] = tree
        if len(dictA) == 0 or len(dictB) == 0:
            return dictA, dictB, center
        # 求每个簇的中心点
        newCenter = []
        newCenter.append(GetCT(dictA))
        newCenter.append(GetCT(dictB))
        for i in range(2):
            ir = IR(center[i], newCenter[i])
            ur = UR(center[i], newCenter[i])
            simi += 1 - Dist(ir, ur)
        similar.append(simi / len(center))
        similar.pop(0)
        center[0] = newCenter[0]
        center[1] = newCenter[1]
        # print(similar)
    return dictA, dictB, center

def cal_D(cluster):
    D = 0
    item = {}
    for id, tree in cluster.items():
        for plu, freq in tree[3].items():
            if plu not in item.keys():
                D += 1
            else:
                item[plu] = bool(1)
    return D

def cal_O(cluster, center):
    dist = 0
    for id, tree in cluster.items():
        ir = IR(tree, center)
        ur = UR(tree, center)
        dist += Dist(ir, ur)**2
    return dist

def BIC(cluster):
    N = len(cluster)
    D = cal_D(cluster)
    bic_before = 0
    bic_after = 0
    bic_before -= N * math.log(2 * math.pi) * 0.5
    bic_before -= 0.5 * N * D * math.log((1 / (N - 1)) * cal_O(cluster, GetCT(cluster)))
    bic_before -= 0.5 * (N - 1)
    bic_after -= (D + 1) * math.log(2)
    cluster1, cluster2, center = kmeans(cluster)
    N1 = len(cluster1)
    N2 = len(cluster2)
    if N1 < 3 or N2 < 3:
        return bool(0), cluster1, cluster2
    bic_after += N1 * math.log(N1) + N2 * math.log(N2)
    bic_after -= (N1 + N2) * math.log(N1 + N2)
    bic_after -= 0.5 * (N1 + N2) * math.log(2 * math.pi)
    bic_after -= 0.5 * N1 * D * math.log((1 / (N1 - 2)) * cal_O(cluster1, center[0]))
    bic_after -= 0.5 * N2 * D * math.log((1 / (N2 - 2)) * cal_O(cluster2, center[1]))
    bic_after -= 0.5 * (N1 - 2) + 0.5 * (N2 - 2)
    if bic_after > bic_before:
        return bool(1), cluster1, cluster2
    else:
        return bool(0), {}, {}

def CP(cluster, center):
    distance = []
    for id, clu in enumerate(cluster):
        cp = 0
        for key, tree in clu.items():
            ir = IR(tree, center[id])
            ur = UR(tree, center[id])
            cp += Dist(ir, ur)
        distance.append(cp / len(clu))
    dist = 0
    for i in range(len(distance)):
        dist += distance[i]
    return dist / len(distance)

def SC(cluster):
    innerDist = 0
    externalDist = np.zeros(len(cluster))
    externaldist = float('inf')
    count = 0
    num = 0
    sc = 0
    for id, clu in enumerate(cluster):
        for Skey, Stree in clu.items():
            #计算簇内平均距离
            for Okey, Otree in clu.items():
                if Okey != Skey:
                    ir = IR(Stree, Otree)
                    ur = UR(Stree, Otree)
                    innerDist += Dist(ir, ur)
            innerDist = innerDist / (len(clu) - 1)
            #计算簇间平均距离
            for Oid, Oclu in enumerate(cluster):
                if Oid != id:
                    for Ekey, Etree in Oclu.items():
                        ir = IR(Stree, Etree)
                        ur = UR(Stree, Etree)
                        externalDist[Oid] += Dist(ir, ur)
                        count += 1
                    if count != 0:
                        externalDist[Oid] /= count
                    count = 0
            for dist in externalDist:
                if dist != 0:
                    if dist < externaldist:
                        externaldist = dist
            if externaldist > innerDist:
                sc += (externaldist - innerDist) / externaldist
            else:
                sc += (externaldist - innerDist) / innerDist
            num += 1
            innerDist = 0
            externaldist = float('inf')
            for i in range(len(externalDist)):
                externalDist[i] = 0
    return sc / num


if __name__ == "__main__":

    dataset = pd.read_csv("trade_new.csv")
    #获取时间起始点
    time = list(dataset['sldatime'])
    date = []
    latestTime = ''     #时间起始点
    for item in time:
        item = item[:10]
        if not item in date:
            date.append(item)
    for index in sorted(date):
        latestTime = index
    customer_data = init_data(dataset)

    # 计算距离分布
    distance = []
    for i, tree1 in customer_data.items():
        for j, tree2 in customer_data.items():
            if j > i:
                ir = IR(tree1, tree2)
                ur = UR(tree1, tree2)
                distance.append(Dist(ir, ur))
    plt.hist(distance, bins=50)
    plt.xlabel('distance')
    plt.ylabel('frequency')
    plt.title('Distance distribution Q3')
    plt.grid(True, linestyle="-", color="gray", axis='both')
    plt.savefig('distance distribution Q3.png', dpi=400)
    plt.show()

    print("start")
    ableclusters = []
    unableclusters = []
    centers = []
    ableclusters.append(customer_data)
    while len(ableclusters) > 0:
        newclusters = []
        for key, clu in enumerate(ableclusters):
            flag, div1, div2 = BIC(clu)
            if (flag):
                newclusters.append(div1)
                newclusters.append(div2)
            else:
                unableclusters.append(clu)
                centers.append(GetCT(clu))
        ableclusters = newclusters
        print(len(ableclusters), len(unableclusters))
        print("iterate once")
    print("-----------------------------")
    print(len(unableclusters))
    for cluster in unableclusters:
        print(cluster)
    print(CP(unableclusters, centers))
    print(SC(unableclusters))