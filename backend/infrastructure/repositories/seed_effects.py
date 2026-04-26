"""Seed the AR effect library + color-grading preset catalogue."""
from __future__ import annotations

import json
import logging

from sqlmodel import Session, select

from .models import EffectLibraryDB, ColorGradingPresetDB

logger = logging.getLogger(__name__)


SEED_EFFECTS: list[dict] = [
    # Hand-built starter shaders + face filters per refactor250426 §7.
    {"name": "Soft Glow", "category": "filter", "effect_type": "shader", "is_ar": False,
     "description": "Bloom + gentle vignette.",
     "parameters": {"bloom": 0.6, "vignette": 0.25}},
    {"name": "Vintage 8mm", "category": "filter", "effect_type": "shader", "is_ar": False,
     "description": "Film grain, warm shift, slight wobble.",
     "parameters": {"grain": 0.4, "warm": 0.3, "wobble": 0.05}},
    {"name": "VHS Glitch", "category": "filter", "effect_type": "shader", "is_ar": False,
     "description": "Chromatic aberration + scanlines.",
     "parameters": {"aberration": 0.3, "scanlines": 0.7}},
    {"name": "Mirror World", "category": "transform", "effect_type": "shader", "is_ar": False,
     "description": "Symmetrical mirror down the centre.",
     "parameters": {"axis": "vertical"}},
    {"name": "Anime Eyes", "category": "face", "effect_type": "facemesh", "is_ar": True,
     "description": "Enlarged sparkle eyes via Face Mesh landmark warp.",
     "parameters": {"eye_scale": 1.4, "sparkle": True}},
    {"name": "Puppy Filter", "category": "face", "effect_type": "facemesh", "is_ar": True,
     "description": "Ears + nose + tongue overlay.",
     "parameters": {"sticker_set": "puppy"}},
    {"name": "Neon Outline", "category": "face", "effect_type": "facemesh", "is_ar": True,
     "description": "Glowing outline tracing face contour.",
     "parameters": {"colour": "#00f5ff", "thickness": 4}},
    {"name": "Background Blur", "category": "background", "effect_type": "segmentation", "is_ar": True,
     "description": "MediaPipe selfie-segmentation blur.",
     "parameters": {"strength": 12}},
]

SEED_PRESETS: list[dict] = [
    # LUT-driven, settings stored as a small JSON spec the editor turns into
    # CSS filter / WebGL shader inputs at apply-time.
    {"name": "Cinematic Teal-Orange", "category": "cinema",
     "settings": {"lift": [0.0, -0.05, -0.1], "gamma": [1.05, 1.0, 0.92], "gain": [1.0, 1.0, 1.05]}},
    {"name": "Warm Sunset", "category": "warm",
     "settings": {"temperature": 0.25, "tint": 0.05, "saturation": 0.15}},
    {"name": "Cold Steel", "category": "cool",
     "settings": {"temperature": -0.25, "tint": -0.05, "saturation": -0.1}},
    {"name": "B&W Classic", "category": "monochrome",
     "settings": {"saturation": -1.0, "contrast": 0.15}},
    {"name": "Faded Film", "category": "film",
     "settings": {"black_lift": 0.08, "white_clip": -0.05, "saturation": -0.2}},
    {"name": "High Contrast Pop", "category": "punchy",
     "settings": {"contrast": 0.35, "saturation": 0.2, "vibrance": 0.15}},
]


def seed_effects(session: Session, *, force: bool = False) -> int:
    inserted = 0

    existing_eff_keys: set[str] = set()
    if not force:
        rows = session.exec(select(EffectLibraryDB)).all()
        existing_eff_keys = {r.name for r in rows}
    for spec in SEED_EFFECTS:
        if spec["name"] in existing_eff_keys:
            continue
        session.add(EffectLibraryDB(
            name=spec["name"],
            description=spec["description"],
            category=spec["category"],
            effect_type=spec["effect_type"],
            parameters=json.dumps(spec.get("parameters", {})),
            is_premium=spec.get("is_premium", False),
            is_ar=spec.get("is_ar", False),
            creator_id="_clipsmith_seed",
        ))
        inserted += 1

    existing_preset_keys: set[str] = set()
    if not force:
        rows = session.exec(select(ColorGradingPresetDB)).all()
        existing_preset_keys = {r.name for r in rows}
    for spec in SEED_PRESETS:
        if spec["name"] in existing_preset_keys:
            continue
        session.add(ColorGradingPresetDB(
            name=spec["name"],
            description=spec.get("description"),
            category=spec["category"],
            settings=json.dumps(spec["settings"]),
            is_system=True,
        ))
        inserted += 1

    if inserted:
        session.commit()
    logger.info("Seeded %d effects/presets", inserted)
    return inserted
