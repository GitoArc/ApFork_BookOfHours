from ..jsondump import lessons, skills


class TestJson:

    def test_lessons_match_skill(self) -> None:
        for i in range(0,74):
            try:
                l = lessons[i]
                s = skills[i]
                ls = l["IdStr"]
                ss = s["IdStr"]
                lid0 = ls[1:]
                sid0 = ss[1:]
                assert ls[1:] == ss[1:], f"mismatch at {i} - {ls} {ss}"
            except IndexError:
                if lessons[i]["IdStr"] == "x.summon.echidna":
                    assert True # echidna has no equivalent skill, only a lesson
                else:
                    assert False
