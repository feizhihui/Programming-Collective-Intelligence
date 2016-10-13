# encoding=utf-8

from searchengine import *


class searcher:
    def __init__(self, dbname):
        self.conn = MySQLdb.Connect(host='127.0.0.1', user='root', passwd='poiu1234', port=3306, db=dbname)

    def __del__(self):
        self.conn.close()

    def getmatchrows(self, q):
        # 构造查询的字符串
        fieldlist = 'w0.urlid'
        tablelist = ' '
        clauselist = ''
        wordids = []

        # 根据空格拆分单词
        words = q.split(' ')
        tablenumber = 0

        cursor = self.conn.cursor()
        for word in words:
            # 获取单词的ID
            cursor.execute("select rowid from wordlist where word='%s'" % word)
            wordrow = cursor.fetchone()
            if wordrow != None:
                wordid = wordrow[0]
                wordids.append(wordid)
                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber - 1, tablenumber)
                fieldlist += ',w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
                tablenumber += 1

        # 根据各个组分，建立查询
        fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
        cursor.execute(fullquery)
        rows = [row for row in cursor.fetchall()]

        return rows, wordids


if __name__ == '__main__':
    e = searcher('searchindex')
    print e.getmatchrows('classname')
