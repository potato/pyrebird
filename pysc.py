#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygst
pygst.require('0.10')
import gst
from guis.urwidui import UI
import apis

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

    def search(self, q):
        return apis.search(q)

    def play(self, url):
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri', url)
        self.player.set_state(gst.STATE_PLAYING)

    def stop(self):
        self.player.set_state(gst.STATE_NULL)

    def pause(self):
        state = filter(lambda x: type(x) == gst.State, self.player.get_state())
        if gst.STATE_PLAYING in state:
            self.player.set_state(gst.STATE_PAUSED)
        elif gst.STATE_PAUSED in state:
            self.player.set_state(gst.STATE_PLAYING)

    def volume_inc(self):
        volume = self.player.get_property('volume')
        self.player.set_property('volume', volume + 0.01)

    def volume_dec(self):
        volume = self.player.get_property('volume')
        if volume > 0.01:
            self.player.set_property('volume', volume - 0.01)

    def handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif msg.type == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = msg.parse_error()
            print '[E] ', err, debug
        elif msg.type == gst.MESSAGE_ANY:
            pass
        return True

if __name__ == '__main__':
    try:
        sc = SoundcloudPlayer()
        ui = UI(sc)
        ui.main_loop()
    except Exception as e:
        print e
