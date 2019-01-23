# -*- coding: utf-8 -*-

#  python 3

import json
import time
import datetime
import random
import os
import re
import requests
import sys


def use_proxy(url):     
    response = requests.get(url)
    #print(response.content)
    if response.status_code == 200:
        proxy_status,data = 200 , response.content
    else:
        print("use_proxy Failtured response.status_code = %s"%response.status_code)
        proxy_status,data = response.status_code,"{}" 
    return  proxy_status,data

#获取微博主页的containerid，爬取微博内容时需要此id
def get_containerid(url):
    proxy_status,data = use_proxy(url)
    if proxy_status != 200:
        return 0
    content=json.loads(data).get('data')
    tabs = content.get('tabsInfo').get('tabs')
    for data in tabs:
        if(data.get('tab_type')=='weibo'):
            containerid=data.get('containerid')
    return containerid 

def get_ShortName(filename):    #文件名太长,截断
    fn = ""
    fl = filename.split('\n')
    for l in fl:
        fn = fn + l.strip()
    if len(fn)>50:
        return fn[:50]
    else:
        return fn
    
def init_UrlInfor(uid,page):    
    url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+ uid
    containerid = get_containerid(url)
    if containerid == 0 :
        print("init_UrlInfor Error containerid!")
        return ("","")
    weibo_url="https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=%s&page=%s"%(uid,str(containerid),str(page))
    print(weibo_url)
    return (url,weibo_url)

def download_video(video_name,stream_url):
    print(u"%s downloading ......"% datetime.datetime.now().strftime('[%H:%M:%S]'))
    stime = time.perf_counter()
    #status, content = url_open(url)
    #if status == 200:                            
    #browser.get(stream_url)
    response = requests.get(stream_url)
    if response.status_code == 200:
        fn = open(video_name,'wb')
        fn.write(response.content)
        fn.close()
    else:
        print("download Failtured response.status_code = %s"%response.status_code)
        return 0
    etime = time.perf_counter()
    tt = stime - etime
    print(u"%s downloaded  耗时: %.2f 秒\n"% (datetime.datetime.now().strftime('[%H:%M:%S]'),tt))

def get_ParentDirName(cards,uid):
    mblog0 = cards[0].get("mblog")
    user = mblog0.get("user") 
    screen_name = user["screen_name"].strip().replace(" ","")
    #description = re.sub('[\/:*?"<>|，：、]','_',user["description"]).replace(" ","")
    dirName =  u"%s/%s_%s"%(os.curdir,uid,screen_name)
    print ("dirName=%s"%dirName)
    return dirName

def filter_Non_BMP_Characters(target):    
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    name=target.translate(non_bmp_map)
    return name

def format_createdDate(targetDate):
    create_at   = targetDate
    if create_at.find("小时前") != -1 : # 最近二天 格式
        before_hours = int( create_at.split("小")[0] )
        create_at = (datetime.datetime.now()+datetime.timedelta(hours= -before_hours )).strftime("%Y-%m-%d")
    elif create_at.find("分钟前")!= -1:
        create_at = datetime.datetime.now().strftime("%Y-%m-%d")
    elif create_at.find("昨天") != -1 :
        create_at = (datetime.datetime.now()+datetime.timedelta(days= -1 )).strftime("%Y-%m-%d")
    else:
        which = create_at.split('-')
        if(len(which) == 2 ):      # 今年的 都是 '11-09' 之类的格式         
            year = time.strftime('%Y',time.localtime(time.time()))
            create_at = "%s-%s"%(year,create_at)
        elif(len(which)== 3 ):    # 去年的  都是 '2017-11-09' 之类的格式
            pass
        else:
            pass
    return create_at

def get_detailContent(detail_url):
    try:
        proxy_status,data = use_proxy(detail_url) 
        if not data.find('微博正文 - 微博HTML5版'):
            return ''
        content = json.loads(data).get('data')
        longTextContent=content.get('longTextContent')
        return longTextContent
    except Exception as e:
        print(e)
        return ''
 
def download_video(video_name,stream_url):
    print(u"%s downloading ......"% datetime.datetime.now().strftime('[%H:%M:%S]'))
    stime = time.perf_counter()
    response = requests.get(stream_url)
    if response.status_code == 200:
        fn = open(video_name,'wb')
        fn.write(response.content)
        fn.close()
    else:
        print("download Failtured response.status_code = %s"%response.status_code)
        return 0
    etime = time.perf_counter()
    tt = stime - etime
    print(u"%s downloaded  耗时: %.2f 秒\n"% (datetime.datetime.now().strftime('[%H:%M:%S]'),tt))

def download_pictures(data,cur_dir):
    count = 0
    try:
        try:
            curWeiboId = data["id"]
            img_text = ""                    
            pics = []
            pics = data.get("pics")
            pic_count = len(pics)
        except Exception as e:
            print(e)
            return
        
        print("发现微博中有 %s 图片------"%pic_count)
        created_at   = data.get("created_at")
        created_at= format_createdDate(created_at)      
        for picIndex in range(pic_count):
            cur_pid = pics[picIndex]["pid"]
            cur_pic_large_url = pics[picIndex].get("large")["url"]
            cur_pic_extensionName = cur_pic_large_url.split(".")[-1]
            cur_pic_Name = cur_pic_large_url.split("/")[-1]
            picName = u"%s/%s"%(cur_dir,cur_pic_Name)
            if os.path.exists(picName):
                print("当前文件已存在!")
                continue            
            print(u"开始下载     :  第%s张图片"%(picIndex+1))
            stime = time.perf_counter()
            print(u"%s downloading ......"% datetime.datetime.now().strftime('[%H:%M:%S]'))
            print("%s"%cur_pic_large_url)                            
            response = requests.get(cur_pic_large_url)
            if response.status_code == 200:
                fn = picName
                with open( fn , 'wb') as f:  # 以二进制写入到本地
                    f.write(response.content)
                    f.close()              
            etime = time.perf_counter()
            times = etime - stime
            print(u"%s downloaded  耗时: %.2f 秒\n"% (datetime.datetime.now().strftime('[%H:%M:%S]'),times))
            count = count + 1    #下载总数
            
    except Exception as e:
        print(e)

        
