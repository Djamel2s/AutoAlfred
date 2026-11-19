"""Robot profiles: physical capabilities and limits of each candidate humanoid.

The simulation uses the numeric fields. `description` and `limits` are what the
platform loads as the robot sheet (CAG) so the planner knows what is possible.
Values are estimates until the hardware is chosen and measured.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RobotProfile:
    id: str
    name: str
    description: str
    limits: list[str]
    can_grip: bool
    max_grip_weight_g: int
    max_grip_size_cm: float
    pick_success_rate: float
    navigation_success_rate: float
    ocr_min_font_pt: int
    battery_minutes: int
    extra: dict = field(default_factory=dict)


PROFILES: dict[str, RobotProfile] = {
    "tonypi": RobotProfile(
        id="tonypi",
        name="Hiwonder TonyPi",
        description=(
            "Humanoïde bipède 16 servos bus, Raspberry Pi 5, caméra HD sur tête 2 axes. "
            "SDK Python + OpenCV."
        ),
        limits=[
            "Pas de lidar : navigation approximative par repères visuels.",
            "Préhension très limitée : seulement de très petits objets légers (balle, petit cube).",
            "Ne porte qu'un objet à la fois.",
            "Batterie ~60 min.",
        ],
        can_grip=True,
        max_grip_weight_g=50,
        max_grip_size_cm=4.0,
        pick_success_rate=0.55,
        navigation_success_rate=0.85,
        ocr_min_font_pt=14,
        battery_minutes=60,
    ),
    "ainex": RobotProfile(
        id="ainex",
        name="Hiwonder AiNex (Standard)",
        description=(
            "Humanoïde bipède 24 servos bus, Raspberry Pi 5, caméra HD sur tête 2 axes, "
            "mains mécaniques, ROS + Gazebo."
        ),
        limits=[
            "Pas de lidar : navigation approximative par repères visuels.",
            "Préhension de petits objets légers uniquement.",
            "Ne porte qu'un objet à la fois.",
            "Batterie ~60 min.",
        ],
        can_grip=True,
        max_grip_weight_g=150,
        max_grip_size_cm=7.0,
        pick_success_rate=0.8,
        navigation_success_rate=0.9,
        ocr_min_font_pt=12,
        battery_minutes=60,
    ),
}


def get_profile(profile_id: str) -> RobotProfile:
    try:
        return PROFILES[profile_id]
    except KeyError:
        raise ValueError(f"Profil inconnu : {profile_id}. Profils : {', '.join(PROFILES)}") from None
