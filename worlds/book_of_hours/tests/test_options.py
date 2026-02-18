from .bases import BoHTestBase
from ..options import BoHOptions


class TestOptions(BoHTestBase):

    def test_every_option_has_display_name(self):
        options:BoHOptions = self.world.options
        members = vars(options)
        for s in members:
            op = getattr(options, s)
            self.assertTrue(getattr(op, "display_name") != "", f"{s} has no display_name set")

    # more a "compile-time" test (if the option does not exist, I'll know before test runs)
    def test_world_options_not_None(self):
        ops = self.world.options
        assert ops.goal is not None
        assert ops.room_goal is not None
        assert ops.memorinsanity is not None
        assert ops.insoulnity is not None
        assert ops.terrainsanity is not None
        pass