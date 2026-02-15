from test.bases import WorldTestBase

from ..world import BoHWorld

class BoHTestBase(WorldTestBase):
    game = "Book of Hours"
    world: BoHWorld