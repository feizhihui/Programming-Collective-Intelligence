# encoding=utf-8
from psimilarity import sim_pearson, sim_distance
from recommendations import critics


# 筛选出top n个与person的相似的匹配者
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    # 对所有人进行相似度评分
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]

    # 对列表进行排序，评分最高者排在靠前
    scores.sort()
    scores.reverse()
    return scores[:n]


if __name__ == '__main__':
    print '打印与Toby相似度（基于欧氏距离）最高的前三者：'
    print topMatches(critics, 'Toby', n=3,similarity=sim_distance)
    print '打印与Toby相似度（基于相关系数）最高的前三者：'
    print topMatches(critics, 'Toby', n=3)
    print 'This is a test!'
    print topMatches(critics, 'Toby', n=100)
