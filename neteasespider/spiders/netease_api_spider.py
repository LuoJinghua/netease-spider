# -*- coding: utf-8 -*-
import base_spider


class ArtistApiSpider(base_spider.BaseSpider):
    name = "netease_api_spider"
    allowed_domains = ["music.163.com"]
