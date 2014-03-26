#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygst
pygst.require('0.10')
import gst
from interfaces.urwidui import Interface
import apis


class Pyrebird():
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
        state = self.player.get_state()
        if gst.STATE_PLAYING == state[1]:
            self.player.set_state(gst.STATE_PAUSED)
        elif gst.STATE_PAUSED == state[1]:
            self.player.set_state(gst.STATE_PLAYING)

    def volume_inc(self):
        volume = self.player.get_property('volume')
        self.player.set_property('volume', volume + 0.01)

    def volume_dec(self):
        volume = self.player.get_property('volume')
        if volume > 0.01:
            self.player.set_property('volume', volume - 0.01)

    def get_volume(self):
        return self.player.get_property('volume')

    def handle_message(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif msg.type == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = msg.parse_error()
            print '[E] ', err, debug
        return True

if __name__ == '__main__':
    try:
        pyrebird = Interface(Pyrebird())
        pyrebird.main_loop()
    except Exception as e:
        print e
