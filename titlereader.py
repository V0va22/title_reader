from __future__ import unicode_literals
from gmusicapi import Mobileclient
import re
import requests
import time
import thread
import argparse

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

last_update = time.time()

def icy_monitor(stream_url, callback=None):

    r = requests.get(stream_url, headers={'Icy-MetaData': '1'}, stream=True)
    if r.encoding is None:
        r.encoding = 'utf-8'

    byte_counter = 0
    meta_counter = 0
    metadata_buffer = BytesIO()

    metadata_size = int(r.headers['icy-metaint']) + 255

    data_is_meta = False

    for byte in r.iter_content(1):

        byte_counter += 1

        if (byte_counter <= 2048):
            pass

        if (byte_counter > 2048):
            if (meta_counter == 0):
                meta_counter += 1

            elif (meta_counter <= int(metadata_size + 1)):

                metadata_buffer.write(byte)
                meta_counter += 1
            else:
                data_is_meta = True

        if (byte_counter > 2048 + metadata_size):
            byte_counter = 0

        if data_is_meta:

            metadata_buffer.seek(0)

            meta = metadata_buffer.read().rstrip(b'\0')

            m = re.search(br"StreamTitle='([^']*)';", bytes(meta))
            if m:
                title = m.group(1).decode(r.encoding, errors='replace')
                print('New title: {}'.format(title))
                global last_update
                last_update = time.time()
                if callback:
                    callback(title)

            byte_counter = 0
            meta_counter = 0
            metadata_buffer = BytesIO()

            data_is_meta = False


def print_title(title):
    print('Title: {}'.format(title))


def add_song_to_playlist(title, username, password, playlist):
    try:
        api = Mobileclient()
        api.login(username, password, Mobileclient.FROM_MAC_ADDRESS)
        search_result = api.search(title, max_results=1)
        store_id = search_result['song_hits'][0]['track']['storeId']
        if store_id in get_playlist_song_ids(api, playlist):
            print "Song already in playlist"
        else:
            playlist_id = get_playlist_id(api, playlist)
            api.add_songs_to_playlist(playlist_id, store_id)
            print "Add at " + time.ctime()
    except:
        print "!!Cant find " + title + " in google music"


def get_playlist_song_ids(api, playlist):
    for p in api.get_all_user_playlist_contents():
        if p['name'] == playlist:
            return [track['track']['storeId'] for track in p['tracks']]


def get_playlist_id(api, playlist):
    for p in api.get_all_playlists():
        if p['name'] == playlist:
            playlist_id = p['id']
            break
    return playlist_id


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-u", "--user", dest="user", nargs="?", help="google music username")
    parser.add_argument("-p", "--pass", dest="password", nargs="?", help="google music password")
    parser.add_argument("-pl", "--playlist", dest="playlist", nargs="?", help="google music playlist")
    parser.add_argument("-s", "--stream_url", dest="stream_url", nargs="?", help="stream url")

    args = parser.parse_args()
    def monitor_updates():
        while True:
            time.sleep(600)
            if time.time() - last_update > 600:
                import os
                print 'exit'
                os._exit(1)

    thread.start_new_thread(monitor_updates, ())

    icy_monitor(args.stream_url,
                callback=lambda title: add_song_to_playlist(title, args.user, args.password, args.playlist))
