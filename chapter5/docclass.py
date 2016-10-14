# encoding=utf-8

import re
import math
import MySQLdb
import warnings

warnings.filterwarnings("ignore")


def getwords(doc):
    splitter = re.compile('\\W*')  # 非单词字符组成的串
    print doc
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]

    # Return the unique set of words only
    return dict([(w, 1) for w in words])


class classifier:
    def __init__(self, getfeatures):
        # Counts of feature/category combinations
        self.fc = {}
        # Counts of documents in each category
        self.cc = {}
        self.getfeatures = getfeatures

    # cc是类别表，cf是特征分类表
    def setdb(self, dbfile):
        self.conn = MySQLdb.Connect(host='127.0.0.1', user='root', passwd='poiu1234', port=3306, db=dbfile)
        self.cursor = self.conn.cursor()
        try:
            # 特征，特征类型，特征-类型 出现次数
            self.cursor.execute('create table if not exists fc(feature varchar(20),category varchar(20),count int(11))')
            # 特征类型， 出现次数（邮件的分类数）
            self.cursor.execute('create table if not exists cc(category varchar(20),count int(11))')
            self.conn.commit()
        except Exception as e:
            print 'Error:', e
            raise

    def incf(self, f, cat):
        count = self.fcount(f, cat)
        if count == 0:
            self.cursor.execute("insert into fc values ('%s','%s',1)"
                                % (f, cat))
        else:
            self.cursor.execute(
                "update fc set count=%d where feature='%s' and category='%s'"
                % (count + 1, f, cat))

    def fcount(self, f, cat):
        self.cursor.execute(
            'select count from fc where feature="%s" and category="%s"'
            % (f, cat))
        res = self.cursor.fetchone()
        if res == None:
            return 0
        else:
            return float(res[0])

    def incc(self, cat):
        count = self.catcount(cat)
        if count == 0:
            self.cursor.execute("insert into cc values ('%s',1)" % (cat))
        else:
            self.cursor.execute("update cc set count=%d where category='%s'"
                                % (count + 1, cat))

    def catcount(self, cat):
        self.cursor.execute('select count from cc where category="%s"'
                            % (cat))
        res = self.cursor.fetchone()
        if res == None:
            return 0
        else:
            return float(res[0])

    def categories(self):
        self.cursor.execute('select category from cc')
        return [d[0] for d in self.cursor.fetchall()]

    # 返回邮件的总数量
    def totalcount(self):
        self.cursor.execute('select sum(count) from cc')
        res = self.cursor.fetchone();
        if res == None: return 0
        return res[0]

    def train(self, item, cat):
        features = self.getfeatures(item)
        # Increment the count for every feature with this category
        for f in features:
            self.incf(f, cat)

        # Increment the count for this category
        self.incc(cat)
        self.conn.commit()

    # 特征feature在cat类中出现的概率
    def fprob(self, f, cat):
        if self.catcount(cat) == 0: return 0

        # The total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f, cat) / self.catcount(cat)

    def weightedprob(self, f, cat, prf, weight=1.0, assumedprob=0.5):
        # Calculate current probability
        basicprob = prf(f, cat)

        # Count the number of times this feature has appeared in
        # all categories(邮件总数)
        totals = sum([self.fcount(f, c) for c in self.categories()])

        # Calculate the weighted average
        bp = ((weight * assumedprob) + (totals * basicprob)) / (weight + totals)
        return bp


# 训练样本导入分类器
def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')


class naivebayes(classifier):
    def docprob(self, item, cat):
        features = self.getfeatures(item)

        # 将所有特征的概率相乘
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        # cat类型的邮件数量/总数量 Pr(Category)
        catprob = self.catcount(cat) / self.totalcount()
        # item各feature在cat类型邮件中出现的概率 Pr(Document|Category)
        docprob = self.docprob(item, cat)
        # item各feature属于cat类型的概率  Pr(Category|Document)=Pr(Document|Category)*Pr(Category) /Pr(Document)
        return docprob * catprob


def naiveclassifier_train():
    c1 = classifier(getwords)
    c1.setdb('classifier')
    # 这是一个正式邮件
    c1.train('the quick brown fox jumps over the lazy dog', 'good')
    # 这是一个垃圾邮件
    c1.train('make quick money in the online casino', 'bad')
    print c1.fcount('quick', 'good')
    print c1.fcount('quick', 'bad')

    # sampletrain(c1)
    # print c1.fprob('quick', 'good')

    c1 = classifier(getwords)
    sampletrain(c1)
    print c1.weightedprob('money', 'good', c1.fprob)

    sampletrain(c1)
    print c1.weightedprob('money', 'good', c1.fprob())


if __name__ == '__main__':
    c1 = naivebayes(getwords)
    sampletrain(c1)
    # Pr(Category|Document) = Pr(Document|Category)*Pr(Category) / Pr(Document)
    print c1.prob('quick rabbit', 'good')
    print c1.prob('quick rubbit', 'bad')
