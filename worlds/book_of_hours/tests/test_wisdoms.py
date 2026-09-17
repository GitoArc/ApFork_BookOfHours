from BaseClasses import Region, Location
from .bases import BOHTestBase
from .._generate_locations import WISDOMS_GENERIC_PROGRESSION, WISDOMS_TIERS, WISDOMS_PATHS, \
    WISDOMS_GENERIC_PROGRESSION_NAMES, WISDOMS_TIERS_NAMES, WISDOMS_PATHS_REGIONS_NAMES
from ..enums import BOHStrEnums
from ..functions import find_roman
from ..locations import BOHLocation

roman1to9 = ["I","II","III","IV","V","VI","VII","VIII","IX"]


class TestWisdoms(BOHTestBase):
    run_default_tests = False

    def test_generic_progression(self):
        if not self.world.options.insanitree.generic_progression_enabled:
            return

        wt: Region = self.world.get_region(BOHStrEnums.TreeOfWisdoms)  # will raise Exception if not found
        generics:list[BOHLocation] = [a for a in wt.locations if not a.is_event and a.name.startswith("Commit ") and a.name.split(" ", 2)[1].isnumeric()]
        # from  "index 0"   to  "arr[COUNT]"
        # from  "Commit 1"  to  "Commit COUNT"
        for i in range(0, self.world.options.insanitree.generic_progression_count):
            sublocs_for_i_committed = [a for a in generics if f" {i+1} " in a.name]
            self.assertTrue(len(sublocs_for_i_committed) == self.world.options.insanitree.generic_progression_rewards_per_loc)
        for j in range(self.world.options.insanitree.generic_progression_count, 81):
            name = WISDOMS_GENERIC_PROGRESSION_NAMES[j]
            self.assertRaises(KeyError, lambda n=name: self.world.get_region(n))
        l1 = generics[0]
        l2 = generics[1]
        l3 = generics[2]
        self.assertTrue(l1.can_reach(self.multiworld.state))
        self.assertFalse(l3.can_reach(self.multiworld.state))
        self.multiworld.state.add_item("WT G", self.player, 1)
        self.assertTrue(l3.can_reach(self.multiworld.state))

        pass

    def test_tiered_progression(self):
        if not self.world.options.insanitree.tiered_progression_enabled:
            return

        wt: Region = self.world.get_region(BOHStrEnums.TreeOfWisdoms)
        for t in range(10):
            expectedLocAmount = self.world.options.insanitree.tiered_progression_rewards_for_tier[t]
            expectedLocType = self.world.options.insanitree.tiered_progression_locprogtype_for_tier[t]
            rname = WISDOMS_TIERS_NAMES[t]
            tlocs = [l for l in wt.locations if not l.is_event and rname in l.name and "- Reward " in l.name]
            self.assertTrue(len(tlocs) == expectedLocAmount)
            for l in tlocs:
                self.assertTrue(l.progress_type == expectedLocType)

    def test_paths_progression(self):
        if not self.world.options.insanitree.path_progression_enabled:
            return

        _all_locs = self.world.get_locations()
        for w in WISDOMS_PATHS_REGIONS_NAMES:
            t = find_roman(w)
            limit_amount = self.world.options.insanitree.path_progression_rewards_per_loc[t]
            limit_loctype = self.world.options.insanitree.path_progression_locprogtype_for_tier[t]
            # assert theres ONLY the expected amount of locations

            p_locs:list[Location] = [a for a in _all_locs if w in a.name]
            self.assertTrue(len(p_locs) == limit_amount)

            for i in range(1, 1+limit_amount):
                loc = self.world.get_location(f"{w} - Reward {i}")
                self.assertTrue(loc.progress_type == limit_loctype)

class Test_Off(TestWisdoms):
    options = {
        "insanitree": {
            "generic_progression_enabled": 0,
            "tiered_progression_enabled": 0,
            "path_progression_enabled": 0
        }
    }


class Test_All_Max(TestWisdoms):
    options = {
        "insanitree": {
            "generic_progression_enabled": 1,
            "generic_progression_locations": 81,
            "generic_progression_rewards_per": 9,
            "tiered_progression_enabled": 1,
            "tiered_progression_rewards_per_":      "9999999999",
            "tiered_progression_locprogtypes_per_": "1111111111",
            "path_progression_enabled": 1,
            "path_progression_rewards_per_":         "999999999",
            "path_progression_locprogtypes_per_":    "111111111",
        }
    }
    def test_report(self):
        ll = self.world.get_region(BOHStrEnums.TreeOfWisdoms).locations
        ll = list(ll)
        ll = sorted(ll)
        pass


class Test_Tiers1To5_Mixed(TestWisdoms):
    options = {
        "insanitree": {
            "generic_progression_enabled": 0,
            "path_progression_enabled": 0,
            "tiered_progression_enabled": 1,
            "tiered_progression_rewards_per_": "0123456789",
            "tiered_progression_locprogtypes_per_": "2211333333"
        }
    }
