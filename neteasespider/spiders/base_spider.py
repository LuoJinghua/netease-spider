# -*- coding: utf-8 -*-
import json

import scrapy
import os
from scrapy.http.request import Request
from scrapy.selector import Selector

from neteasespider.items import ArtistSpiderItem, AlbumSpiderItem, MusicSpiderItem, MusicLyricsSpiderItem
from neteasespider.settings import LYRICS_PATH

class BaseSpider(scrapy.Spider):
    name = "netease_base_spider"
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

    def parse(self, response):
        """ parse the artist list """
        gender = response.meta['gender']
        category = response.meta['category']

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
            artist_id = artist_ids[i].encode("utf-8")
            url = 'http://music.163.com/api/artist/albums/%s?offset=0&limit=200' % (artist_id)
            yield Request(url,
                          meta={'type': 'album_api', 'artist_id': artist_id},
                          callback=self.parse_album,
                          dont_filter=True)

    def parse_album(self, response):
        import datetime
        artist_id = response.meta['artist_id']
        album_info = AlbumSpiderItem()
        json_response = json.loads(response.text)
        albums = json_response['hotAlbums']
        for i in range(len(albums)):
            album_info['album_id'] = str(albums[i]['id'])
            album_info['album_name'] = albums[i]['name'].encode("utf-8")
            album_info['album_time'] = datetime.date.fromtimestamp(albums[i]['publishTime'] / 1000)
            album_info['artist_id'] = artist_id
            yield album_info

        for i in range(len(albums)):
            album_id = str(albums[i]['id'])
            url = 'http://music.163.com/api/album/%s' % (album_id)
            yield Request(url,
                          meta={'type': 'album_info_json', 'artist_id': artist_id, 'album_id': album_id},
                          callback=self.parse_album_info,
                          dont_filter=True)

    def parse_album_info(self, response):
        artist_id = response.meta['artist_id']
        album_id = response.meta['album_id']

        music_info = MusicSpiderItem()
        json_response = json.loads(response.text)
        songs = []
        if 'album' in json_response and 'songs' in json_response['album']:
            songs = json_response['album']['songs']
        else:
            print json_response

        for i in range(len(songs)):
            music_info['music_id'] = str(songs[i]['id'])
            music_info['music_name'] = songs[i]['name'].encode("utf-8")
            music_info['artist_id'] = artist_id
            music_info['album_id'] = album_id
            yield music_info

        for i in range(len(songs)):
            music_id = str(songs[i]['id'])
            if os.path.exists(os.path.join(LYRICS_PATH, artist_id, music_id + '.lrc')):
                continue
            url = 'http://music.163.com/api/song/lyric?os=pc&id=%s&lv=-1&kv=-1&tv=-1' % (music_id)
            yield Request(url,
                          meta={'type': 'lyrics_json', 'artist_id': artist_id, 'album_id': album_id,
                                'music_id': music_id},
                          callback=self.parse_lyrics,
                          dont_filter=True)

    def parse_lyrics(self, response):
        artist_id = response.meta['artist_id']
        album_id = response.meta['album_id']
        music_id = response.meta['music_id']

        lyrics_info = MusicLyricsSpiderItem()
        lyrics_info['music_id'] = music_id
        lyrics_info['album_id'] = album_id
        lyrics_info['artist_id'] = artist_id
        lyrics_info['lyrics'] = ''

        json_response = json.loads(response.text)
        if 'lrc' in json_response and 'lyric' in json_response['lrc']:
            lyrics_info['lyrics'] = json_response['lrc']['lyric'].encode('utf-8')
        yield lyrics_info
