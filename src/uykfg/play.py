
from uykfg.music.db import startup
from uykfg.support.configure import Config
from uykfg.mpd_.play import play_links


def play():
    config = Config.default()
    session = startup(config)
    play_links(session, config)


if __name__ == '__main__':
    play()
