# encoding=utf-8

import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import MySQLdb
import re

ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class crawler:
    # 初始化crawler类并传入数据库名称
    def __init__(self, dbname):
        self.conn = MySQLdb.Connect(host='127.0.0.1', user='root', passwd='poiu1234', port=3306, db=dbname)
        print self.conn

    def __del__(self):
        self.conn.close()

    def dbcommit(self):
        self.conn.commit()

    # 辅助函数,用于获取条目的id，并且如果条目不存在,就将其加入数据库中
    def getentryid(self, table, field, value, createnew=True):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select rowid from %s where %s='%s'" % (table, field, value))
            res = cursor.fetchone()
            if res == None:
                cursor.execute("insert into %s (%s) values ('%s')" % (table, field, value))
                return cursor.lastrowid
            else:
                return res[0]

        finally:
            self.dbcommit()
            cursor.close()

    # 为每个网页建立索引
    def addtoindex(self, url, soup):
        if self.isindexed(url): return
        print 'Indexing ' + url

        # 获取每个单词
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        # 得到url的id
        urlid = self.getentryid('urllist', 'url', url)

        # 将每个单词与该url关联
        try:
            cursor = self.conn.cursor()
            for i in range(len(words)):
                word = words[i]
                if word in ignorewords: continue
                wordid = self.getentryid('wordlist', 'word', word)
                cursor.execute('insert into wordlocation(urlid,wordid,location) \
                               values (%d,%d,%d)' % (urlid, wordid, i))
        finally:
            cursor.close()

        self.dbcommit()

    # 从一个HTML网页中提取文字(不带标签的)
    # 返回一个包含所有有效文字的长字符串
    def gettextonly(self, soup):
        v = soup.string
        # 含有子标签
        if v == None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    # 根据任何非空白字符进行分词处理
    def separatewords(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']

    # 如果url已经建立索引，则返回true
    def isindexed(self, url):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select rowid from urllist where url='%s'" % url)
            u = cursor.fetchone()

            if u != None:
                # 检查它是否已经被检索过了(是否与任何单词产生关联)
                cursor.execute("select * from wordlocation where urlid=%d" % u[0])
                v = cursor.fetchone()
                if v != None: return True
            return False
        except Exception as e:
            print 'Error:', e
            print "[ select rowid from urllist where url='%s' ]" % url
        finally:
            cursor.close()

    # 添加一个关联两个网页的链接
    def addlinkref(self, urlFrom, urlTo, linkText):
        pass

    # 从一小组网页开始进行广度优先搜索，直至某一给定深度，期间为网页建立索引
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print 'Could not open %s' % page
                    continue
                soup = BeautifulSoup(c.read(), 'html.parser')
                self.addtoindex(page, soup)
                # soup('a')
                links = soup.find_all('a')

                for link in links:

                    if ('href' in dict(link.attrs)):
                        # 拼接成完整域名
                        url = urljoin(page, link['href'])

                    if not self.isindexed(url):
                        newpages.add(url)

                    linkText = self.gettextonly(link)
                    self.addlinkref(page, url, linkText)

                self.dbcommit()
            pages = newpages

    # 创建数据库表
    def createindextables(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('create table urllist(rowid int(11) primary key auto_increment,url varchar(100))')
            cursor.execute('create table wordlist(rowid int(11) primary key auto_increment,word varchar(100))')
            cursor.execute(
                'create table wordlocation(rowid int(11) primary key auto_increment,urlid integer,wordid integer,location varchar(100))')
            cursor.execute('create table link(rowid int(11) primary key auto_increment,fromid integer,toid integer)')
            cursor.execute(
                'create table linkwords(rowid int(11) primary key auto_increment,wordid integer,linkid integer)')

            cursor.execute('create index wordidx on wordlist(word)')
            cursor.execute('create index urlidx on urllist(url)')
            cursor.execute('create index wordurlidx on wordlocation(wordid)')
            cursor.execute('create index urltoidx on link(toid)')
            cursor.execute('create index urlfromidx on link(fromid)')
        finally:
            cursor.close()
        self.dbcommit()

print 'import searchengine once'

if __name__ == '__main__':
    pagelist = ['http://www.nature.com/news']

    crawler = crawler('searchindex')
    crawler.createindextables()
    crawler.crawl(pagelist)
