import requests
import time
import os
import re
# from ebooklib import epub
from tqdm import tqdm

Web_Headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40'}
# TODO ： 分安卓与苹果来输入Cookies
STRING_RENEW_CRED = "[?] renew your credential :[y/n(default)]"
STRING_ASSIGN_CRED = "[?] provide your credential(cookie) :"


class API():
    def __init__(self):
        self.book = ''
        self.Chapter = []
        self.Volume = []
        self.Novel_Name = ''
        self.Cookie = ''
        self.headers = {'Host': 'api.sfacg.com',
'Accept-Encoding': 'gzip, deflate, br',
'Connection': 'keep-alive',
'Accept': 'application/vnd.sfacg.api+json;version=1',
'User-Agent': 'boluobao/4.6.52(iOS;14.2)/appStore/80F83EC3-FFF0-4B69-81D4-6FE6EEE3616B',
'Accept-Language': 'zh-Hans-US;q=1, zh-Hant-TW;q=0.9',
'Authorization': 'Basic YXBpdXNlcjozcyMxLXl0NmUqQWN2QHFlcg=='}
        
    def get_cookie_security(self):
        if not os.path.exists('./config/cookie.conf'):
            if not os.path.exists('./config'):
                os.mkdir('./config')
            self.Cookie = input(STRING_ASSIGN_CRED)
            with open('./config/cookie.conf','w+') as fb:
                fb.write(self.Cookie)
            self.headers['Cookie'] = self.Cookie
        else:
            if input(STRING_RENEW_CRED) == 'y':
                self.Cookie = input(STRING_ASSIGN_CRED)
                with open('./config/cookie.conf','w+') as fb:
                    fb.write(self.Cookie)
                self.headers['Cookie'] = self.Cookie
                return 0

    def sign(self):
        result = requests.put("https://api.sfacg.com/user/signInfo", headers=self.headers)
        print(result.json()["status"]["msg"])

    def write_point(self,downloaded_list):
        # last_list 是指的当前小说的剩余章节     
        if not os.path.exists('./config'):
            os.mkdir('./config')
        with open('./config/' + self.Novel_Name + '.conf', 'a', encoding = 'utf-8') as fb:
            fb.write(str(downloaded_list))
    def check_point(self):
        # TODO : 检查最后一个下载点，并从最后一个下载点开始下载
        with open('./config/' + self.Novel_Name + '.conf', 'r', encoding = 'utf-8') as fb:
            last_str_list = fb.read()         
        return last_str_list

    def sort(self):
        # TODO ： 对不同类别的小说进行下载  
        pass
    
    def get_chapter(self,bookid = ''):
        self.book = bookid
        self.Volume = []
        # self.Division_Volume = {}
        if self.book == '':
            self.book = input("book's unique id")
        book_url = "http://book.sfacg.com/Novel/"+ self.book +"/MainIndex/"
        ## 编译正则表达式
        pattern_name = re.compile(r'<h1 class=["]story-title["]>(.*?)</h1>', re.M | re.S)
        pattern_div = re.compile(r'<h3 class="catalog-title">(.*?)</h3>', re.M | re.S)
        pattern_404 = re.compile(r'小说不存在')
        pattern_chapter = re.compile(r'<a href=(.*?) class=""')
        r = requests.get(book_url,headers = Web_Headers)
        if re.search(pattern_404,r.text) is not None:
            print("This book is invalid probably removed")
            return -1
        try:
            self.Novel_Name = re.findall(pattern_name, r.text)[0]
            self.Novel_Name = self.Novel_Name.replace("?", "")  # 防止 windows系统下无法创建文件问题
            self.Volume = re.findall(pattern_div, r.text)
            list_Chapters = []
            for i in re.findall(pattern_chapter, r.text):
                a = i.split('"')[1].split('/')[-2], i.split('"')[3]
                list_Chapters.append(a)
            self.Chapter = list_Chapters
        except:
            return -1

    def download(self):
        read_str_list = ''
        if os.path.exists('.//config//' + self.Novel_Name + '.conf'):
            read_str_list = self.check_point()
        if not os.path.exists('.//novel'):
            os.mkdir('.//novel')
        download_status = 0
        with open(".//novel//"+ self.Novel_Name + ".txt", 'a', encoding='utf-8') as fb:
            pbar = tqdm(self.Chapter)
            for i in pbar:
                pbar.set_description(desc = "<{}> {}".format(self.Novel_Name,i[-1]))
                # 判断当前章节是否已经被下载
                if i[0] in read_str_list:
                    # print("\t{}已经下载完成，跳过".format(j[-1]))
                    continue
                url = 'https://api.sfacg.com/Chaps/' + i[0] + '?chapsId=' + i[0] + '&expand=content%2Cchatlines%2Ctsukkomi%2CneedFireMoney%2CoriginNeedFireMoney'
                try:
                    result = requests.get(url, headers=self.headers)
                except Exception as err:
                    print(err)
                    continue
                if result.json()['status']['httpCode'] == 401:
                    download_status = 401
                    break
                else:
                    # TODO: 创建一个EPUB文件
                    text = '\n' + i[-1] + '\n' + result.json()["data"]["expand"]["content"]
                    fb.write(text)
                    # print("\t\t",j[-1],':已完成下载')
                    self.write_point(i[0] + '、')
                    time.sleep(0.2)
        if download_status == 401 :
            print("[!] Subscription is required to download this chapter, abort ...")

    def download_sort(self,num,sortid):
        # 返回 分类小说 的目录
        sort_list = []
        for i in range(num):
            result = requests.get("https://api.sfacg.com/novels/0/sysTags/" + sortid + "/novels?expand=typeName&filter=all&page=" + str(i) + "&size=20&sort=viewtimes",headers = self.headers)
            for data in result.json()['data']:
                if int(data['charCount']) >= 100000:
                    sort_list.append(str(data['novelId']))
                    print('[{name:<{len}}\t{length}'.format(name=data['novelName']+']',len=40-len(data['novelName'].encode('GBK'))+len(data['novelName']), length = data['charCount']))
            print("{} book(s) will be downloaded".format(len(sort_list)))
        for i in sort_list:
            self.get_chapter(i)
            self.download()

    def download_stared(self):
        # 下载收藏爱心的小说
        sort_list = []
        result = requests.get('https://api.sfacg.com/user/Pockets?expand=chatNovels%2Cnovels%2Calbums%2Ccomics%2Cdiscount%2CdiscountExpireDate', headers = self.headers)
        pattern_id = re.compile("novelId.+?[0-9]{1,12}")
        # pattern_court = re.compile("charCount.+?[0-9]{1,12}")
        for i in re.findall(pattern_id,result.text):
            sort_list.append(i.split(":")[-1])
        print("\n{} book(s) will be downloaded".format(len(sort_list)))
        for i in sort_list:
            if self.get_chapter(i) == -1:
                print("book {} is invalid".format(i))
                continue
            self.download()


# ### 笔记：
# 
# open对象创建的文件，不能用write方法写入非string的数据
# 
# 可以用 if not 语句来判断东西的exited

# str_list = downloader.check_point()
# print(str_list)


# for i in sort_list:
#     Book_downloader.get_chapter(i)
#     Book_downloader.download()
# BOOK = API("344997")
# BOOK.get_chapter()
# BOOK.download()
# url = 'https://api.sfacg.com/Chaps/4300212?chapsId=4300212&expand=content%2Cchatlines%2Ctsukkomi%2CneedFireMoney%2CoriginNeedFireMoney'
# 签到
# result = requests.put("https://api.sfacg.com/user/signInfo", headers=Iphone_Headers)
# print(result.text)
