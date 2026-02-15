from BaseClasses import Entrance, Region
from .bases import BoHTestBase


class TestDefaultLogic(BoHTestBase):
    def test_construct(self):
        self.assertTrue(True, f"World did not create")

    def test_room_progression_step_by_step(self):
        state = self.multiworld.state
        not_yet_checked:list[Region] = [r for r in self.world.get_regions()]

        # start from the 'always accessible' default region "Menu"
        menu = self.world.get_region("Menu")
        not_yet_checked.remove(menu)
        entered:list[Region] = [menu]
        touched:list[Region] = []
        # assert Menu can enter at least one room #
        c = 0
        for t in [a for a in not_yet_checked for b in a.entrances if b.parent_region.name == "Menu"]:
            self.assertTrue(t.can_reach(state), f"{t.name} should be accessible from Menu")
            c += 1
            touched.append(t)
        self.assertTrue(c > 0, f"No region accessible from Menu!")

        while len(touched) > 0:
            current = touched[0]
            can_access = current.can_reach(state)
            pre=[]
            if not can_access: # collect its pre-requisite event-itemS and retry
                pre = [p.parent_region.name for p in current.entrances]
                self.collect_by_name(pre)
            self.assertTrue(current.can_reach(state), f"Collected '{pre}' from '{pre}' but can not access '{current}'")

            e:Entrance
            for e in current.exits:
                conreg = e.connected_region
                exists = any(a.name == conreg.name for a in touched)
                if not exists:
                    touched.append(conreg)

            touched.remove(current)
            entered.append(current)


            #each: collect prev region-location-eventitem and check access to current-region
            #prev = [p for p in r.entrances]
            #for p in prev:
            #    c = self.collect_by_name(p.parent_region.name)
            #    self.assertTrue(len(c) > 0)
            #    self.assertTrue(r.can_reach(state), f"Collected '{p.parent_region.name}' but can not access '{r.name}'")


            #regions.remove(r)

    def scrub_items(self):
        locations = self.world.get_locations()
        items = [i for l in locations for i in self.get_items_by_name(l.name)]
        self.remove(items)