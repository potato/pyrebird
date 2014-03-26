import urwid


class Interface():
    def __init__(self, player=None):
        # init variables, objects
        self.palette = [
            ('body', 'yellow', ''),
            ('focus', 'black', 'brown'),
        ]
        self.player = player
        self.playlist = Playlist()
        self.searchlist = Searchlist()
        self.prompt = Prompt()
        self.top = Top(self.player)
        self.window = urwid.Frame(self.playlist.get_box(), self.top, self.prompt)
        self.screen = urwid.raw_display.Screen()

        # setting up signals
        urwid.register_signal(Prompt, ['perform_search', 'cancel_input'])
        urwid.register_signal(Searchlist, ['add_track', 'play_track'])
        urwid.register_signal(Playlist, ['play_track'])
        urwid.register_signal(urwid.Frame, ['set_volume'])
        urwid.connect_signal(self.prompt, 'perform_search', self.search_callback)
        urwid.connect_signal(self.prompt, 'cancel_input', self.cancel_input_callback)
        urwid.connect_signal(self.searchlist, 'add_track', self.add_track_callback)
        urwid.connect_signal(self.searchlist, 'play_track', self.play_track_callback)
        urwid.connect_signal(self.searchlist, 'play_track', self.top.play_track_callback)
        urwid.connect_signal(self.playlist, 'play_track', self.play_track_callback)
        urwid.connect_signal(self.playlist, 'play_track', self.top.play_track_callback)
        urwid.connect_signal(self.window, 'set_volume', self.top.set_volume_callback)

        # starting the main loop
        self.loop = urwid.MainLoop(self.window, self.palette, unhandled_input=self._handle_global_input)
        self.loop.set_alarm_in(0.5, self.top.update)

    def _handle_global_input(self, key):
        if key == 'q':
            raise urwid.ExitMainLoop()
        elif key == 's':
            self.window.focus_position = 'footer'
            self.prompt.do_ask('Search: ')
        elif key == 'tab':
            if self.window.get_body().get_body() == self.playlist:
                self.window.set_body(self.searchlist.get_box())
            else:
                self.window.set_body(self.playlist.get_box())
        elif key in ('h', 'left'):
            self.player.volume_dec()
            urwid.emit_signal(self.window, 'set_volume')
        elif key in ('l', 'right'):
            self.player.volume_inc()
            urwid.emit_signal(self.window, 'set_volume')
        elif key in ('p'):
            self.player.pause()

    def search_callback(self):
        q = self.prompt.edit_text
        self.searchlist.update(self.player.search(q))
        self.searchlist.set_result_text(q)
        self.window.set_body(self.searchlist.get_box())
        self.prompt.hide()
        self.window.focus_position = 'body'

    def cancel_input_callback(self):
        self.prompt.hide()
        self.window.focus_position = 'body'

    def add_track_callback(self, track):
        self.playlist.add_track(track)

    def play_track_callback(self, track):
        self.player.play(track.url)

    def main_loop(self):
        self.loop.run()


class Top(urwid.Columns):
    def __init__(self, player):
        self.player = player
        self.time_total = urwid.Text('0:00')
        self.time_current = urwid.Text('0:00')
        self.title = urwid.Text('')
        self.volume = urwid.Text('Volume: %f' % self.player.get_volume())
        self._items = [
            ('pack', self.time_total),
            ('pack', urwid.Text(' / ')),
            ('pack', self.time_current),
            (3, urwid.Text('   ')),
            self.title,
            ('pack', self.volume)
        ]
        super(Top, self).__init__(self._items)

    def update(self, loop, args):
        if self.player.player.get_state()[1].value_name == 'GST_STATE_PLAYING':
            time = float(self.player.player.get_clock().get_time()) / 1000000.0
            self.time_current.set_text(printable_duration(time))
        loop.set_alarm_in(0.5, self.update)

    def set_volume_callback(self):
        self.volume.set_text('Volume: %f' % self.player.get_volume())

    def play_track_callback(self, track):
        self.time_total.set_text(track.p_duration)
        self.title.set_text(track.title)


