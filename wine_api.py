# encoding:utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import bs4
from scrapy.http import HtmlResponse
import time
import urllib
import re
import urllib2
import os
from lxml import etree
import selenium.webdriver.support.ui as ui
import argparse
from pymongo import MongoClient


class get_example():
    """docstring for get_example"""

    def __init__(self):
        self.path = r'D:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe'
        self.driver = webdriver.PhantomJS(self.path)

    def html_to_soup(self, url):
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()
        soup = BeautifulSoup(the_page, "html.parser")
        return soup

    def parse_search_page(self, api):
        base_url = 'https://social.msdn.microsoft.com/Search/zh-CN?query='
        url = base_url + api
        self.driver.get(url)
        wait = ui.WebDriverWait(self.driver, 10)
        wait.until(lambda dr: dr.find_element_by_class_name('SearchResult').is_displayed())
        time.sleep(3)
        fp = open('1.html', 'w')
        fp.write(self.driver.page_source)
        self.driver.quit()
        # print query_url
        htmlfile = open('1.html', 'r')
        the_page = htmlfile.read()
        data = BeautifulSoup(the_page, "html.parser")
        result_list = data.find_all('a', {'class': 'resultTitleLink'})
        count = 0
        new_url = ''
        for result in result_list:
            # print result.text
            # print result.find('a').get('href')
            # real=result.find('div',{'class':'result'})
            # print real
            # print result
            se = re.search(r'\sfunction\s', result.text)
            if se:
                new_url = result.get('href')
                return new_url
                # print real.find('a').get('href')

        return new_url

    def parse_function_page(self, url):
        soup = self.html_to_soup(url)
        example = soup.find_all('h2')
        dirc = {}
        for h in example:  # 得到Examples下所有测试用例链接地址,存在一个函数有多种测试用例的情况
            if h.text == "Examples":
                nexts = h.next_siblings
                for tag in nexts:
                    if tag.string == "Requirements":
                        break
                    if type(tag) == bs4.NavigableString:  # 判断是否为NavigableString类型,NavigableString类型标签不存在find等操作
                        continue
                    if isinstance(tag, bs4.Tag):
                        link = tag.find_all('a')
                        for href in link:
                            dirc[href.text] = href.get('href')
        return dirc  # 所有Example链接地址及说明

    def get_example(self, url):  # 得到url地址下对应的example代码
        soup = self.html_to_soup(url)
        example = soup.find_all('div', class_='codeSnippetContainerCode')[-1]
        return example

    def example_to_dir(self, dirc):
        new_dir = {}
        for key in dirc:
            url = dirc[key]
            example = self.get_example(url)
            new_dir[key] = example
        return new_dir

    def connect_db(self):
        client = MongoClient('localhost', 27017)
        db_name = 'API'
        db = client[db_name]
        collection_useraction = db['example']
        return collection_useraction

    def add_db(self, api, dirc):
        con = self.connect_db()
        con.insert(api, dirc)


if __name__ == '__main__':
    api = 'CreateFile'
    example = get_example()
    url = example.parse_search_page(api)
    example_dir = example.example_to_dir(example.parse_function_page(url))
    example.add_db(api, example_dir)




