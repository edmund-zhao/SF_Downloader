import requests
import time
import os
import re
# from ebooklib import epub
from tqdm import tqdm

Web_Headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40'}

# TODO ： 分安卓与苹果来输入Cookies


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
'User-Agent': 'boluobao/4.5.52(iOS;14.0)/appStore',
'Accept-Language': 'zh-Hans-US;q=1',
'Authorization': 'Basic YXBpdXNlcjozcyMxLXl0NmUqQWN2QHFlcg=='}
        
    def get_cookie_security(self):
        if not os.path.exists('./config/cookie.conf'):
            if not os.path.exists('./config'):
                os.mkdir('./config')
            self.Cookie = input("请输入SFACG的字符串cookie[注：非字典类cookie]:")
            # self.SFSecurity = input("请输入SFSecurity:")
            with open('./config/cookie.conf','w+') as fb:
                fb.write(self.Cookie)
            # with open('./config/SFSecurity.conf','w+') as fb:
            #     fb.write(self.SFSecurity)
                
            self.headers['Cookie'] = self.Cookie
        else:
            
            if input('是否刷新cookie 与 security:[y/n(default)]') == 'y':
                self.Cookie = input("请输入SFACG的字符串cookie[注：非字典类cookie]:")
                # self.SFSecurity = input("请输入SFSecurity:")
                with open('./config/cookie.conf','w+') as fb:
                    fb.write(self.Cookie)
                # with open('./config/SFSecurity.conf','w+') as fb:
                #     fb.write(self.SFSecurity)
                self.headers['Cookie'] = self.Cookie
                # self.headers['SFSecurity'] = self.SFSecurity
                print('刷新成功')

                return 0
            
            with open('./config/cookie.conf') as fb:
                self.Cookie = fb.read()
            # with open('./config/SFSecurity.conf','w+') as fb:
            #     self.SFSecurity = fb.read()
            self.headers['Cookie'] = self.Cookie
            # self.headers['SFSecurity'] = self.SFSecurity
        

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
        self.Division_Volume = {}
        if self.book == '':
            self.book = input("请输入小说的ID")
        book_url = "http://book.sfacg.com/Novel/"+ self.book +"/MainIndex/"
        ## 编译正则表达式
        pattern_name = re.compile(r'<h1 class=["]story-title["]>(.*?)</h1>', re.M | re.S)
        pattern_div = re.compile(r'<h3 class="catalog-title">(.*?)</h3>', re.M | re.S)
        pattern_404 = re.compile(r'小说不存在')
        pattern_chapter = re.compile(r'<a href=(.*?) class=""')
        r = requests.get(book_url,headers = Web_Headers)
        '''
        不在支持Beautifulsoup4
        Soup = BeautifulSoup(r.text,'html.parser')
        if Soup.find(text= '小说不存在') == '小说不存在':
            return -1
        '''
        if re.search(pattern_404,r.text) is not None:
            print("此小说已下架，或着被河蟹")
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
            '''
            不在支持Beautifulsoup4
            self.Novel_Name = Soup.find('h1',{'class':'story-title'}).text
            self.Novel_Name = self.Novel_Name.replace("?","")
            # print('当前小说为:',self.Novel_Name)
            for volume in Soup.find_all('h3', {'class': 'catalog-title'}):
                self.Volume.append(volume.text)
            i = 0
            # v 代表一卷，BS4库无法直接搜索，因此要用两层循环
            for v in Soup.find('div').find_all('div',{'class': "story-catalog"}):
                Chapter = []
                for chap in v.find_all('li'):
                    chapter_id = chap.find('a').get('href').split('/')[-2]
                    title = chap.find('a').get('title')
                    Chapter.append([chapter_id,title])
                self.Division_Volume[self.Volume[i]] = Chapter
                i += 1
            '''
        except:
            return -1
#         print(self.Volume)
#         print(self.Division_Volume)

    def download(self):
        read_str_list = ''
        if os.path.exists('.//config//' + self.Novel_Name + '.conf'):
            read_str_list = self.check_point()
        if not os.path.exists('.//novel'):
            os.mkdir('.//novel')
        with open(".//novel//"+ self.Novel_Name + ".txt", 'a', encoding='utf-8') as fb:
            pbar = tqdm(self.Chapter)
            for i in pbar:
                pbar.set_description(desc = "下载:<{}> {}".format(self.Novel_Name,i[-1]))
                # 判断当前章节是否已经被下载
                if i[0] in read_str_list:
                    # print("\t{}已经下载完成，跳过".format(j[-1]))
                    continue
                url = 'https://api.sfacg.com/Chaps/' + i[0] + '?chapsId=' + i[0] + '&expand=content%2Cchatlines%2Ctsukkomi%2CneedFireMoney%2CoriginNeedFireMoney'
                try:
                    result = requests.get(url, headers=self.headers)
                except:
                    return -1
                if result.json()['status']['httpCode'] == 403:
                    print("\t", i[-1], "需要付费VIP")
                    break
                else:
                    # TODO: 创建一个EPUB文件
                    text = '\n' + i[-1] + '\n' + result.json()["data"]["expand"]["content"]
                    fb.write(text)
                    # print("\t\t",j[-1],':已完成下载')
                    time.sleep(0.5)
                    self.write_point(i[0] + '、')
            else:
                print("全本小说已经下载完成")
            # for i in self.Volume:
            #     # print("正在下载{}卷".format(i.split('】')[-1]))
            #     for j in tqdm(self.Division_Volume[i],desc = "\t{}".format(i.split('】')[-1])):
            #         # 判断当前章节是否已经被下载
            #         if j[0] in read_str_list:
            #             # print("\t{}已经下载完成，跳过".format(j[-1]))
            #             continue
            #         # self.__last_list.append()
            #         url = 'https://api.sfacg.com/Chaps/' + j[0] +'?chapsId='+ j[0] +'&expand=content%2Cchatlines%2Ctsukkomi%2CneedFireMoney%2CoriginNeedFireMoney'
            #         try:
            #             result = requests.get(url, headers = self.headers)
            #         except:
            #             return -1
            #         if result.json()['status']['httpCode'] == 403:
            #             print("\t",j[-1],"需要付费VIP")
            #             break
            #         else:
            #             # TODO: 创建一个EPUB文件
            #             text = '\n' + j[-1] +'\n' + result.json()["data"]["expand"]["content"]
            #             fb.write(text)
            #             # print("\t\t",j[-1],':已完成下载')
            #             time.sleep(0.5)
            #             self.write_point(j[0] + '、')
            #     else:
            #         continue
            #     # print("下载《", self.Novel_Name, "》完成")
            #     break
            #
            # else:
            #     print("全本小说已经下载完成")


    def download_sort(self,num,sortid):
        # 返回 分类小说 的目录
        sort_list = []
        for i in range(num):
            result = requests.get("https://api.sfacg.com/novels/0/sysTags/" + sortid + "/novels?expand=typeName&filter=all&page=" + str(i) + "&size=20&sort=viewtimes",headers = self.headers)
            for data in result.json()['data']:
                if int(data['charCount']) >= 100000:
                    sort_list.append(str(data['novelId']))
                    print('书名《{novelName}》\n  小说字数{charCount}'.format_map(data))
            print("总计下载{}本书".format(len(sort_list)))
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
        print("\n总计下载{}本书".format(len(sort_list)))
        for i in sort_list:
            if self.get_chapter(i) == -1:
                print("当前小说不存在ID{}".format(i))
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




