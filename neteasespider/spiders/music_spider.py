# -*- coding: utf-8 -*-

import mysql.connector
from scrapy.http.request import Request

import base_spider
from neteasespider.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


class MusicSpider(base_spider.BaseSpider):
    name = "music_spider"
    allowed_domains = ["music.163.com"]

    def connect_to_db(self):
        self.db_config = {
            'user': DB_USER,
            'password': DB_PASSWORD,
            'host': DB_HOST,
            'database': DB_NAME
        }
        self.db = mysql.connector.connect(**self.db_config)
        self.cursor = self.db.cursor()
        self.cursor.execute("SET NAMES utf8mb4")

    def start_requests(self):
        self.connect_to_db()
        self.cursor.execute('SELECT * FROM `artist_info`')
        result = self.cursor.fetchall()
        for artist in result:
            artist_id = str(artist[0])
            url = 'http://music.163.com/api/artist/albums/%s?offset=0&limit=200' % (artist_id)
            yield Request(url,
                          meta={'type': 'album_api', 'artist_id': artist_id},
                          callback=self.parse_album,
                          dont_filter=True)
