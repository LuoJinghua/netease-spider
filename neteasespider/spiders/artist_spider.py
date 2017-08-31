# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector

from neteasespider.items import ArtistSpiderItem, AlbumSpiderItem, MusicSpiderItem, MusicLyricsSpiderItem


class ArtistSpider(scrapy.Spider):
    name = "artists_spider"
    allowed_domains = ["music.163.com"]

    categories = [
        ('华语男歌手', 'zh', 'M', 'http://music.163.com/#/discover/artist/cat?id=1001'),
        ('华语女歌手', 'zh', 'F', 'http://music.163.com/#/discover/artist/cat?id=1002'),
        ('华语组合', 'zh', 'D', 'http://music.163.com/#/discover/artist/cat?id=1003'),
        ('欧美男歌手', 'west', 'M', 'http://music.163.com/#/discover/artist/cat?id=2001'),
        ('欧美女歌手', 'west', 'F', 'http://music.163.com/#/discover/artist/cat?id=2002'),
        ('欧美组合', 'west', 'D', 'http://music.163.com/#/discover/artist/cat?id=2003'),
        ('日本男歌手', 'jp', 'M', 'http://music.163.com/#/discover/artist/cat?id=6001'),
        ('日本女歌手', 'jp', 'F', 'http://music.163.com/#/discover/artist/cat?id=6002'),
        ('日本组合', 'jp', 'D', 'http://music.163.com/#/discover/artist/cat?id=6003'),
        ('韩国男歌手', 'kr', 'M', 'http://music.163.com/#/discover/artist/cat?id=7001'),
        ('韩国女歌手', 'kr', 'F', 'http://music.163.com/#/discover/artist/cat?id=7002'),
        ('韩国组合', 'kr', 'D', 'http://music.163.com/#/discover/artist/cat?id=7003'),
    ]

    def start_requests(self):
        for i in self.categories:
            for j in range(65, 91):
                # 获得A-Z歌手信息
                url = '%s&initial=%d' % (i[3], j)
                yield Request(url,
                              meta={'type': 'artist', 'gender': i[2], 'category': i[1]},
                              callback=self.parse, dont_filter=True)
            # 获得 “其他” 歌手信息
            url = '%s&initial=%d' % (i[3], 0)
            yield Request(url,
                          meta={'type': 'artist', 'gender': i[2], 'category': i[1]},
                          callback=self.parse,
                          dont_filter=True)

    # 处理华语男歌手、华语女歌手以及华语乐队组合页面
    def parse(self, response):
        gender = response.meta['gender']
        category = response.meta['category']

        # 开始分析页面 抽取出歌手artist_id和artist_name
        artist_info = ArtistSpiderItem()
        sel = Selector(response)
        artist_ids = sel.xpath('//a[contains(@href, "/artist?id=")][@class="nm nm-icn f-thide s-fc0"]').re(
            r'/artist\?id=\s*(\d*)"')
        artist_names = sel.xpath(
            '//a[contains(@href, "/artist?id=")][@class="nm nm-icn f-thide s-fc0"]/text()').extract()
        for i in range(len(artist_ids)):
            artist_info['artist_id'] = artist_ids[i].encode("utf-8")
            artist_info['artist_name'] = artist_names[i].encode("utf-8")
            artist_info['gender'] = gender
            artist_info['category'] = category
            yield artist_info

        for i in range(len(artist_ids)):
            #self.start_album_request(artist_ids[i].encode("utf-8"))
            artist_id = artist_ids[i].encode("utf-8")
            url = 'http://music.163.com/#/artist/album?id=%s&limit=200&offset=0' % (artist_id)
            yield Request(url,
                          meta={'type': 'album', 'artist_id': artist_id},
                          callback=self.parse_album,
                          dont_filter=True)

    def start_album_request(self, artist_id):
        url = 'http://music.163.com/#/artist/album?id=%s&limit=200&offset=0' % (artist_id)
        yield Request(url,
                      meta={'type': 'album', 'artist_id': artist_id},
                      callback=self.parse_album,
                      dont_filter=True)

    def parse_album(self, response):
        import datetime
        artist_id = response.meta['artist_id']
        album_info = AlbumSpiderItem()
        sel = Selector(response)
        album_ids = sel.xpath('//a[contains(@href, "/album?id=")][@class="tit s-fc0"]').re(
            r'/album\?id=\s*(\d*)"')
        album_names = sel.xpath(
            '//a[contains(@href, "/album?id=")][@class="tit s-fc0"]/text()').extract()
        album_times = sel.xpath(
            '//span[@class="s-fc3"]/text()').extract()

        for i in range(len(album_ids)):
            album_info['album_id'] = album_ids[i].encode("utf-8")
            album_info['album_name'] = album_names[i].encode("utf-8")
            date = album_times[i].encode("utf-8").split('.')
            if len(date) == 3:
                album_info['album_time'] = datetime.date(int(date[0]), int(date[1]), int(date[2]))
            album_info['artist_id'] = artist_id
            yield album_info

        for i in range(len(album_ids)):
            album_id = album_ids[i].encode("utf-8")
            url = 'http://music.163.com/#/album?id=%s' % (album_id)
            yield Request(url,
                          meta={'type': 'album_info', 'artist_id': artist_id, 'album_id': album_id},
                          callback=self.parse_album_info,
                          dont_filter=True)

    def start_album_info_request(self, artist_id, album_id):
        url = 'http://music.163.com/#/album?id=%s' % (album_id)
        yield Request(url,
                      meta={'type': 'album_info', 'artist_id': artist_id, 'album_id': album_id},
                      callback=self.parse_album_info,
                      dont_filter=True)

    # 处理华语男歌手、华语女歌手以及华语乐队组合页面
    def parse_album_info(self, response):
        artist_id = response.meta['artist_id']
        album_id = response.meta['album_id']

        # 开始分析页面 抽取出歌手artist_id和artist_name
        music_info = MusicSpiderItem()
        sel = Selector(response)
        song_ids = sel.xpath('//a[contains(@href, "/song?id=")]').re(
            r'/song\?id=\s*(\d*)"')
        song_names = sel.xpath(
            '//a[contains(@href, "/song?id=")]/b/text()').extract()
        for i in range(len(song_ids)):
            music_info['music_id'] = song_ids[i].encode("utf-8")
            music_info['music_name'] = song_names[i].encode("utf-8")
            music_info['artist_id'] = artist_id
            music_info['album_id'] = album_id
            yield music_info

        for i in range(len(song_ids)):
            # self.start_lyrics_request(artist_id, album_id, song_ids[i].encode("utf-8"))
            music_id = song_ids[i].encode("utf-8")
            url = 'http://music.163.com/api/song/lyric?os=pc&id=%s&lv=-1&kv=-1&tv=-1' % (music_id)
            yield Request(url,
                          meta={'type': 'lyrics', 'artist_id': artist_id, 'album_id': album_id, 'music_id': music_id},
                          callback=self.parse_lyrics,
                          dont_filter=True)

    def start_lyrics_request(self, artist_id, album_id, music_id):
        url = 'http://music.163.com/api/song/lyric?os=pc&id=%s&lv=-1&kv=-1&tv=-1' % (music_id)
        yield Request(url,
                      meta={'type': 'lyrics', 'artist_id': artist_id, 'album_id': album_id, 'music_id': music_id},
                      callback=self.parse_lyrics,
                      dont_filter=True)

    def parse_lyrics(self, response):
        artist_id = response.meta['artist_id']
        album_id = response.meta['album_id']
        music_id = response.meta['music_id']

        lyrics_info = MusicLyricsSpiderItem()
        json_response = json.loads(response.text)
        if 'lrc' in json_response and 'lyric' in json_response['lrc']:
            lyrics_info['music_id'] = music_id
            lyrics_info['album_id'] = album_id
            lyrics_info['artist_id'] = artist_id
            lyrics_info['lyrics'] = json_response['lrc']['lyric'].encode('utf-8')
            yield lyrics_info
