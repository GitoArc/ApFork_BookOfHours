from .bases import BoHTestBase
from ..GenericFilter import parseFilterstring
from ..jsondump import everything
from ..options import BoHOptions


class TestOptions(BoHTestBase):

    # more a "compile-time" test (if the option does not exist, I'll know before test runs)
    def test_world_options_not_None(self):
        ops = self.world.options
        assert ops.goal is not None
        assert ops.room_goal is not None
        #assert ops.memorinsanity is not None
        #assert ops.insoulnity is not None
        #assert ops.terrainsanity is not None
        pass


    def test_every_option_has_display_name(self):
        options:BoHOptions = self.world.options
        members = vars(options)
        for s in members:
            op = getattr(options, s)
            self.assertTrue(getattr(op, "display_name") != "", f"{s} has no display_name set")


    def test_parse_filterstring(self):
        lines = [
            "__all<2__filler__50",
            "persistent__all<2__progression__5",
            "persistent__all<3__useful__10",
            "persistent__all<4__useful__10",
            "hindsight,salt__any>0__progression+useful__30"
        ]
        for line in lines:
            passed = []
            filterObj = parseFilterstring(line)
            for e in everything:
                if filterObj.evaluate(e):
                    passed.append(e)
            # now assert what 'filterObj.evaluate' has filtered (without using .evaluate()):
            for p in passed:
                # manually check each stat without .evaluate()
                # ; That did 'a->c', now use 'b->c' to check if 'a' set 'c' correctly
                targetStringFound = False
                for t in filterObj.targets:
                    targetStringFound = targetStringFound or p.contains_substr(t)
                self.assertTrue(targetStringFound, f"{p} was not a valid target but got caught")

                predicateMatchedAspects = filterObj.filterPredicate.evaluate_dict(p.Aspects)
                predicateMatchedTerrainReqs = filterObj.filterPredicate.evaluate_dict(p.Requires)

                self.assertTrue(predicateMatchedAspects or predicateMatchedTerrainReqs, f"{p} was incorrectly passed")
            pass


class TestOption_MemoryProgressionOff(BoHTestBase):
    run_default_tests = False
    options = {
        "memory_progression": {
            "locations": 0
        }
    }

    def test_locations_do_not_exists(self):
        l = [a for a in self.world.get_locations() if "recall" in a.name or "memories" in a.name]
        self.assertTrue(len(l)==0, f"")

class TestOption_MemoryProgressionOn(BoHTestBase):
    run_default_tests = False
    options = {
        "memory_progression": {
            "locations": 40
        }
    }

    def test_n_locations_exist(self):
        l = [a for a in self.world.get_locations() if "Recall" in a.name and "memories" in a.name]
        self.assertTrue(len(l) == 40, f"")