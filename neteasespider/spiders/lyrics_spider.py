# -*- coding: utf-8 -*-

import os

import mysql.connector
from scrapy.http.request import Request

import base_spider
from neteasespider.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, LYRICS_PATH


class MusicLyricsSpider(base_spider.BaseSpider):
    name = "lyrics_spider"
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
        self.cursor.execute('SELECT * FROM `music_info`')
        result = self.cursor.fetchall()
        for artist in result:
            artist_id = str(artist[3])
            album_id = str(artist[4])
            music_id = str(artist[0])
            if os.path.exists(os.path.join(LYRICS_PATH, artist_id, music_id + '.lrc')):
                continue
            url = 'http://music.163.com/api/song/lyric?os=pc&id=%s&lv=-1&kv=-1&tv=-1' % (music_id)
            yield Request(url,
                          meta={'type': 'lyrics_json', 'artist_id': artist_id, 'album_id': album_id,
                                'music_id': music_id},
                          callback=self.parse_lyrics,
                          dont_filter=True)
