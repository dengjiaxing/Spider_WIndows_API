#encoding:utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import bs4
import time
import urllib
import re
import urllib2
import os
from lxml import etree 
from selenium.webdriver.common import proxy as _px
import argparse
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
from proxy_ip import main
class get_example():
    """docstring for get_example"""
    def __init__(self):
        self.path=r'D:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe'
        self.headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48'}
        self.base_url='https://social.msdn.microsoft.com/Search/zh-CN?query='
    def html_to_soup(self,url):
        # main()
        # req = urllib2.Request(url, headers=self.headers)
        # html = urllib2.urlopen(req).read()
        # soup=BeautifulSoup(html,"html.parser")
        req = urllib2.Request(url,headers=self.headers) 
        response = urllib2.urlopen(req)
        the_page = response.read()
        soup=BeautifulSoup(the_page,"html.parser")


        return soup
    def parse_search_page(self,api):
        # proxy=webdriver.Proxy()
        # proxy.proxy_type=_px.ProxyType.MANUAL
        # proxy.http_proxy=ip
        # # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
        # proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
        # self.driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
        driver=webdriver.PhantomJS(self.path)
        url=self.base_url+api
        driver.get(url)
        #wait = ui.WebDriverWait(self.driver, 10)
        #wait.until(lambda dr: dr.find_element_by_class_name('SearchResult').is_displayed())
        time.sleep(3)
        filename=api+'.html'
        fp = open(filename,'w')
        fp.write(driver.page_source)
        driver.quit()
        fp.close()
        #print query_url
        htmlfile = open(filename, 'r')
        the_page = htmlfile.read()
        htmlfile.close()
        #os.remove(filename)
        data=BeautifulSoup(the_page,"html.parser")
        new_url=''
        non_result=data.find('div',{'id':'NoResultsContainer'})#  没有找到搜索项
        if non_result:
            return new_url
        result_list=data.find_all('a',{'class':'resultTitleLink'})
        for result in result_list:
            # print result.text
            # print result.find('a').get('href')
            #real=result.find('div',{'class':'result'})
           # print real
            #print result
            se=re.search(r'\sfunction\s',result.text)
            if se:
                new_url=result.get('href')
                return new_url
           # print real.find('a').get('href')
        
        return new_url
    def parse_function_page(self,url):
        dirc={}
        if url=='':
            return dirc
        soup=self.html_to_soup(url)
        example=soup.find_all('h2')
        for h in example:             #得到Examples下所有测试用例链接地址,存在一个函数有多种测试用例的情况
            if h.text=="Examples":
                nexts=h.next_siblings
                for tag in nexts:
                    if tag.string=="Requirements":
                        break
                    if type(tag)==bs4.NavigableString:         #判断是否为NavigableString类型,NavigableString类型标签不存在find等操作
                        continue
                    if isinstance(tag, bs4.Tag):
                        link =tag.find_all('a')
                        for href in link:
                            dirc[href.text]=href.get('href')
        return dirc                                           #所有Example链接地址及说明
    def get_example(self,url):   #得到url地址下对应的example代码
        soup=self.html_to_soup(url)
        example=soup.find_all('div',class_='codeSnippetContainerCode')[-1]
        return example.find('pre').text
    def example_to_dir(self,dirc):
        new_dir={}
        if not dirc:
            return new_dir
        for key in dirc:
            url=dirc[key]
            example=self.get_example(url)
            new_dir[key]=example
        return new_dir
    def connect_db(self):    #连接mongodb数据库
        client = MongoClient('localhost', 27017)
        db_name = 'API'
        db = client[db_name]
        collection_useraction = db['example']
        return collection_useraction
    def add_db(self,api,dirc):    #将数据添加到数据库中
        insert_dir={} 
        insert_dir[api]=dirc
        con=self.connect_db()
        con.insert(insert_dir)
    def get_all_api(self):
        fp=open("result.txt",'r')
        all_api=[]
        lines=fp.readlines();
        count=0
        for line in lines:
            test_list=line.split()
            index=test_list.index("WINAPI")
            if index+1==len(test_list):
                continue
            else:
                str_temp=test_list[index+1]
                i=0
                end_str=''
                while i<len(str_temp) and str_temp[i]!='(':
                    end_str=end_str+str_temp[i]
                    i=i+1
                all_api.append(end_str)
        return set(all_api)
    def execute(self):
        all_api=self.get_all_api()
        for api in all_api:
            if api!='':
                print api
                #ip=main()
                url=self.parse_search_page(api)
                example_dir=self.example_to_dir(self.parse_function_page(url))
                self.add_db(api,example_dir)
if __name__ == '__main__':
    example=get_example()
    example.execute()

