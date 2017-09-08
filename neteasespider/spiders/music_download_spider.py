# -*- coding: utf-8 -*-

import json
import urllib

import mysql.connector
from scrapy.http import FormRequest

import base_spider
from neteasespider import encrypt_util
from neteasespider.items import MusicFileSpiderItem
from neteasespider.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, MUSIC_BITRATE


class MusicFileSpider(base_spider.BaseSpider):
    name = "music_download_spider"
    allowed_domains = ["music.163.com"]

    # 比特率(Bitrate)，常用取值：128000、192000、320000、990000...值越大代表音质越好，文件也越大

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
        albums = {}
        for music in result:
            artist_id = music[3]
            album_id = music[4]
            music_id = music[0]

            if album_id not in albums:
                albums[album_id] = {}
                albums[album_id]['artist_id'] = artist_id
                albums[album_id]['music_ids'] = []
            albums[album_id]['music_ids'].append(music_id)

        for album_id in albums:
            album_info = albums[album_id]
            artist_id = str(album_info['artist_id'])
            music_id_list = album_info['music_ids']
            url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
            data = {
                'ids': music_id_list,
                # br 代表比特率(Bitrate)，常用取值：128000、192000、320000、990000...值越大代表音质越好，文件也越大
                'br': MUSIC_BITRATE
            }
            data = json.dumps(data)
            data = encrypt_util.encrypt_request(url, data)
            yield FormRequest(url,
                              method='POST',
                              formdata=data,
                              meta={'type': 'music_url_json', 'artist_id': artist_id, 'album_id': str(album_id),
                                    'music_ids': music_id_list},
                              callback=self.parse_music_url,
                              dont_filter=True)

    def parse_music_url(self, response):
        artist_id = response.meta['artist_id']
        album_id = response.meta['album_id']
        music_ids = response.meta['music_ids']

        obj = json.loads(response.text)

        urls = {}
        for item in obj['data']:
            if item['id'] in music_ids and item['url']:
                urls[item['id']] = item['url']

        for music_id in music_ids:
            if music_id in urls:
                item = MusicFileSpiderItem()
                item['album_id'] = album_id
                item['artist_id'] = artist_id
                item['music_id'] = music_id
                item['file_urls'] = [urls[music_id]]
                yield item
