from __future__ import unicode_literals
from gmusicapi import Mobileclient
import re
import requests
import time
import thread
import argparse
import logging

try:
    from StringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

last_update = time.time()

logging.getLogger('root').setLevel(logging.INFO)

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
                logging.warn('New title: {}'.format(title))
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


def add_song_to_playlist(title, api, playlist):
    try:

        search_result = api.search(title, max_results=1)
        store_id = search_result['song_hits'][0]['track']['storeId']
        if store_id in get_playlist_song_ids(api, playlist):
            logging.warn("Song already in playlist")
        else:
            playlist_id = get_playlist_id(api, playlist)
            api.add_songs_to_playlist(playlist_id, store_id)
            logging.warn("Add at " + time.ctime())
    except:
        logging.warn("!!Cant find " + title + " in google music")


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
    parser.add_argument("-bp", "--bash_pid", dest="bash_pid", nargs="?", help="stream url")

    args = parser.parse_args()

    def monitor_updates():
        while True:
            time.sleep(600)
            if time.time() - last_update > 600:
                import os
                logging.warn('exit')
                os._exit(1)
    print 11
    if args.bash_pid:
        logging.warn("PID: " + str(args.bash_pid))
        print 22

    thread.start_new_thread(monitor_updates, ())
    api = Mobileclient(debug_logging=False)
    api.login(args.user, args.password, Mobileclient.FROM_MAC_ADDRESS)

    icy_monitor(args.stream_url,
                callback=lambda title: add_song_to_playlist(title, api, args.playlist))

