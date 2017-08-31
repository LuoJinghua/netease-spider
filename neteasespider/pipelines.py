# -*- coding: utf-8 -*-

import os

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector

from items import ArtistSpiderItem, AlbumSpiderItem, MusicSpiderItem, MusicLyricsSpiderItem
from settings import LYRICS_PATH, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


class NeteasespiderPipeline(object):
    def __init__(self):
        try:
            self.db_config = {
                'user': DB_USER,
                'password': DB_PASSWORD,
                'host': DB_HOST,
                'database': DB_NAME
            }
            self.db = mysql.connector.connect(**self.db_config)
            self.cursor = self.db.cursor()
            self.cursor.execute("SET NAMES utf8mb4")
        except mysql.connector.Error as err:
            print('错误: 连接数据库失败,原因%d: %s' % (err.args[0], err.args[1]))

    # the default pipeline invoke function
    def process_item(self, item, spider):
        if isinstance(item, ArtistSpiderItem):
            self.process_artist_item(item)
        elif isinstance(item, AlbumSpiderItem):
            self.process_album_item(item)
        elif isinstance(item, MusicSpiderItem):
            self.process_music_item(item)
        elif isinstance(item, MusicLyricsSpiderItem):
            self.process_lyrics_item(item)
        return item

    def process_artist_item(self, item):
        insert_sql = ("INSERT INTO artist_info (artist_id, artist_name, gender, category) VALUES (%s, %s, %s, %s)")
        data = (item['artist_id'], item['artist_name'], item['gender'], item['category'])
        try:
            result = self.cursor.execute(insert_sql, data)
            self.db.commit()
            print('保存歌手信息成功.')
        except mysql.connector.Error as err:
            self.db.rollback()
            print("错误: 插入数据失败，原因 %d, %s" % (err.args[0], err.args[1]))

    def process_album_item(self, item):
        insert_sql = ("INSERT INTO album_info (album_id, album_name, album_time, artist_id) VALUES (%s, %s, %s, %s)")
        data = (item['album_id'], item['album_name'], item['album_time'], item['artist_id'])
        try:
            result = self.cursor.execute(insert_sql, data)
            self.db.commit()
            print('保存专辑信息成功.')
        except mysql.connector.Error as err:
            self.db.rollback()
            print("错误: 插入数据失败，原因 %d, %s" % (err.args[0], err.args[1]))

    def process_music_item(self, item):
        insert_sql = ("INSERT INTO music_info (music_id, music_name, artist_id, album_id) VALUES (%s, %s, %s, %s)")
        data = (item['music_id'], item['music_name'], item['artist_id'], item['album_id'])
        try:
            result = self.cursor.execute(insert_sql, data)
            self.db.commit()
            print('保存歌曲信息成功.')
        except mysql.connector.Error as err:
            self.db.rollback()
            print("错误: 插入数据失败，原因 %d, %s" % (err.args[0], err.args[1]))

    def process_lyrics_item(self, item):
        if item['lyrics']:
            path = os.path.join(LYRICS_PATH, item['artist_id'], item['music_id'] + '.lrc')
            try:
                os.makedirs(os.path.dirname(path))
            except:
                pass
            with file(path, 'wb') as fp:
                fp.write(item['lyrics'])
