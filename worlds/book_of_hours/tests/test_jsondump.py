from ..jsondump import lessons, skills


class TestJson:

    def test_lessons_match_id_with_skill(self) -> None:
        _lessons = lessons.copy()
        _skills = skills.copy()
        for i in range(0,73): # 73 skills in game
            l = _lessons[0]
            s = _skills[0]
            ls = l.IdStr
            ss = s.IdStr
            assert ls[1:] == ss[1:], f"mismatch at {i} - {ls} {ss}"
            _lessons.remove(l)
            _skills.remove(s)

        assert len(_skills) == 0
        assert len(_lessons) == 1
        assert _lessons[0].IdStr == "x.summon.echidna", f"the last lesson, no matching skill, was not echidna."
