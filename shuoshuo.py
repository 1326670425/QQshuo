# -*- coding: utf-8 -*-
from selenium import webdriver
from pyecharts import Bar
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
import csv
import jieba
import re
#登录
def login(qq_number):
    driver.get('http://user.qzone.qq.com/{}/311'.format(qq_number))
    time.sleep(5)
    try:
        driver.find_element_by_id('login_div')
        driver.switch_to.frame('login_frame')
        #选择本机登录的QQ，xxxxxxxx为QQ号
        driver.execute_script('document.getElementById("img_out_xxxxxxxx").click();')
        flag = True
    except:
        flag = False
    return flag
#爬取
def spider():
    finish = False
    i = 0
    driver.switch_to.frame('app_canvas_frame')
    #data存储说说时间和内容
    data = []
    while(not finish):
        content = driver.find_elements_by_css_selector('.content')
        #精确定位，避免当转发说说时，获取到两个时间
        stime = driver.find_elements_by_css_selector('div.box.bgr3>div.ft>div.info>span.c_tx3>.c_tx.c_tx3.goDetail')
        for con,sti in zip(content,stime):
            data.append([sti.get_attribute('title'),con.text.replace('\n','  ')])
        #尝试翻页操作
        try:
            js = 'document.getElementById("pager_next_{}").click();'.format(i)
            driver.execute_script(js)
            time.sleep(3)
            finish = True
            i += 1
        except:
            finish = True
    
    driver.close()
    driver.quit()
    return data
#转存为csv文件
def save_to_csv(path,data):
    with open(path,'w',newline = '',encoding = 'utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['时间','内容'])
        for i in range(len(data)):
            writer.writerow(data[i])
#词频分析
def word_analyze(words):
    s = ''
    for each in words:
        s += each
    seg = jieba.cut(s.strip())
    str_list = "/".join(seg)
    my_word_list = []
    f_stop_seg_list = []
    #停用词位置自选
    with open('../stopword.txt','r',encoding='utf-8') as f:
        for line in f.readlines():
            f_stop_seg_list.append(line.strip())

    for myword in str_list.split('/'):
        if not(myword.strip() in f_stop_seg_list) and len(myword.strip())>1:
            my_word_list.append(myword)

    word_freq = {}  
    for word in my_word_list:  
        if word in word_freq:  
            word_freq[word] += 1  
        else:  
            word_freq[word] = 1  
    freq_word = []  
    for word, freq in word_freq.items():  
        freq_word.append((word, freq))  
    freq_word.sort(key = lambda x: x[1], reverse = True)  
  
    max_number = 30      # 设置高频词数

    top = []
    for word, freq in freq_word[: max_number]:  
        print(word, freq)
        top.append(word)
    
    content_text = " ".join(my_word_list)
    font = 'C:\Windows\Fonts\simfang.ttf'
    wordcloud = WordCloud(font_path=font,max_words=max_number,width=1400,height=1000,collocations=False,margin=2).generate(content_text)
    plt.figure()
    plt.imshow(wordcloud,interpolation='bilinear')
    plt.axis('off')
    plt.show()
def time_analyze(time_list):
    stime = []
    for each in time_list:
        print(each)
        stime.append(re.search('\d{1,2}:\d{2}', each).group())
    clock = []
    for i in range(24):
        clock.append([i,0])
    for each in stime:
        n = int(each.split(':')[0])
        clock[n][1] += 1
    s = [clock[i][0] for i in range(len(clock))]
    c = [clock[i][1] for i in range(len(clock))]

    bar = Bar("一天各个时间段说说数")
    bar.add("说说条数",s,c,is_stack=True,mark_line=["min", "max"],mark_point=["average"])
    bar.render()
    
if __name__ == '__main__':
    qq_number = input('输入待爬的QQ号：')
    driver = webdriver.Ie()
    if login(qq_number):
        driver.implicitly_wait(5)
        result = spider()
        #时间段活跃分析
        time_list = [row[0] for row in result]
        time_analyze(time_list[1:])
        
        words = [row[1] for row in result]
        #剔除第一行标题
        word_analyze(result[1][1:])
        path = qq_number+'.csv'
        save_to_csv(path,result)
