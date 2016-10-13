# encoding=utf-8

from math import tanh
import MySQLdb
import time


class searchnet:
    def __init__(self, dbname):
        self.conn = MySQLdb.Connect(host='127.0.0.1', user='root', passwd='poiu1234', port=3306, db=dbname)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def maketables(self):
        try:
            self.cursor.execute(
                "create table hiddennode(rowid integer primary key auto_increment,create_key varchar(20))")
            self.cursor.execute(
                "create table wordhidden(rowid integer primary key auto_increment,fromid int,toid int,strength float)")
            self.cursor.execute(
                "create table hiddenurl(rowid integer primary key auto_increment,fromid int,toid int,strength float)")

            self.cursor.execute('create index hiddennode_index on hiddennode(create_key)')
            self.cursor.execute('create index index1 on wordhidden(fromid)')
            self.cursor.execute('create index index2 on wordhidden(toid)')
            self.cursor.execute('create index index1 on hiddenurl(fromid)')
            self.cursor.execute('create index index2 on hiddenurl(toid)')

            self.conn.commit()
        except Exception as e:
            print 'Error:', e
            raise

    # 判断当前连接的强度
    def getstrength(self, fromid, toid, layer):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'
        self.cursor.execute("select strength from %s where fromid=%d and toid=%d" % (table, fromid, toid))
        res = self.cursor.fetchone()
        if res == None:
            if layer == 0:
                return -0.2
            if layer == 1:
                return 0
        return res[0]

    # 更新连接或者创建连接 wordid, hiddenid, 0, 1.0 / len(wordids)
    def setstrength(self, fromid, toid, layer, strength):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'
        self.cursor.execute("select rowid from %s where fromid=%d and toid=%d" % (table, fromid, toid))
        res = self.cursor.fetchone()
        try:
            if res == None:
                self.cursor.execute(
                    "insert into %s (fromid,toid,strength) values (%d,%d,%f)" % (table, fromid, toid, strength))
            else:
                rowid = res[0]
                self.cursor.execute("update %s set strength=%f where rowid=%d" % (table, strength, rowid))
        except Exception as e:
            print 'Error:', e
            raise

        self.conn.commit()

    # 生成隐含层 wordids：[wWorld, wBank], urlsid：[uWorldBank, uRiver, uEarth]
    def generatehiddennode(self, wordids, urls):
        if len(wordids) > 3: return None
        # 检查我们是否已经为这组单词建好一个节点
        createkey = '_'.join(sorted([str(wi) for wi in wordids]))
        try:
            self.cursor.execute("select rowid from hiddennode where create_key='%s'" % createkey)
        except Exception as e:
            print 'Error:', e
            raise
        res = self.cursor.fetchone()

        # 如果没有，则建立之
        if res == None:
            try:
                self.cursor.execute("insert into hiddennode (create_key) values ('%s')" % createkey)
            except Exception as e:
                print 'Error:', e
                raise
            hiddenid = self.cursor.lastrowid
            # 设置默认权重
            for wordid in wordids:
                self.setstrength(wordid, hiddenid, 0, 1.0 / len(wordids))
            for urlid in urls:
                self.setstrength(hiddenid, urlid, 1, 0.1)
            self.conn.commit()

    # 寻找数据库中的隐藏层节点id
    def getallhiddenids(self, wordids, urlids):
        l1 = {}
        try:
            for wordid in wordids:
                self.cursor.execute(
                    'select toid from wordhidden where fromid=%d' % wordid)
                for row in self.cursor.fetchall(): l1[row[0]] = 1
            for urlid in urlids:
                self.cursor.execute(
                    'select fromid from hiddenurl where toid=%d' % urlid)
                for row in self.cursor.fetchall(): l1[row[0]] = 1
        except Exception as e:
            print 'Error:', e
        return l1.keys()

    def setupnetwork(self, wordids, urlids):
        # value lists
        self.wordids = wordids
        self.hiddenids = self.getallhiddenids(wordids, urlids)
        self.urlids = urlids

        # node outputs
        self.ai = [1.0] * len(self.wordids)
        self.ah = [1.0] * len(self.hiddenids)
        self.ao = [1.0] * len(self.urlids)

        # create weights matrix
        self.wi = [[self.getstrength(wordid, hiddenid, 0)
                    for hiddenid in self.hiddenids]
                   for wordid in self.wordids]
        self.wo = [[self.getstrength(hiddenid, urlid, 1)
                    for urlid in self.urlids]
                   for hiddenid in self.hiddenids]

    def feedforward(self):
        # the only inputs are the query words
        for i in range(len(self.wordids)):
            self.ai[i] = 1.0

        # hidden activations
        for j in range(len(self.hiddenids)):
            sum = 0.0
            for i in range(len(self.wordids)):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        # output activations
        for k in range(len(self.urlids)):
            sum = 0.0
            for j in range(len(self.hiddenids)):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(sum)

        return self.ao[:]

    # 模型的输出值
    def getresult(self, wordids, urlids):
        self.setupnetwork(wordids, urlids)
        return self.feedforward()

    # 计算误差 N代表学习率，更新权重时作为一个倍率，一般取（0.01,0.8）
    # 先更新输出节点和隐藏层节点的error值，再更新层与层之前的权重值
    def backPropagate(self, targets, N=0.5):
        # calculate errors for output
        output_deltas = [0.0] * len(self.urlids)
        for k in range(len(self.urlids)):
            error = targets[k] - self.ao[k]
            output_deltas[k] = dtanh(self.ao[k]) * error

        # calculate errors for hidden layer
        hidden_deltas = [0.0] * len(self.hiddenids)
        for j in range(len(self.hiddenids)):
            error = 0.0
            for k in range(len(self.urlids)):
                error = error + output_deltas[k] * self.wo[j][k]
            hidden_deltas[j] = dtanh(self.ah[j]) * error

        # update output weights
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                change = output_deltas[k] * self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N * change

        # update input weights
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                change = hidden_deltas[j] * self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N * change

    def trainquery(self, wordids, urlids, selectedurl):
        # generate a hidden node if necessary
        self.generatehiddennode(wordids, urlids)

        self.setupnetwork(wordids, urlids)
        self.feedforward()
        targets = [0.0] * len(urlids)
        targets[urlids.index(selectedurl)] = 1.0
        error = self.backPropagate(targets)
        self.updatedatabase()

    def updatedatabase(self):
        # set them to database values
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.setstrength(self.wordids[i], self.hiddenids[j], 0, self.wi[i][j])
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                self.setstrength(self.hiddenids[j], self.urlids[k], 1, self.wo[j][k])


