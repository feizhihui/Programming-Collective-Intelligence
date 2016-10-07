# encoding=utf-8
from recommendations import critics
from psimilarity import sim_pearson, sim_distance

# 利用所有他人评价的加权平均，为某人提供建议
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person: continue
        sim = similarity(prefs, person, other)

        if sim <= 0: continue
        for item in prefs[other]:
            # 只对自己还未看过的电影进行评价
            if item not in prefs[person]:
                # 相似度*评价值
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # 相似度之和
                simSums.setdefault(item, 0)
                simSums[item] += sim


    # 建立一个归一化的列表
    ranking = [(score / simSums[item], item) for item, score in totals.items()]

    #返回经过排序的列表
    ranking.sort()
    ranking.reverse()
    return ranking

if __name__=='__main__':
    print getRecommendations(critics,'Toby')
    print getRecommendations(critics, 'Toby',similarity=sim_distance)