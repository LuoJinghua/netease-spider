# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.http import HtmlResponse
from selenium import webdriver


class JavaScriptMiddleware(object):
    rendered_by_js = set(['artist', 'album', 'album_info'])

    def process_request(self, request, spider):
        if spider.name == "artists_spider" and request.meta.get('type', None) in self.rendered_by_js:
            driver = webdriver.PhantomJS()  # 指定使用的浏览器
            driver.get(request.url)
            driver.switch_to.frame(driver.find_element_by_xpath("//iframe"))
            content = driver.page_source
            return HtmlResponse(driver.current_url, body=content,
                                encoding='utf-8', request=request)


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        UA = random.choice(self.user_agent_list)
        if UA:
            request.headers.setdefault('User-Agent', UA)

    user_agent_list = [
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    ]


class NeteasespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