# ========================================================================================================\
def dtanh(y):
    return 1.0 - y * y


def makeprepare(mynet):
    mynet.maketables()
    wWorld, wRiver, wBank = 101, 102, 103
    uWorldBank, uRiver, uEarth = 201, 202, 203
    mynet.generatehiddennode([wWorld, wBank], [uWorldBank, uRiver, uEarth])
    mynet.cursor.execute("select * from wordhidden")
    print 'wordhidden:'
    for c in mynet.cursor.fetchall(): print c
    mynet.cursor.execute("select * from hiddenurl")
    print 'hiddenurl'
    for c in mynet.cursor.fetchall(): print c


def makepredict(mynet, itera=30):
    wWorld, wRiver, wBank = 101, 102, 103
    uWorldBank, uRiver, uEarth = 201, 202, 203
    allurls = [uWorldBank, uRiver, uEarth]

    for i in range(itera):
        mynet.trainquery([uWorldBank, wBank], allurls, uWorldBank)
        mynet.trainquery([wRiver, wBank], allurls, uRiver)
        mynet.trainquery([wWorld], allurls, uEarth)

    print mynet.getresult([wWorld, wBank], allurls)
    print mynet.getresult([wRiver, wBank], allurls)
    print mynet.getresult([wBank], allurls)


if __name__ == '__main__':
    mynet = searchnet('nn')
    makeprepare(mynet)
    wWorld, wRiver, wBank = 101, 102, 103
    uWorldBank, uRiver, uEarth = 201, 202, 203
    # print mynet.getresult([wWorld, wBank], [uWorldBank, uRiver, uEarth])
    # 训练一个数据
    mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)

    # 求出一个词组与特定一组网页关联值
    print mynet.getresult([wWorld, wBank], [uWorldBank, uRiver, uEarth])
    t1 = time.clock()
    makepredict(mynet)
    t2 = time.clock()
    print 'read time:%f' % (t2 - t1)
