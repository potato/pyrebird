import socket
from os.path import join

MPD_HOST = 'localhost'
MPD_PORT = 6600
MPD_MUSIC_DIR = ''  # fill me


class API():
    def __init__(self):
        self.tag = 'MPD'
        self.name = 'mpdclient'

    def search(self, q):
        # comment out the line below to enable mpd search results
        return []
        t_title = self.do_command('search title "%s"' % q)
        t_artist = self.do_command('search artist "%s"' % q)
        return self.digest_data(t_title, t_artist)

    def do_command(self, cmd):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((MPD_HOST, MPD_PORT))
        self.socket.recv(1024)
        self.socket.send(cmd + "\r\n")
        ret = ''
        while True:
            chunk = self.socket.recv(1024)
            ret += chunk
            if chunk.endswith("OK\n"):
                break
        self.socket.close()
        return ret[:-3]

    def digest_data(self, t_title, t_artist):
        ret = []
        tmp = {'url': '', 'duration': 0, 'title': ''}
        for d in t_title.split("\n"):
            if d == '':
                continue
            (key, value) = d.split(': ', 1)
            if key == 'file':
                tmp['url'] = 'file://' + join(MPD_MUSIC_DIR, value)
            elif key == 'Time':
                tmp['duration'] = int(value) * 1000
            elif key == 'Artist':
                tmp['title'] = value
            elif key == 'Title':
                tmp['title'] += ' - %s' % value
            elif key == 'Genre':
                ret.append(tmp)
        tmp = {'url': '', 'duration': 0, 'title': ''}
        for d in t_artist.split("\n"):
            if d == '':
                continue
            (key, value) = d.split(': ', 1)
            if key == 'file':
                tmp['url'] = 'file://' + join(MPD_MUSIC_DIR, value)
            elif key == 'Time':
                tmp['duration'] = int(value) * 1000
            elif key == 'Artist':
                tmp['title'] = value
            elif key == 'Title':
                tmp['title'] += ' - %s' % value
            elif key == 'Genre':
                ret.append(tmp)
                tmp = {'url': '', 'duration': 0, 'title': ''}
        return ret
