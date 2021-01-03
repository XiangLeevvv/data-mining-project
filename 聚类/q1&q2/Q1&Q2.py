import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np

def Jaccardfuc(datas, level, id1, id2):
    dict1 = {}
    dict2 = {}
    for index,row in datas.iterrows():
        if(row['vipno'] == id1):
            key = int(row['pluno'] / level)
            if(key in dict1):
                dict1[key] += row['amt']
            else:
                dict1[key] = row['amt']
        elif(row['vipno'] == id2):
            key = int(row['pluno'] / level)
            if(key in dict2):
                dict2[key] += row['amt']
            else:
                dict2[key] = row['amt']
    union = 0
    intersection = 0
    #计算交集
    for k,v in dict1.items():
        if(k in dict2):
            if(v <= dict2[k]):
                intersection += v
            else:
                intersection += dict2[k]
    #计算并集
    for k,v in dict1.items():
        union += v
    for k,v in dict2.items():
        union += v
    union = union - intersection
    return intersection/union

def sumfuc(datas, level):
    dicts = {}
    for index,row in datas.iterrows():
        key = int(row['pluno'] / level)
        if(key in dicts):
            dicts[key] += row['amt']
        else:
            dicts[key] = row['amt']
    return dicts

#预处理，返回一个字典数组，每个字典代表一个用户的购买记录
def init_data(dataset):
    integration = {}
    result = []
    for index,row in dataset.iterrows():
        key = row['vipno']
        pluno = int(row['pluno'] / 1000)
        if(key in integration):
            if(pluno in integration[key]):
                integration[key][pluno] += row['amt']
            else:
                integration[key][pluno] = row['amt']
        else:
            integration[key] = {}
            integration[key][pluno] = row['amt']
    for id, record in integration.items():
        result.append(record)
    return result

def JacDist(dictA, dictB, flag):
    if len(dictA) == 0 or len(dictB) == 0:
        return 0
    si = 0
    length = 1
    for i in range(flag):
        union = 0
        intersection = 0
        dict1 = {}
        dict2 = {}
        for plu, amt in dictA.items():
            key = (int)(plu / length)
            if key in dict1.keys():
                dict1[key] += amt
            else:
                dict1[key] = amt
        for plu, amt in dictB.items():
            key = (int)(plu / length)
            if key in dict2.keys():
                dict2[key] += amt
            else:
                dict2[key] = amt
        #计算并集
        for plu, amt in dict1.items():
            union += amt
        for plu, amt in dict2.items():
            union += amt
        #计算交集
        for plu, amt in dict1.items():
            if plu in dict2:
                if(amt <= dict2[plu]):
                    intersection += amt
                else:
                    intersection += dict2[plu]
        union -= intersection
        si += intersection / union
        length = length * 10
    si = si / flag
    distance = 1 -si
    return distance

def SC_score(clusters):
    SI = 0
    ai = 0
    BI = np.zeros(len(clusters))
    bi = 100
    count = 0
    #计算每一个样本的簇内不相似度a(i)
    for index, cluster in enumerate(clusters):
        for i, customer in enumerate(cluster):
            for j, other_customer in enumerate(cluster):
                ai += JacDist(customer, other_customer, 1)
            if len(cluster) > 1:
                ai = ai / (len(cluster) - 1)
            else:
                ai = 0
            for k, other_cluster in enumerate(clusters):
                if(k != index):
                    for m, customer1 in enumerate(other_cluster):
                        BI[k] += JacDist(customer, customer1, 1)
                    if BI[k] != 0:
                        BI[k] = BI[k] / len(other_cluster)
            for i in range(len(BI)):
                if (BI[i] != 0):
                    if(BI[i] < bi):
                        bi = BI[i]
            if(bi > ai):
                SI += (bi - ai) / bi
                count += 1
            else:
                SI += (bi - ai) / ai
                count += 1
            for i in range(len(BI)):
                BI[i] = 0
            bi = 100
            ai = 0
    SI = SI / count
    return SI

def CP_score(clusters, center):
    CP = np.zeros(len(clusters))
    cp = 0
    for index, cluster in enumerate(clusters):
        for i, customer in enumerate(cluster):
            CP[index] += JacDist(customer, center[index], 1)
    for i, clu in enumerate(clusters):
        if len(clu) != 0:
            CP[i] = CP[i] / len(clu)
    for i in range(len(CP)):
        cp += CP[i]
    return cp / len(CP)

