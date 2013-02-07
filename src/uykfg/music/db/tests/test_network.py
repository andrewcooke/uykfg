
from unittest import TestCase

from uykfg.music.db import startup
from uykfg.music.db.catalogue import Artist
from uykfg.support.configure import Config


class TestNetwork(TestCase):

    def test_network(self):

        session = startup(Config(db_url='sqlite:///'))

        alice = Artist(name='alice')
        session.add(alice)
        bob = Artist(name='bob')
        session.add(bob)
        bob.srcs.append(alice)
        assert len(alice.dsts) == 1, alice.dsts
