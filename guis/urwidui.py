import urwid
from math import ceil


class UI():
    def __init__(self, player=None):
        self.palette = [
                ('body', 'yellow', ''),
                ('focus', 'black', 'brown'),
                ]
        self.player = player
        self.time_total = None
        self.time_current = None
        self.title = None
        self.screen = urwid.raw_display.Screen()
        self.width, self.height = self.screen.get_cols_rows()
        self.container = urwid.Frame(self.draw_playlist(), self.draw_player(), self.draw_statusbar())
        self.loop = urwid.MainLoop(self.container, self.palette, unhandled_input=self._handle_global_input)
        self.loop.set_alarm_in(1, self.periodic_update, self)

    def draw_playlist(self):
        self.playlist = Tracklist(self.player.search('foxsky'))
        w = urwid.Frame(self.playlist, urwid.AttrWrap(urwid.Divider(u'\u2015'), 'body'))
        return w

    def draw_player(self):
        self.topbar = Topbar()
        return urwid.AttrWrap(self.topbar, 'body')

    def draw_statusbar(self):
        w = urwid.AttrWrap(urwid.Pile([
                urwid.Columns([
                    urwid.Divider(u'\u2015'),
                    (8, urwid.Text('[23/99]')),
                ]),
                urwid.Text('<write something here>'),
        ]), 'body')
        return w

    def draw_input(self, txt):
        urwid.PopUpTarget(urwid.Text(txt, 'center'))

    def _handle_global_input(self, key):
        if key == 'q':
            raise urwid.ExitMainLoop()
        elif key == 's':
            self.draw_input('hell')
        elif key == 'enter':
            tr = self.playlist.focus
            self.topbar.update(tr)
            self.player.play(tr.url)
        elif key in ('h', 'left'):
            self.player.volume_dec()
        elif key in ('l', 'right'):
            self.player.volume_inc()
        elif key in ('p', ' '):
            self.player.pause()

    def periodic_update(self, loop, caller):
        caller.topbar.update_time(caller.player.player)
        loop.set_alarm_in(1, caller.periodic_update, caller)

    def main_loop(self):
        self.loop.run()


class Topbar(urwid.Columns):
    def __init__(self):
        self.time_total = urwid.Text('0:00')
        self.time_current = urwid.Text('0:00')
        self.title = urwid.Text('')
        self._items = [
            (len(self.time_total.get_text()[0]), self.time_total),
            (3, urwid.Text(' / ')),
            (len(self.time_total.get_text()[0]), self.time_current),
            (3, urwid.Text('   ')),
            self.title
            ]
        super(Topbar, self).__init__(self._items)

    def update(self, tr):
        self.time_total = urwid.Text(tr._duration)
        self.time_current = urwid.Text('0:00')
        self.title = urwid.Text(tr.title)
        self._items = [
            (len(self.time_total.get_text()[0]), self.time_total),
            (3, urwid.Text(' / ')),
            (len(self.time_total.get_text()[0]), self.time_current),
            (3, urwid.Text('   ')),
            self.title
            ]
        super(Topbar, self).__init__(self._items)

    def update_time(self, player):
        if 'GST_STATE_PLAYING' in [x.value_name for x in player.get_state()]:
            time = ceil(float(player.get_clock().get_time()) / 1000000.0)
            self.time_current.set_text(printable_duration(time))


class Tracklist(urwid.ListBox):
    def __init__(self, tracks):
        self.items = []
        for track in tracks:
            self.items.append(TracklistItem(track))
        super(Tracklist, self).__init__(urwid.SimpleListWalker(self.items))


class TracklistItem(urwid.WidgetWrap):
    def __init__(self, tr):
        self.api = tr['api']
        self.title = tr['title']
        self.url = tr['url']
        self._duration = printable_duration(tr['duration'])
        self.item = [
                urwid.Text('%s' % self.title),
                (len(self.api) + 4, urwid.Padding(urwid.Text('[%s]' % self.api), 'center', len(self.api) + 2)),
                (10, urwid.Padding(urwid.Text(self._duration), 'right', len(self._duration))),
        ]
        self._w = urwid.AttrWrap(urwid.Columns(self.item), 'body', 'focus')

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'j':
            return 'down'
        elif key == 'k':
            return 'up'
        else:
            return key


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
