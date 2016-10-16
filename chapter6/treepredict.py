# encoding=utf-8

#  title: 来源网站，位置，是否阅读过FAQ，浏览网页数，选择服务类型
my_data = [['slashdot', 'USA', 'yes', 18, 'None'],
           ['google', 'France', 'yes', 23, 'Premium'],
           ['digg', 'USA', 'yes', 24, 'Basic'],
           ['kiwitobes', 'France', 'yes', 23, 'Basic'],
           ['google', 'UK', 'no', 21, 'Premium'],
           ['(direct)', 'New Zealand', 'no', 12, 'None'],
           ['(direct)', 'UK', 'no', 21, 'Basic'],
           ['google', 'USA', 'no', 24, 'Premium'],
           ['slashdot', 'France', 'yes', 19, 'None'],
           ['digg', 'USA', 'no', 18, 'None'],
           ['google', 'UK', 'no', 18, 'None'],
           ['kiwitobes', 'UK', 'no', 19, 'None'],
           ['digg', 'New Zealand', 'yes', 12, 'Basic'],
           ['slashdot', 'UK', 'no', 21, 'None'],
           ['google', 'UK', 'yes', 18, 'Basic'],
           ['kiwitobes', 'France', 'yes', 19, 'Basic']]


# 代表树上的每一个节点
class decisionnode:
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        # 待检验的判断条件所对应的列索引值
        self.col = col
        # 对应于为了使结果为True，当前列必须匹配的值
        self.value = value
        # 保存的是针对当前分支的结果，它是一个字典。除叶节点外，在其他节点该值都为None
        self.results = results
        # tb和fb也是decisionnode，对应于结果分别为True或False时，树上相对于当前节点的子树上的节点
        self.tb = tb
        self.fb = fb


# Divides a set on a specific column. Can handle numeric
# or nominal values
def divideset(rows, column, value):
    """
    根据column列的特征来拆分节点；
    value是阈值或某一名义字符串
    :param rows:
    :param column:
    :param value:
    :return: (set1,set2)
    """
    # Make a function that tells us if a row is in
    # the first group (true) or the second group (false)
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        # 根据数值型特征拆分节点
        split_function = lambda row: row[column] >= value
    else:
        # 根据名义型特征拆分节点
        split_function = lambda row: row[column] == value

    # Divide the rows into two sets and return them
    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return (set1, set2)


# Create counts of possible results (the last column of
# each row is the result)
def uniquecounts(rows):
    """
    统计rows有哪些类别和它们的数量
    :param rows:
    :return: {C1:1，C2：2，...}
    """
    results = {}
    for row in rows:
        # The result is the last column
        r = row[len(row) - 1]
        if r not in results: results[r] = 0
        results[r] += 1
    return results


# Probability that a randomly placed item will
# be in the wrong category
def giniimpurity(rows):
    """
    计算这个类别的基尼不纯度（错误分类的概率）
    :param rows:
    :return: impurity（float）
    """
    total = len(rows)
    counts = uniquecounts(rows)
    imp = 0
    for k1 in counts:
        p1 = float(counts[k1]) / total
        for k2 in counts:
            if k1 == k2: continue
            p2 = float(counts[k2]) / total
            imp += p1 * p2
    return imp


# Entropy is the sum of p(x)log(p(x)) across all
# the different possible results
def entropy(rows):
    """
    返回rows的当前熵
    :param rows:
    :return:
    """
    from math import log
    log2 = lambda x: log(x) / log(2)
    results = uniquecounts(rows)
    # Now calculate the entropy
    ent = 0.0
    for r in results.keys():
        p = float(results[r]) / len(rows)
        ent = ent - p * log2(p)
    return ent


def buildtree(rows, scoref=entropy):
    if len(rows) == 0:
        print '样本为空'
        return decisionnode()
    # rows的类别熵
    current_score = scoref(rows)

    # Set up some variables to track the best criteria
    # 定义一些变量用来记录最佳拆分条件
    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(0, column_count):
        # Generate the list of different values in
        # this column
        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        # Now try dividing the rows up for each value
        # in this column
        # 接下来根据这一列中的每个值，尝试对数据集进行拆分
        for value in column_values.keys():
            (set1, set2) = divideset(rows, col, value)

            # Information gain
            p = float(len(set1)) / len(rows)
            # Gain(X)=H(C)-H(C|X)=H(C)-p
            gain = current_score - p * scoref(set1) - (1 - p) * scoref(set2)
            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)
    # Create the sub branches
    if best_gain > 0:
        trueBranch = buildtree(best_sets[0])
        falseBranch = buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0], value=best_criteria[1],
                            tb=trueBranch, fb=falseBranch)
    else:
        # 拆分结束
        return decisionnode(results=uniquecounts(rows))


def printtree(tree, indent=''):
    # Is this a leaf node?
    if tree.results != None:
        print str(tree.results)
    else:
        # Print the criteria
        print str(tree.col) + ':' + str(tree.value) + '? '

        # Print the branches
        print indent + 'T->',
        printtree(tree.tb, indent + '  ')
        print indent + 'F->',
        printtree(tree.fb, indent + '  ')


def prune(tree, mingain):
    # If the branches aren't leaves, then prune them
    if tree.tb.results == None:
        prune(tree.tb, mingain)
    if tree.fb.results == None:
        prune(tree.fb, mingain)

    # If both the subbranches are now leaves, see if they
    # should merged
    if tree.tb.results != None and tree.fb.results != None:
        # Build a combined dataset
        tb, fb = [], []
        for v, c in tree.tb.results.items():
            tb += [[v]] * c
        for v, c in tree.fb.results.items():
            fb += [[v]] * c

        # Test the reduction in entropy
        delta = entropy(tb + fb) - (entropy(tb) + entropy(fb) / 2)

        if delta < mingain:
            # Merge the branches
            tree.tb, tree.fb = None, None
            tree.results = uniquecounts(tb + fb)


def classify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        branch = None
        if isinstance(v, int) or isinstance(v, float):
            if v >= tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        else:
            if v == tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        return classify(observation, branch)


if __name__ == '__main__':
    # result = divideset(my_data, 2, 'yes')
    # print result

    tree = buildtree(my_data)
    # printtree(tree)

    prune(tree, 1.0)
    printtree(tree)
