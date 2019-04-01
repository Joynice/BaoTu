# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
import os
import queue
import threading
import time
import requests
from bs4 import BeautifulSoup
from lxml import etree


def usetime(func):
    def inner(*args, **kwargs):
        time_start = time.time()
        func(*args, **kwargs)
        time_run = time.time() - time_start
        print(func.__name__ + '用时 %.2f 秒' % time_run)
    return inner

class Baotu(object):
    '''
    负责爬虫存储
    TODO:
        1.解决多线程下网络错误：增加retry机制

    '''
    def __init__(self, url='https://ibaotu.com/shipin/', thread=1, max_page=250, useragent=None):
        '''

        :param url:
        :param thread: 线程数
        :param max_page: 爬取页数
        :param useragent: 请求useragent
        '''

        self.url = url
        self.thread = thread
        self.page = max_page
        self.useragent = useragent
        self.header = self._get_header()
        self.que = queue.Queue()
        
        page = self._get_maxpage()
        if self.page > page:
            self.page = page
        super(Baotu, self).__init__()


    # 如果用户没有设置将使用默认
    def _get_header(self):
        if not isinstance(self.useragent, str):
            self.useragent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
            return {'User-Agent': self.useragent}

    def _get_maxpage(self):
        req = requests.get(self.url, headers=self.header, timeout=10, verify=True).text
        html = etree.HTML(req)
        return int(html.xpath("//div[@class='pagelist']/a[8]/text()")[0])

    @usetime
    def request(self):
        for i in range(1, self.page+1):
            try:
                print(self.url)
                req = requests.get(self.url + '6-0-0-0-0-{}.html'.format(i), headers=self.header, timeout=10, verify=True)
                print('正在爬取第%d页的数据' %i)
                if req.status_code == 200:
                    bs = BeautifulSoup(req.text)
                    for _, n in zip(bs.find_all('video', src=True), bs.find_all('img', {'class': 'scrollLoading'})):
                        self.que.put({'url': 'http:'+_['src'], 'name':n['alt']})
            except Exception as e:
                print(e)
                pass
        print('共有{}条视频需要下载！'.format(self.que.qsize()))

    @usetime
    def download(self, path=os.getcwd()):
        while not self.que.empty():
            data = self.que.get()
            try:
                req = requests.get(url=data['url'],headers=self.header, verify=False)
                if req.status_code == 200:
                    print('-'*10,data['url'],'-'*10)
                    if os.path.exists(path):
                        with open(os.path.join(path, data['name']), 'wb') as f:
                            f.write(req.content)
                    else:
                        raise Exception('文件夹不存在')
                else:
                    time.sleep(2)
                    req2 = requests.get(url=data['url'], headers=self.header, verify=False)
                    if req2.status_code ==200:
                        print('+'*10, data['url'], '+'*10)
                        with open(os.path.join(path, data['name']), 'wb') as f:
                            f.write(req.content)
            except Exception as e:
                print(e)
                continue

    def run(self):
        t1 = threading.Thread(target=self.request)
        t1.start()
        t1.join()
        thread_list = []
        for i in range(self.thread):
            t = threading.Thread(target=self.download, args=('D:\\video',))
            thread_list.append(t)
        for t in thread_list:
            t.start()


if __name__ == '__main__':
    a = Baotu(max_page=1, thread=1).run()
# D:\video