def k_means(dataset, k):
    #初始化簇心
    index = [0,7,14,25,35,49,56,67,78,85,99,100,111,120,135,144,153,167,179,185,192,200,212,222,235,248,250,266,270,285,299,300,313,323,335,344,359,360,378,385,396,404,416,425,435,444,459,467,477,485]
    # index = [0,1,2,3,4,5,6,7,8,9,10]
    key = random.sample(list(range(len(index))), k)
    center = []    #中心点vector
    similar = []     #中心点相似度
    similar.append(1)
    similar.append(0)
    for i in key:
        center.append(dataset[index[i]])
    #初始化标签
    labels = {}
    #根据中心点判断簇是否变化
    while (abs(similar[1] - similar[0]) > 0.01) or (similar[1] > similar[0]):
        C = []
        sim = 0
        for i in range(k):
            C.append([])
        #按最小距离分类
        for index, dict in enumerate(dataset):
            classIndex = -1
            minDist = float('inf')
            for i, point in enumerate(center):
                dist = JacDist(dict, point, 1)
                if(dist < minDist):
                    classIndex = i
                    minDist = dist
            C[classIndex].append(dict)
            labels[index] = classIndex
        #求每个簇的中心点
        for i, cluster in enumerate(C):
            clusterHeart = {}
            centroid = {}   #中心点
            customers = {}  #记录购买同一种类商品用户个数
            for cusdict in cluster:
                for plu, amt in cusdict.items():
                    if plu in centroid.keys():
                        centroid[plu] += amt
                        customers[plu] += 1.0
                    else:
                        centroid[plu] = amt
                        customers[plu] = 1.0
            for key, value in centroid.items():
                clusterHeart[key] = value / len(centroid)
            sim += 1 - JacDist(clusterHeart, center[i], 1)
            center[i] = clusterHeart
        sim /= len(center)
        similar.append(sim)
        similar.pop(0)
        print(similar)
        # plt.plot(list(labels.keys()), list(labels.values()), '.')
        # plt.show()
    return C, labels, center

if __name__ == "__main__":

    dataset = pd.read_csv("trade_new.csv")
    customer_data = init_data(dataset)

    klist = []
    cplist = []
    sclist = []
    sccplist = []
    for K in range(2, 11):
        cp = 0
        sc = 0
        C, labels, clusterHeart = k_means(customer_data, K)
        for key, value in enumerate(C):
            print("簇序号: ",key,"length: ",len(value))
            print(30*'-')
        cp = CP_score(C, clusterHeart)
        sc = SC_score(C)
        klist.append(K)
        sccplist.append(sc / cp)
        sclist.append(sc)
        cplist.append(cp)
        print(cp, sc)
        print('\n')
    plt.plot(klist, cplist, color="darkblue", linewidth=2, linestyle='--', marker='+')
    plt.xlabel('K')
    plt.ylabel('CP')
    plt.show()
    plt.plot(klist, sclist, color="darkblue", linewidth=2, linestyle='--', marker='+')
    plt.xlabel('K')
    plt.ylabel('SC')
    plt.show()
    plt.plot(klist,sccplist,color="darkblue",linewidth=2,linestyle='--',marker='+')
    plt.xlabel('K')
    plt.ylabel('SC/CP')
    plt.show()

    #计算距离分布
    distance = []
    for i in range(len(customer_data) - 1):
        for j in range(i + 1, len(customer_data)):
            distance.append(JacDist(customer_data[i], customer_data[j], 4))
    plt.hist(distance, bins=50)
    plt.xlabel('distance')
    plt.ylabel('frequency')
    plt.title('Distance distribution Q2')
    plt.grid(True, linestyle="-", color="gray", axis='both')
    plt.savefig('distance distribution Q2.png', dpi=400)
    plt.show()

    #字典计算金额总和
    catalog_1th = sumfuc(dataset, 1000000)
    catalog_2th = sumfuc(dataset, 100000)
    catalog_3th = sumfuc(dataset, 10000)
    catalog_4th = sumfuc(dataset, 1000)
    print("第4级品类结构金额汇总:")
    print(catalog_4th)
    print(50*'-')
    print("第3级品类结构金额汇总:")
    print(catalog_3th)
    print(50 * '-')
    print("第3级品类结构金额汇总:")
    print(catalog_2th)
    print(50 * '-')
    print("第3级品类结构金额汇总:")
    print(catalog_1th)
    print(50 * '-')

    sim1 = Jaccardfuc(dataset,1000,2900003115009,2900001575201)
    sim2 = Jaccardfuc(dataset,10000,2900003115009,2900001575201)
    sim3 = Jaccardfuc(dataset,100000,2900003115009,2900001575201)
    sim4 = Jaccardfuc(dataset,1000000,2900003115009,2900001575201)
    print("方法1 Jaccard相似度:",sim1)
    print("方法2 Jaccard相似度:",((sim1 + sim2 + sim3 + sim4) / 4))
    
