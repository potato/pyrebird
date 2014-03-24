import requests


class API():
    def __init__(self):
        self.base_url = 'http://api.soundcloud.com'
        self.client_id = 'b45b1aa10f1ac2941910a7f0d10f8e28'
        self.tag = 'SC'
        self.name = 'Soundcloud'

    def search(self, q):
        r = self.make_request('tracks', {'q': q})
        res = []
        if r.status_code == 200:
            for t in r.json():
                res.append({'title': t['title'], 'duration': t['duration'], 'url': t['stream_url'] + '?client_id=%s' % self.client_id})
        return res

    def make_request(self, rtype, args={}):
        args.update({'client_id': self.client_id})
        return requests.get(self.base_url + '/' + rtype + '.json', params=args)
