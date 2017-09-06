#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import json
import os
import sys
import urllib
import urllib2

import encrypt_util


def get_mp3_url_list(song_detail_list, bitrate):
    url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
    song_id_list = []
    for detail in song_detail_list:
        song_id_list.append(detail['id'])
    data = {
        'ids': song_id_list,
        # br 代表比特率(Bitrate)，常用取值：128000、192000、320000、990000...值越大代表音质越好，文件也越大
        'br': bitrate
    }
    data = json.dumps(data)
    data = encrypt_util.encrypt_request(url, data)
    json_result = urllib2.urlopen(url, urllib.urlencode(data)).read().decode('utf-8')
    obj = json.loads(json_result)
    for item in obj['data']:
        detail = next(x for x in song_detail_list if x['id'] == item['id'])
        detail['url'] = item['url']
        detail['size'] = item['size']
        detail['bitrate'] = item['br']
    return song_detail_list


def get_song_download_url(song_id_list, bitrate):
    song_detail_list = []
    for song_id in song_id_list:
        resp = urllib2.urlopen('http://music.163.com/api/song/detail/?id=' + song_id + '&ids=%5B' + song_id + '%5D')
        json_str = resp.read()
        obj = json.loads(json_str)
        item = {
            'id': obj['songs'][0]['id'],
            'name': obj['songs'][0]['name'].encode('utf-8'),
            'artist': obj['songs'][0]['artists'][0]['name'].encode('utf-8'),
        }
        song_detail_list.append(item)

    return get_mp3_url_list(song_detail_list, bitrate)


def download_file(url, path):
    try:
        f = urllib2.urlopen(url)

        with open(path, "wb") as fp:
            fp.write(f.read())

    # handle errors
    except urllib2.HTTPError, e:
        print("HTTP Error: %d %s" % (e.code, url))
    except urllib2.URLError, e:
        print("URL Error: %s %s" % (e.reason, url))


def download_lrc(music_id, output):
    url = 'http://music.163.com/api/song/lyric?os=pc&id=%s&lv=-1&kv=-1&tv=-1' % (music_id)
    response = urllib2.urlopen(url)
    json_response = json.loads(response.read())
    if 'lrc' in json_response and 'lyric' in json_response['lrc']:
        lyrics = json_response['lrc']['lyric'].encode('utf-8')
        with file(output, 'wb') as fp:
            fp.write(lyrics)


def download(music_id, mp3_path, lrc_path, bitrate):
    result = get_song_download_url([music_id], bitrate)
    if result:
        url = result[0]['url']
        print('downloading music `%s\' from %s' % (music_id, url))
        download_file(url, mp3_path)

        if lrc_path:
            download_lrc(music_id, lrc_path)

        print('downloaded music: `%s\'' % (music_id))


if __name__ == '__main__':
    from optparse import OptionParser

    usage = """%prog mp3_id..."""
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--bitrate', dest='bitrate', default=320000,
                      help='the bitrate of mp3')
    parser.add_option('-l', '--lrc', dest='lrc', default=False,
                      action='store_true',
                      help='the bitrate of mp3')
    parser.add_option('-d', '--output', dest='output', default='./',
                      help='the directory to save download mp3')
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("Missing the id of music.")
        sys.exit(-1)
    for arg in args:
        download(arg,
                 os.path.join(options.output, arg + '.mp3'),
                 os.path.join(options.output, arg + '.lrc') if options.lrc else None,
                 options.bitrate)
