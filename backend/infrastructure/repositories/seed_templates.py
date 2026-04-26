"""Seed the AI Template library with curated starter templates."""
from __future__ import annotations

import json
import logging
from typing import Iterable

logger = logging.getLogger(__name__)

# Curated starter templates. These are intentionally minimal JSON specs:
# the editor picks them up and applies as a starting state.
SEED_TEMPLATES: list[dict] = [
    {
        "name": "Clean Cut",
        "description": "Minimal text overlay, white-on-black title at intro.",
        "category": "general",
        "style": "minimal",
        "is_premium": False,
        "tags": ["minimal", "intro", "text"],
        "project_data": {
            "tracks": [
                {"type": "video", "items": []},
                {
                    "type": "text",
                    "items": [
                        {
                            "text": "Your title",
                            "start": 0.0,
                            "end": 2.5,
                            "color": "#ffffff",
                            "size": 64,
                            "weight": 700,
                        }
                    ],
                },
            ]
        },
    },
    {
        "name": "Vibrant Pop",
        "description": "High-saturation grade + animated emoji burst.",
        "category": "entertainment",
        "style": "vibrant",
        "is_premium": False,
        "tags": ["color", "animated", "fun"],
        "project_data": {
            "color_grading": {"saturation": 1.4, "vibrance": 1.2, "contrast": 1.15},
            "transitions": [{"type": "zoom", "duration": 0.3}],
        },
    },
    {
        "name": "Cinematic",
        "description": "Letterbox, teal-orange grade, slow zoom.",
        "category": "entertainment",
        "style": "cinematic",
        "is_premium": False,
        "tags": ["letterbox", "cinematic", "moody"],
        "project_data": {
            "letterbox": {"top": 0.1, "bottom": 0.1},
            "color_grading": {"preset": "teal-orange", "saturation": 0.95},
            "speed": [{"start": 0.0, "end": 1.0, "rate": 0.85}],
        },
    },
    {
        "name": "Tutorial",
        "description": "Step-by-step layout with chapter markers.",
        "category": "education",
        "style": "modern",
        "is_premium": False,
        "tags": ["education", "steps", "tutorial"],
        "project_data": {
            "chapters": [
                {"title": "Step 1", "start": 0.0, "end": 0.0},
                {"title": "Step 2", "start": 0.0, "end": 0.0},
                {"title": "Step 3", "start": 0.0, "end": 0.0},
            ],
            "tracks": [
                {"type": "video", "items": []},
                {
                    "type": "text",
                    "items": [
                        {"text": "Step 1", "start": 0, "end": 5, "size": 48},
                    ],
                },
            ],
        },
    },
    {
        "name": "Recipe Card",
        "description": "Ingredient list overlay + countdown timer.",
        "category": "food",
        "style": "playful",
        "is_premium": False,
        "tags": ["food", "recipe", "list"],
        "project_data": {
            "tracks": [
                {"type": "video", "items": []},
                {"type": "ingredient_list", "items": []},
                {"type": "timer", "items": []},
            ]
        },
    },
    {
        "name": "Workout Sequence",
        "description": "Set/rep counter, beat-synced cuts.",
        "category": "fitness",
        "style": "energetic",
        "is_premium": False,
        "tags": ["fitness", "counter", "beat-sync"],
        "project_data": {
            "counter": {"max_reps": 12, "rest_seconds": 30},
            "beat_sync": True,
        },
    },
    {
        "name": "Story Arc",
        "description": "Three-act structure with smooth transitions.",
        "category": "entertainment",
        "style": "narrative",
        "is_premium": True,
        "price": 2.99,
        "tags": ["narrative", "storytelling", "premium"],
        "project_data": {
            "arc": ["setup", "conflict", "resolution"],
            "transitions": [{"type": "fade", "duration": 0.5}],
        },
    },
    {
        "name": "News Briefing",
        "description": "Lower-third, ticker, professional grade.",
        "category": "news",
        "style": "professional",
        "is_premium": False,
        "tags": ["news", "ticker", "lower-third"],
        "project_data": {
            "lower_third": {"primary": "#0a3d62", "accent": "#ffffff"},
            "ticker": {"speed": 80, "items": []},
        },
    },
    {
        "name": "Comedy Reaction",
        "description": "Snap zoom on punchline, sound effects.",
        "category": "comedy",
        "style": "fun",
        "is_premium": False,
        "tags": ["comedy", "reaction", "sfx"],
        "project_data": {
            "reactions": [{"type": "zoom-snap", "trigger": "punchline"}],
        },
    },
    {
        "name": "Travel Vlog",
        "description": "Map intro, location pin overlays, ambient music slot.",
        "category": "travel",
        "style": "cinematic",
        "is_premium": False,
        "tags": ["travel", "map", "vlog"],
        "project_data": {
            "intro_map": True,
            "location_pins": [],
            "music_slot": {"genre": "ambient"},
        },
    },
]


def seed_ai_templates(session, *, force: bool = False) -> int:
    """Insert SEED_TEMPLATES into AITemplateDB if absent. Returns count
    inserted. Idempotent: skips templates whose name+style already exists.
    """
    from sqlmodel import select

    from backend.infrastructure.repositories.models import AITemplateDB

    existing_keys: set[tuple[str, str]] = set()
    if not force:
        rows = session.exec(select(AITemplateDB)).all()
        existing_keys = {(r.name, r.style) for r in rows}

    inserted = 0
    for spec in SEED_TEMPLATES:
        key = (spec["name"], spec["style"])
        if key in existing_keys:
            continue
        row = AITemplateDB(
            name=spec["name"],
            description=spec["description"],
            category=spec["category"],
            style=spec["style"],
            project_data=json.dumps(spec["project_data"]),
            is_premium=spec.get("is_premium", False),
            price=spec.get("price", 0.0),
            tags=json.dumps(spec.get("tags", [])),
            is_public=True,
            creator_id="_clipsmith_seed",
            usage_count=0,
        )
        session.add(row)
        inserted += 1
    if inserted:
        session.commit()
    logger.info("Seeded %d AI templates", inserted)
    return inserted
