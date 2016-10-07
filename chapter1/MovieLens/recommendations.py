# encoding=utf-8

from chapter1.introduction.GetRecommendations import getRecommendations
from chapter1.introduction.TopMatches import topMatches
from chapter1.introduction.psimilarity import sim_distance


def loadMoviesLens(path='../data/movielens'):
    # 获取影片标题
    movies = {}
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    # 加载数据
    # prefs={userid:{moviename:rating},...}
    prefs = {}
    for line in open(path + '/u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)

    return prefs


# 计算物品的相似度
def calculateSimilarItems(prefs, n=10):
    # 建立字典，以给出与这些物品最为相近的所有其他物品
    result = {}

    # 以物品为中心对偏好矩阵实施倒置处理
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # 针对大数据及更新状态变量
        c += 1
        if c % 100 == 0: print "%d/%d" % (c, len(itemPrefs))
        # 寻找最为相近的物品
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


# {person:{movie,score},...}->{movie:{person,score}}
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            # 将物品和人员对调
            result[item][person] = prefs[person][item]

    return result


def getRecommendedItems(pref, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # 循环遍历由当前用户评分的物品
    for (item, rating) in userRatings.items():
        # 循环遍历与当前物品相近的物品
        for (similarity, item2) in itemMatch[item]:
            # 如果用户已经对当前物品做过评价，则将其忽略
            if item2 in userRatings: continue

            # 评价值与相似度的加权之和
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating

            # 全部相似度之和
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity

    # 将每个合计值除以加权和，求出平均值
    rankings=[(score/totalSim[item],item) for item,score in scores.items()]

    # 按最高到最低的顺序，返回评分结果
    rankings.sort()
    rankings.reverse()
    return rankings






if __name__ == '__main__':
    prefs = loadMoviesLens()
    print '用户数量：', len(prefs)
    # 基于用户的推荐
    print getRecommendations(prefs, '87')[0:30]

    # 基于物品的推荐
    itemsim=calculateSimilarItems(prefs,n=50)
    print getRecommendedItems(prefs,itemsim,'87')[0:30]