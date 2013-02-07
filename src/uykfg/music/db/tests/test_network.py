
from unittest import TestCase

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.music.db.network import Link
from uykfg.support.configure import Config


class TestNetwork(TestCase):

    def test_network(self):

        session = startup(Config(db_url='sqlite:///'))

        alice = Artist(name='alice')
        session.add(alice)
        bob = Artist(name='bob')
        session.add(bob)
        session.add(Link(src=bob, dst=alice))
        assert len(alice.srcs) == 1, alice.srcs
        assert alice.srcs[0].src == bob
