Pyrebird
========

Pyrebird is a hackable music player for various music sources (soundcloud, ... nope, it's only soundcloud yet) with various user interfaces (urwid only yet).

### Installation

1. clone source: `git clone https://github.com/potato/pyrebird.git`
2. install gstreamer, plugins-ugly for gstreamer and the python bindings
3. install other dependencies: `pip install urwid requests`
4. run `python pyrebird.py` to start the application

### Usage

Currently Pyrebird comes with an urwid ui, which accepts the following keystrokes:
* `s`: prompt for search (`escape` cancels the prompt)
* `p`: toggle play/pause
* `j` or `up`: move up in the tracklist
* `k` or `down`: move down in the tracklist
* `h` or `left`: decrease volume
* `l` or `right`: increase volume
* `q`: quits Pyrebird

### TODO

* more apis (for online streams and local files too)
* more UIs (perhaps some socket-listener-thingy too)
* config file handling

### Bugs

Bugs or suggestions? Visit the [issue tracker](https://github.com/potato/pyrebird/issues).

### [License](https://github.com/potato/pyrebird/blob/master/LICENSE)

