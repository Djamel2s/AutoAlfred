import pytest

from robot_stub.profiles import PROFILES, get_profile
from robot_stub.world import SCENARIOS, World


def perfect(profile_id: str):
    """Profile without randomness, to test the world rules themselves."""
    from dataclasses import replace

    return replace(get_profile(profile_id), pick_success_rate=1.0, navigation_success_rate=1.0)


@pytest.mark.parametrize("profile_id", list(PROFILES))
def test_ranger_solvable(profile_id):
    w = World(perfect(profile_id), "ranger")
    for obj, loc in [("balle_rouge", "table"), ("cube_bleu", "sol")]:
        assert w.navigate_to(loc)["ok"]
        assert w.pick(obj)["ok"]
        assert w.navigate_to("bac")["ok"]
        assert w.place("bac")["ok"]
    assert w.state()["success"]


def test_heavy_object_cannot_be_picked():
    w = World(perfect("ainex"), "ranger")
    w.navigate_to("table")
    res = w.pick("tasse")
    assert not res["ok"] and "trop lourd" in res["message"]


def test_one_object_at_a_time():
    w = World(perfect("ainex"), "ranger")
    w.navigate_to("table")
    assert w.pick("balle_rouge")["ok"]
    w.navigate_to("sol")
    assert not w.pick("cube_bleu")["ok"]


def test_place_requires_being_there():
    w = World(perfect("ainex"), "ranger")
    w.navigate_to("table")
    w.pick("balle_rouge")
    assert not w.place("bac")["ok"]


def test_small_text_needs_holding_the_label():
    w = World(perfect("ainex"), "lire_web")
    w.navigate_to("bureau")
    res = w.read_text("etiquette")
    assert not res["ok"] and "partial_text" in res
    assert w.pick("etiquette")["ok"]
    res = w.read_text("etiquette")
    assert res["ok"] and "AX-2041" in res["text"]
    assert w.state()["success"]


def test_blocked_route_requires_waypoint():
    w = World(perfect("ainex"), "imprevu")
    w.navigate_to("etagere")
    w.pick("cube_bleu")
    res = w.navigate_to("bureau")
    assert not res["ok"] and "table" in res["message"]
    assert w.navigate_to("table")["ok"]
    assert w.navigate_to("bureau")["ok"]
    assert w.place("bureau")["ok"]
    assert w.state()["success"]


def test_vague_search():
    w = World(perfect("ainex"), "retrouver")
    w.navigate_to("etagere")
    res = w.detect("petit truc rond pour jouer")
    assert res["matches"][0]["id"] == "balle_rouge"
    assert w.state()["success"]


def test_same_seed_same_outcomes():
    def run(seed):
        w = World(get_profile("tonypi"), "ranger", seed)
        w.navigate_to("table")
        return [w.pick("balle_rouge")["ok"] or w.place("table")["ok"] for _ in range(10)]

    assert run(42) == run(42)


def test_reset_restores_scenario():
    w = World(perfect("ainex"), "ranger")
    w.navigate_to("table")
    w.pick("balle_rouge")
    w.reset("ranger")
    assert w.robot_location == "couloir" and w.holding is None
    assert w.obj("balle_rouge").location == "table"
    assert SCENARIOS["ranger"].objects[0].location == "table"  # template untouched


def test_unknown_profile():
    with pytest.raises(ValueError):
        get_profile("nao")
