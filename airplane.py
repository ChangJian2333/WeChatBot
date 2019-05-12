# encoding:utf-8
import urllib
import requests
import re
from bs4 import BeautifulSoup as bs
import time
from urllib import request
import socket
import jieba
import math
import chardet
import nltk
from selenium import webdriver

# 获得网页总数
def getPage(key_words):
    # *******动态抓取网页，返回当前url*******
    url = 'http://search.sina.com.cn/'
    browser = webdriver.Firefox()
    browser.get(url)
    input = browser.find_element_by_xpath('/html/body/div/div[2]/div[3]/form/div/input[1]') # 查找输入框
    input.send_keys(key_words)
    button = browser.find_element_by_xpath('/html/body/div/div[2]/div[3]/form/div/input[4]') # 查找搜索按钮
    button.click() # 发送请求
    current_url = browser.current_url # 获得当前页面的url
    browser.quit()
    b = current_url.split('&')[0]+'&range=title&c=news&sort=time&col=&source=&from=&country=&size=&time=&a=&page=1'
    html = requests.get(b).text
    html = html.encode('utf-8').decode('utf-8')
    soup = bs(''.join(html))
    a = soup('div',{'class':'l_v2'})
    c = ""
    race = str(a).split('新闻')[1].split('篇')[0]  # 获取网址有多少页码
    if len(race)<3:
        count = int(race)
    else:
        count = int(''.join(race.split(',')))
    a1 = int(count / 20)
    new_url = []
    for j in range(a1):
        new_url.append(b+str(j+1))
    return new_url

# 获取搜索界面的新闻url
def getcontenthtmls(url):
    html = requests.get(url).text
    soup = bs(''.join(html))
    a = soup('h2')
    b = [str(each).split('"')[1] for each in a] # 获取新闻的url
    return b

# 进入指定新闻获取内容
def getcontents1(url):
    try:
        html = urllib.request.Request(url)  # 发出请求
        response = urllib.request.urlopen(html)  # 爬取结果
        data = response.read()
        typeDeter = chardet.detect(data)['encoding'] # 判断编码格式
        data = data.decode(typeDeter)
        soup = bs(data)
        # title1 = re.findall('<title>(.*?)</title>',data,re.S)[0].split('|')[0]
        title = soup('title')[0].get_text().split('|')[0]
        description0 = soup('meta',{'name':'description'})
        if len(description0)>0:
            description = str(description0).split('"')[1]  # 获取描述内容
        else:
            description = ''
        contentnew1 = soup('div', {'class': 'article'}) # 获取新闻内容
        contentnew2 = soup('div',{'class':'content'})
        contentnew3 = soup('div',{'class':'blkContainerSblkCon'})
        contentnew4 = re.findall('<div><p>(.*?)<div id="left_hzh_ad">',data,re.S)
        if len(contentnew1)>0:
            contentnew = contentnew1[0].get_text()
        elif len(contentnew2)>0:
            contentnew = contentnew2[0].get_text()
        elif len(contentnew3)>0:
            contentnew = contentnew3[0].get_text()
        elif len(contentnew4)>0:
            contentnew = contentnew4[0].get_text()
        else:
            contentnew = description
        keyword1 = soup('meta', {'name': 'keywords'})  # 获取关键词
        if len(keyword1)>0:
            keyword = str(keyword1).split('"')[1]
        else:
            keyword = ','.join(ContentAnalysis(contentnew)[1])
        time1 = re.findall('<meta name="weibo: article:create_at" content="(.*?)" />',data,re.S)
        time2 = re.findall('<meta property="article:published_time" content="(.*?)" />',data,re.S)
        time3 = re.findall('<em>(.*?)</em>',data,re.S)
        time4 = soup('span',{'id': 'pub_date'})
        if len(time1)>0:
            time = time1[0]
        elif len(time2)>0:
            time = time2[0].split('T')[0]+time2[0].split('+')[0].split('T')[1]
        elif len(time3)>0:
            time = time3[0]
        elif len(time4)>0:
            time = str(time4).split('>')[1].split('<')[0]
        else:
            time = 'error'
            fp = open('timError.txt', 'a')
            fp.writelines(url + '\n')
            fp.close()
        response.close()
        return title,time,url,keyword,description,contentnew
    except UnicodeDecodeError or IndexError:
        fp = open('typError.txt', 'a')
        fp.writelines(url + '\n')
        fp.close()
        pass