def waiting_times(judge,times = None):
    sleeptime = 0
    if times == None:
        sleeptime = random.randint(1,5)
    if( judge % 3 == 0):     
        time.sleep(sleeptime)
    
def get_WeiboAllPostsByUID(uid):
    count = 0
    cur_page= 0
    while True:
        print("\n")
        cur_page = cur_page + 1
        url,weibo_url = init_UrlInfor(uid,cur_page)
        try:
            proxy_status,data = use_proxy(weibo_url)
            if weibo_url == "":
                print("搜罗完毕")
                break
            if proxy_status != 200:
                continue            
            ok   = int(json.loads(data)['ok'])
            if ok == 0 :
                print("At %s  %s "%(cur_page,json.loads(data)["msg"]))
                continue            
            content = json.loads(data).get('data')            
            cards=content.get('cards')
            cards_len = len(cards)
            print("cards_len=%s"%cards_len) 
            if(cards_len>0):                
                dirName = get_ParentDirName(cards,uid)
                if not os.path.exists(dirName):
                    os.mkdir(dirName)
                    print("创建根目录: %s"%dirName)                    
                for card_index in range(cards_len):                     
                    print("\n-----正在下载第"+str(cur_page)+"页，第"+str(card_index+1)+"条微博------")
                    card_type=int(cards[card_index]['card_type'])
                    if(card_type==9):
                        mblog=cards[card_index].get('mblog')                        
                        dir_idstr = mblog["idstr"]
                        create_at   = mblog["created_at"]
                        create_at  = format_createdDate(create_at)
                        sub_dir = "%s/%s"%(dirName,create_at)
                        if not os.path.exists(sub_dir):
                            os.mkdir(sub_dir)
                        #### 判断以前下载历史 检测是否重复 
                        judge_weibo  = "%s/%s"%(sub_dir,dir_idstr)
                        if os.path.exists(judge_weibo):
                            to_choose = 1 # input("该条微博内容已下载[id = %s]过了\n[继续请输入1，退出请输输0]"%dir_idstr)
                            if int(to_choose)== 1 :
                                continue
                            else:
                                return True
                        else:
                            os.mkdir(judge_weibo)
                        #### 提取微博文本    
                        cur_dir = judge_weibo # 当前目录 
                        isLongText = bool(mblog.get('isLongText'))
                        idstr = mblog.get('idstr')
                        if (not isLongText):
                            text=mblog.get('text')
                        else:                            
                            detail_url = 'https://m.weibo.cn/statuses/extend?id=%s'% str(idstr)
                            text = get_detailContent(detail_url)
                        if len(text)<=0:
                            text = ""
                        else:
                            #To save text
                            text = filter_Non_BMP_Characters(text)
                            ftxt = "%s/content.txt"%cur_dir
                            print(ftxt)
                            fp = open(ftxt,"w+",encoding='utf-8')  
                            fp.write(text)
                            fp.close()
                            print("文本摘要：%s"%get_ShortName(text))
                        ##### 含有图片
                        if "pics" not in mblog:
                            #print("-----当前微博中没有  原创图片")
                            if "retweeted_status" in mblog:
                                print("发现  转载图片")
                                download_pictures(mblog.get("retweeted_status"),cur_dir)                 
                        else:                          
                            download_pictures(mblog,cur_dir)  
                        ##### 含有视频
                        if "page_info" in mblog:
                            page_info = mblog["page_info"]
                            media_type = page_info["type"]  #类型 作 扩展名 
                            if media_type == "video":
                                print("发现视频 开始下载")
                                content2 =re.sub('[\/:*?"<>|，：、？]','_', page_info["content2"]).replace(" ","")
                                content2 = filter_Non_BMP_Characters(content2)
                                shortname = get_ShortName(content2)
                                stream_url = page_info.get("media_info")["stream_url"]
                                video_name = "%s/%s.%s"%(cur_dir,idstr,media_type)
                                if os.path.exists(video_name):
                                    print("已下载过了%s"%(video_name.split("/")[-1]))
                                    continue
                                print("发现视频 开始下载%s"%stream_url)
                                download_video(video_name,stream_url)                
                        
                        #### While 循环内
                        count = count + 1    #更新下载总数
                        waiting_times(cur_page)        
            
        except Exception as e:
            print(e)
            break                  
    print('\n>>>>>>>>>>>>>>>>>>>')
    print('下载微博条数共计：%s'%count)                         

     
def main():     
    id_list = ['1989534434']   
    for uid in id_list:
        #url,weburl = init_UrlInfor(uid,1)
        #return
        get_WeiboAllPostsByUID(uid)
        return
        
    
if __name__=="__main__":
    main()



    

