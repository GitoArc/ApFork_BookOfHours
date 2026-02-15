from .bases import BoHTestBase


class Test(BoHTestBase):
    def test_location_event_item_pairs(self):
        events = [l for l in self.world.get_locations() if l.locked]
        for v in events:
            self.assertTrue(v.name == v.item.name, f"'{v.name}' has item '{v.item.name}'")
