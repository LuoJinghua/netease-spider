# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# artist
class ArtistSpiderItem(scrapy.Item):
    artist_id = scrapy.Field()
    artist_name = scrapy.Field()
    gender = scrapy.Field()
    category = scrapy.Field()


# album
class AlbumSpiderItem(scrapy.Item):
    album_id = scrapy.Field()
    album_name = scrapy.Field()
    album_time = scrapy.Field()
    artist_id = scrapy.Field()


# music
class MusicSpiderItem(scrapy.Item):
    music_id = scrapy.Field()
    music_name = scrapy.Field()
    album_id = scrapy.Field()
    artist_id = scrapy.Field()


# lyrics
class MusicLyricsSpiderItem(scrapy.Item):
    music_id = scrapy.Field()
    album_id = scrapy.Field()
    artist_id = scrapy.Field()
    lyrics = scrapy.Field()


# Music file
class MusicFileSpiderItem(scrapy.Item):
    music_id = scrapy.Field()
    album_id = scrapy.Field()
    artist_id = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