# ***计算新闻文本内容中与自然语言的相关度***
def ContentAnalysis(content,keywords=[],Nlpwords=[],Num=[]):
    numch = '1234567890poiuytrewqasdfghjklmnbvcxz'
    content0 = [w for w in jieba.cut(content) if w not in stopword] # 先分词并过滤一部分停用词
    stopword1 = []  # 根据文本内容新增的停用词
    # 根据文本内容自动生成该文本中一些纯数字纯字母和数字字母自合，但若出现有大写字母的英文字串保留在文本中
    for each in content0:
        each1 = [w for w in each if w in numch]
        each1 = ''.join(each1)
        if len(each1) > 0 and each1 not in stopword1:
            stopword1.append(each1)
    content1 = [w for w in content0 if w not in stopword1] # 再次过滤掉文本中的一些词语，如：http,123aef等无意义字符串
    # 计算词频
    wordict = {} # 存放词语及对应频数
    for each in content1:
        if each in wordict.keys():
            wordict[each] += 1
        else:
            wordict.setdefault(each,1)
    # 计算文本中自然语言相关词语所占比例
    d = sorted(wordict.items(),key=lambda item:item[1])[-3:] # 取出前词频最高的3个词语
    keyword = [w[0] for w in d] # 取出前词频最高的3个词语，作为文章的关键字
    if Num:
        Nlpword = ['自然语言','NLP','自然语言处理','Natural Language Processing','Natural Language','文本挖掘','文本分析','学习词汇'] # 可自行添加觉得相关的词语
    else:
        Nlpword = keywords
    Nlpcount = 0 # 用于存放文本中含有与自然语言相关词语的数量
    for each in wordict.keys():
        if each in Nlpword:
            Nlpcount += wordict[each]
    if sum(wordict.values())>0:
        NlpwordP = Nlpcount/sum(wordict.values()) # 计算与自然语言相关的词语占文本中的频率
    else:
        NlpwordP = 0
        print('新闻内容抓取失败')
    return NlpwordP,keyword

#  定义新闻与自然语言处理的相关度：标题、关键词和文本内容各占一定权重
def newsAnalysis(content,title,keyword,key_words):
    keywords = [w for w in jieba.cut(key_words) if w not in stopword]
    Nlpwords = ['自然语言', 'NLP', '自然语言处理', '自然语言识别']
    Num = [1 for each in keywords if each in Nlpwords]
    if Num:
        Nlpword = ['自然语言','NLP','自然语言处理','自然语言识别']
    else:
        Nlpword = key_words
    contentP = ContentAnalysis(content,keywords,Nlpwords,Num)[0] # 新闻内容中自然语言相关词语所占比
    titlelist = [w for w in jieba.cut(title) if w not in stopword]
    titleP = [1 for each in titlelist if each in Nlpword] # 如果标题中有自然语言相关字样出现，赋值1
    keyword = keyword.split(',') # keyword中有多个词语
    keywordP = [1 for each in keyword if each in Nlpword]
    if len(titleP)>0 and len(keywordP)>0:
        KT_W = 0.8
    elif len(titleP)>0:
        KT_W = 0.7
    elif len(titleP)>0:
        KT_W = 0.6
    else:
        KT_W = 0
    # ***两种计算方式
    # PnewNlp = KT_W +0.20*(1/(1+math.exp(-contentP)))
    PnewNlp = 1/(1+math.exp(-KT_W)) + 0.20 * (1/(1 + math.exp(-contentP)))
    return PnewNlp

# ***从内容中生成摘要***
def getText(content):
    numch = '1234567890poiuytrewqasdfghjklmnbvcxzQWERTYUIOPLKJHGFDSAZXCVBNM/<>"=.-:_{} '
    content1 = [w for w in jieba.cut(content)] # 分词
    stopword1 = ['\t','\n'] # 生成动态停用词，剔除抓取内容中的url、HTML格式
    for each in content1:
        each1 = [w for w in each if w in numch]
        each1 = ''.join(each1)
        if len(each1) > 0 and each1 not in stopword1:
            stopword1.append(each1)
    content2 = ''.join([w for w in content1 if w not in stopword1]) # 剔除内容中无用的词语，如:'123reg','rghsdjfv','12345'
    if len(content2)<20:
        content2 = ''
    return content2

# 分句
def sent_tokenizer(texts):
    start1 = 0
    sentences,text1 = [],[]
    punt_list = '.!?。？！，'.encode('utf-8')
    punt_list = punt_list.decode('utf-8')
    # 一句为一个字符存储，如：'我是四川人，但我在昆明'切分为'我是四川人','但我在昆明'
    for j in range(len(texts)):
        if j != len(texts)-1:
            if texts[j] in punt_list and texts[j+1] not in punt_list: # 检查标点符号下一个字符是否还是标点
                sentences.append(texts[start1:j+1]) # 当前标点符号位置
                start2 = j + 1 # start标记到下一句的开头
        else:
            sentences.append((texts[start1:j])) #最后一句话加入
    return sentences

