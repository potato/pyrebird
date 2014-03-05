#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygst
pygst.require('0.10')
import gst
import requests

CLIENT_ID = 'b45b1aa10f1ac2941910a7f0d10f8e28'
MAIN_URL = 'http://api.soundcloud.com'


class SoundcloudPlayer():
    def __init__(self):
        self.player = gst.element_factory_make('playbin2', 'player')
        self.player.set_property('video-sink', gst.element_factory_make('fakesink', 'fakesink'))
        self.player.set_property('buffer-size', 1024)
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.handle_message)
        self.playing = False

    def search_track(self, q):
        r = self.make_request('tracks', {'q': q})
        if r.status_code == 200:
            for test in r.json():
                print test['id'], ': ', test['title']

    def play_track(self, sid):
        self.player.set_state(gst.STATE_NULL)
        r = self.make_request('tracks/%d' % sid)
        if r.status_code == 200:
            self.player.set_property('uri', r.json().get('stream_url') + '?client_id=' + CLIENT_ID)
            self.player.set_state(gst.STATE_PLAYING)

    def make_request(self, rtype, args={}):
        args.update({'client_id': CLIENT_ID})
        return requests.get(MAIN_URL + '/' + rtype + '.json', params=args)

    def stop_player(self):
        self.playing = False
        self.player.set_state(gst.STATE_NULL)

    def handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.playing = False
        elif msg.type == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.playing = False
            err, debug = msg.parse_error()
            print '[E] ', err, debug
        else:
            print msg

if __name__ == '__main__':
    sc = SoundcloudPlayer()
    while True:
        cmd = raw_input('> ')
        if cmd.startswith('.play'):
            sid = cmd.split(' ')[1]
            sc.play_track(int(sid))
        elif cmd == '.quit':
            sc.stop_player()
            break
        else:
            sc.search_track(cmd)
