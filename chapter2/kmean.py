# encoding=utf-8

"""
:k-均值聚类过程
"""
from cluster import pearson, readfile
import random


def kcluster(rows, distance=pearson, k=4):
    # 确定每个维度的最小值和最大值
    ranges = [(min([row[j] for row in rows]), max([row[j] for row in rows])) for j in range(len(rows[0]))]

    # 随机创建k个中间点
    clusters = [[random.random() * (ranges[j][1] - ranges[j][0]) for j in range(len(rows[0]))] for i in range(k)]

    lastmatches = None

    # 设置100次迭代
    for t in range(100):

        print 'Iteration %d' % t
        # k个列表组成的二维列表
        bestmatches = [[] for i in range(k)]

        # 在每一行中寻找距离最近的中心点
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                # 记录第j行最近的基准点
                if d < distance(clusters[bestmatch], row): bestmatch = i
            bestmatches[bestmatch].append(j)

        # 如果结果与上一次相同，则整个过程结束（二维列表未发生变化）
        if bestmatches == lastmatches: break
        lastmatches = bestmatches

        # 把中心移动到其成员的平均位置处，重新确定起始位置，为下一轮做准备
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            lens = len(bestmatches[i])
            if lens > 0:
                # 遍历该个聚集中每一行
                for rowid in bestmatches[i]:
                    # 遍历每一列，对应值相加
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]

                # 计算每一维度的平均值
                avgs = [avgs[j] / lens for j in range(len(avgs))]
                # 重新记录中间点
                clusters[i] = avgs

    return bestmatches


if __name__ == '__main__':
    blognames, words, data = readfile('data/blogdata.txt')

    kclust = kcluster(data, k=20)

    for i in range(len(kclust)):
        print '第%d个集合：' % i
        print [blognames[r] for r in kclust[i]]