#句子得分
def score_sentences(sentences,topn_words):
    CLUSTER_THRESHOLD = 5  # 单词间的距离
    scores = []
    sentence_idx = -1
    for s in [list(jieba.cut(s)) for s in sentences]:
        sentence_idx += 1
        word_idx = []
        for w in topn_words:
            try:
                word_idx.append(s.index(w)) # 关键词出现在该句子中的索引位置
            except ValueError: # w不在句子中
                pass
        word_idx.sort()
        if len(word_idx) == 0:
            continue
        # 对于两个连续的单词，利用单词位置索引，通过距离阀值计算族
        clusters = []
        cluster = [word_idx[0]]
        i = 1
        while i<len(word_idx):
            if word_idx[i]-word_idx[i-1] < CLUSTER_THRESHOLD:
                cluster.append(word_idx[i])
            else:
                clusters.append(cluster[:])
                cluster = [word_idx[i]]
            i+=1
        clusters.append(cluster)
        # 对每个族打分，每个族类的最大分数是对句子的打分
        max_cluster_score = 0
        for c in clusters:
            significant_words_in_cluster = len(c)
            total_words_in_cluster = c[-1]-c[0]+1
            score = 1.0*significant_words_in_cluster*significant_words_in_cluster/total_words_in_cluster
            if score > max_cluster_score:
                max_cluster_score = score
        scores.append((sentence_idx,max_cluster_score))
    return scores

# 摘要
def summarizeText(text,keywords):
    TOP_SENTENCES = 5  # 返回的top n句子
    N = 20 # 取文本中
    sentences = sent_tokenizer(text)
    words = [w for sentence in sentences for w in jieba.cut(sentence) if w not in stopword if len(w) > 1 and w != '\t']
    wordfre = nltk.FreqDist(words)
    topn_words = [w[0] for w in sorted(wordfre.items(), key=lambda d: d[1], reverse=True)][:N]
    for each in keywords:
        if each not in topn_words:
            topn_words.append(each)
    scored_sentences = score_sentences(sentences, topn_words)
    top_n_scored = sorted(scored_sentences,key = lambda s:s[1])[-TOP_SENTENCES:]
    top_n_scored = sorted(top_n_scored,key = lambda s:s[0])
    top_n_summary = ''.join([sentences[idx] for (idx, score) in top_n_scored])
    # ***输出的top_n_summary中存在一句完整的句子，直接输出一句完整的句子；
    # 如果top_n_summary中无完整的句子，直接输出top_n_summary；
    # 如果top_n_summary中有一句完整的句子，还有不完整的一句话，取完整的一句话，其他扔掉。***
    punt_list = '.。？！'.encode('utf-8').decode('utf-8')
    biaoDia = [1 for w in punt_list if w in top_n_summary] # 判断top_n_summary中是否存在完整句子
    abstract_w,start = [],0
    if biaoDia:
        for j in range(len(top_n_summary)):
            if j != len(top_n_summary)-1:
                if top_n_summary[j] in punt_list: # 检查标点符号下一个字符是否还是标点
                    abstract_w.append(top_n_summary[start:j+1]) # 当前标点符号位置
                    start = j + 1 # start标记到下一句的开头
            elif top_n_summary[j] in punt_list:
                abstract_w.append((top_n_summary[start:j]))
            else:
                pass
    else:
        abstract_w = top_n_summary
    return ''.join(abstract_w)

# ***描述内容处理
def descriCont(texts):
    punt_list = '.,?!。？！；，:：'.encode('utf-8').decode('utf-8')
    descriptionC,start = [],0
    for j in range(len(texts)):
        if j != len(texts) - 1:
            if texts[j] in punt_list:  # 检查标点符号下一个字符是否还是标点
                descriptionC.append(texts[start:j + 1])  # 当前标点符号位置
                start = j + 1  # start标记到下一句的开头
        elif texts[j] in punt_list:
            descriptionC.append((texts[start:j]))
        else:
            pass
    return ''.join(descriptionC)

if __name__ == '__main__':
    key_words = input('请输入关键字：')
    fp = open('stopword.txt', 'rb')
    stopword = fp.read().decode('utf-8')  # 提用词提取
    jieba.load_userdict('userdict.txt')  # 分词字典+'自然语言处理'
    url_list = getPage(key_words) # 获取搜索总页数
    socket.setdefaulttimeout(30)  # 设置socket层的超时时间为10秒
    # fp = open('newsNLP.txt','a')
    n = 0
    for each in url_list:
        newsurl = getcontenthtmls(each) # 一个页面所有新闻的url
        n += 1
        print('第%d页%s相关新闻爬取:'%(n,key_words))
        for url in newsurl:
            content = getcontents1(url) #一则新闻的标题，时间，url,关键词，内容
            if content:
                # fp.writelines('标题：'+content[0]+'\n'+'时间：'+content[1]+'\n'+'url： '+content[2]+'关键词：'+content[3]+'\n')
                # fp.writelines('描述内容：'+descriCont(content[4])+'\n'+'相似度：'+str(newsAnalysis(content[5],content[0],content[3],key_words))+'\n')
                # fp.writelines('摘要：'+str(summarizeText(str(getText(str(content[5]))),str(content[3])))+'\n')
                print('标题：' + content[0])
                print('时间：' + content[1])
                print('url:' + content[2])
                print('关键词:' + content[3])
                print('描述内容:' + descriCont(content[4]))
                print('摘要:'+ str(summarizeText(str(getText(str(content[5]))),str(content[3]))))
                print('相似度:'+ str(newsAnalysis(content[5],content[0],content[3],key_words)))
                print('\n')
            else:
                pass
            time.sleep(10)
        time.sleep(20)
    # fp.close()
