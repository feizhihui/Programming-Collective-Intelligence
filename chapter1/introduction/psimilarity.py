# encoding=utf-8

# 返回一个有关person1与person2的基于距离的相似度评价
from math import sqrt
from recommendations import critics


# 返回person1与person2基于距离的相似度评价
def sim_distance(prefs, person1, person2):
    # 得到shared_items的列表
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # 如果二者没有共同之处，返回0
    if len(si) == 0:
        return 0

    # 计算所有差值的平方和

    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in si])

    return 1 / (1 + sqrt(sum_of_squares))


def sim_distance2(prefs, person1, person2):
    # 计算所有差值的平方和
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1 + sqrt(sum_of_squares))


# 返回p1与p2的pearson相关系数作为相似度评价
def sim_pearson(prefs, p1, p2):
    # 得到双方共同的评价列表
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    n = float(len(si))
    if n == 0: return 1
    sum1 = sum([prefs[p1][item] for item in si])
    sum2 = sum([prefs[p2][item] for item in si])
    sum1Sq = sum([pow(prefs[p1][item], 2) for item in si])
    sum2Sq = sum([pow(prefs[p2][item], 2) for item in si])
    pSum = sum([prefs[p1][item] * prefs[p2][item] for item in si])

    # pearson系数计算公式
    nume = pSum - sum1 * sum2 / n
    deno = sqrt((sum1Sq - sum1 * sum1 / n) * (sum2Sq - sum2 * sum2 / n))
    if deno == 0: return 0
    r = nume / deno

    return r


def sim_pearson2(prefs, p1, p2):
    # 得到双方共同的评价列表
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1
    n = float(len(si))
    if n == 0: return 1
    avg1 = sum([prefs[p1][item] for item in si]) / n
    avg2 = sum([prefs[p2][item] for item in si]) / n

    nume = sum([(prefs[p1][item] - avg1) * (prefs[p2][item] - avg2)
                for item in si])
    deno = sqrt(sum([pow(prefs[p1][item] - avg1, 2) for item in si]) *
                sum([pow(prefs[p2][item] - avg2, 2) for item in si]))

    if deno == 0: return 0
    return nume / deno


if __name__ == '__main__':
    print '基于距离的相似度评价：'
    print sim_distance(critics, 'Lisa Rose', 'Gene Seymour')
    print sim_distance2(critics, 'Lisa Rose', 'Gene Seymour')
    print '基于相关系数的相似度评价：'
    print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')
    print sim_pearson2(critics, 'Lisa Rose', 'Gene Seymour')
