import requests
from fake_useragent import UserAgent
from urllib import request, parse


# 实例化一个对象
# ua=UserAgent()
# #随机获取一个ie浏览器ua
# print(ua.ie)
# print(ua.ie)
# #随机获取一个火狐浏览器ua
# print(ua.firefox)
# print(ua.firefox)
class McmodSpider(object):
    def __init__(self):
        print("0")
        self.url = 'https://search.mcmod.cn/s?key={}'

    def get_html(self, url):
        print("2")
        req = request.Request(url=url, headers={'User-Agent': UserAgent().firefox})
        res = request.urlopen(req)
        html = res.read().decode("utf-8")
        return html

    def run(self):
        print("1")
        mod_name = input('input mod name')
        url = self.url.format(mod_name)
        html = self.get_html(url)
        print(html)


if __name__ == '__main__':
    spider = McmodSpider()
    spider.run()
