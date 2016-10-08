# coding=utf-8
import urllib
from bs4 import BeautifulSoup
import codecs
import jieba
from collections import Counter


# 获取当页所有博客的url，以list的方式返回
def get_all_urls(url):
    content = urllib.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')  # 利用beautifsoup进行html的解析
    url_dict = dict()
    for item in soup.find_all('ul', class_='list_009'):
        for i in item.find_all('li'):
            suburl = i.a['href']
            title = i.get_text()
            url_dict[title] = suburl

    return url_dict


# 输入博客的url，返回博客内容
def get_content(url):
    text = urllib.urlopen(url).read()
    soup = BeautifulSoup(text, 'lxml')
    main_content = soup.find('div', class_='articalContent')
    if main_content == None: return ''
    main_text = main_content.get_text()
    return main_text


if __name__ == '__main__':

    url_dict = dict()
    for i in range(1, 5):
        page = 'http://roll.finance.sina.com.cn/blog/blogarticle/cj-bkks/inde_' + str(i) + '.shtml'
        url_dict.update(get_all_urls(page))

    # 创建title,url存储文件
    title_file = codecs.open('data/title.txt', 'w', encoding='utf-8')

    # 循环处理每一篇文章
    id = 0
    blog_dict = {}  # 记录每个博客的单词统计，以及出现这些单词的数目
    for (title, url) in url_dict.items():
        id += 1
        # 按照id title url格式写入文件
        print str(id), title, url
        title_file.write(str(id) + '\t' + title + '\t' + url + '\n')

        # 通过博客url链接得到博客内容
        content = get_content(url).strip()
        filename = str(i) + '.txt'

        # utf8格式打开文档文件，存入每一篇博客内容
        file = codecs.open('data/' + filename, 'w', encoding='utf-8')
        file.write(content)
        file.close()

        # 利用结巴分词，对中文分词(False精确分词,True全分词)，获取标记词列表
        blog_dict[id] = {}
        for word in jieba.cut(content, cut_all=False):
            blog_dict[id].setdefault(word, 0)
            blog_dict[id][word] += 1

    nblogs = id
    # 记录出现单词的博客数目
    apcount = {}
    for wd in blog_dict.values():
        for word in wd:
            apcount.setdefault(word, 0)
            apcount[word] += 1

    wordlist = []

    # 记录所有有价值的分词
    for w, bc in apcount.items():
        frac = float(bc) / nblogs
        if frac > 0.05 and frac < 0.7: wordlist.append(w)

    out = codecs.open('data/blogdata.txt', 'w', encoding='utf-8')
    out.write('Blog')

    for word in wordlist: out.write('\t%s' % word)
    out.write('\n')

    for blogid, wc in blog_dict.items():
        out.write(str(blogid))
        for word in wordlist:
            if word in wc:
                out.write('\t%d' % wc[word])
            else:
                out.write('\t0')
        out.write('\n')
    out.close()