class Prompt(urwid.Edit):
    def __init__(self):
        super(Prompt, self).__init__()

    def do_ask(self, caption, text=None):
        self.set_caption(caption)
        if text is not None:
            self.set_text(text)

    def get_box(self):
        return urwid.Frame(self)

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'perform_search')
        elif key == 'esc':
            urwid.emit_signal(self, 'cancel_input')
        super(Prompt, self).keypress(size, key)

    def hide(self):
        self.set_caption('')
        self.set_edit_text('')


class Topstrip(urwid.Columns):
    def __init__(self):
        self.items = [
            urwid.Divider(u'\u2015')
        ]
        super(Topstrip, self).__init__(self.items)


class Botstrip(urwid.Columns):
    def __init__(self):
        self.current_view = urwid.Text('')
        self.items = [
            (5, urwid.Divider(u'\u2015')),
            ('pack', self.current_view),
            urwid.Divider(u'\u2015')
        ]
        super(Botstrip, self).__init__(self.items)

    def change_current_view(self, s=None):
        if s is not None:
            self.current_view.set_text('[ %s ]' % s)


class Tracklist(urwid.ListBox):
    def __init__(self, tracks=None):
        self._items = []
        self.top_strip = Topstrip()
        self.bot_strip = Botstrip()
        if tracks is not None:
            for track in tracks:
                self._items.append(TracklistItem(track))
        super(Tracklist, self).__init__(urwid.SimpleListWalker(self._items))

    def update(self, tracks):
        self._items = []
        for track in tracks:
            self._items.append(TracklistItem(track))
        self.body = urwid.SimpleListWalker(self._items)

    def add_track(self, track):
        self.body.append(track)

    def get_selected(self):
        return self.focus

    def get_box(self):
        return urwid.Frame(self, self.top_strip, self.bot_strip)


class TracklistItem(urwid.WidgetWrap):
    def __init__(self, track):
        self.api = track['api']
        self.title = track['title']
        self.url = track['url']
        self.duration = track['duration']
        self.p_duration = printable_duration(self.duration)
        self.item = [
            urwid.Text('%s' % self.title),
            (len(self.api) + 4, urwid.Padding(urwid.Text('[%s]' % self.api), 'center', len(self.api) + 2)),
            (10, urwid.Padding(urwid.Text(self.p_duration), 'right', len(self.p_duration))),
        ]
        self._w = urwid.AttrWrap(urwid.Columns(self.item), 'body', 'focus')

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'j':
            key = 'down'
        elif key == 'k':
            key = 'up'
        return key


class Playlist(Tracklist):
    def __init__(self, tracks=None):
        super(Playlist, self).__init__(tracks)
        self.bot_strip.change_current_view('Playlist')

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'play_track', self.focus)
        return super(Playlist, self).keypress(size, key)


class Searchlist(Tracklist):
    def __init__(self, tracks=None):
        super(Searchlist, self).__init__(tracks)
        self.bot_strip.change_current_view('Results')

    def set_result_text(self, q):
        self.bot_strip.change_current_view('Results: %s' % q)

    def keypress(self, size, key):
        if key == ' ':
            urwid.emit_signal(self, 'add_track', self.focus)
            pass
        elif key == 'enter':
            urwid.emit_signal(self, 'add_track', self.focus)
            urwid.emit_signal(self, 'play_track', self.focus)
        return super(Searchlist, self).keypress(size, key)


def printable_duration(secs):
    s = int(secs) / 1000
    m = s / 60
    s -= m * 60
    h = m / 60
    m -= h * 60
    if h > 0:
        return '%d:%02d:%02d ' % (h, m, s)
    else:
        return '%d:%02d ' % (m, s)
