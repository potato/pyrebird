from os import listdir
from os.path import splitext, split, join
from imp import load_source


def search(q):
    result = []
    for api in apis:
        for r in api.search(q):
            r.update({'api': api.tag})
            result += [r]
    return sorted(result, key=lambda x: x['title'])

apis = []
for f in filter(lambda x: x != '__init__.py' and x.endswith('.py'), listdir(split(__file__)[0])):
    module = load_source(splitext(f)[0], join(split(__file__)[0], f))
    try:
        apis.append(module.API())
    except:
        print '[E] %s doesn\'t have an API class' % f
