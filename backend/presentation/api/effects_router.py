"""AR effects + color-grading preset marketplace (Phase 5.2)."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..dependencies import db_models  # legacy ORM access
from ..dependencies import get_current_user
from ..dependencies import get_session_for_router as get_session

EffectLibraryDB = db_models.EffectLibraryDB
ColorGradingPresetDB = db_models.ColorGradingPresetDB

router = APIRouter(prefix="/api/effects", tags=["effects"])


def _serialize_effect(e: EffectLibraryDB) -> dict:
    return {
        "id": e.id,
        "name": e.name,
        "description": e.description,
        "category": e.category,
        "effect_type": e.effect_type,
        "parameters": json.loads(e.parameters) if e.parameters else None,
        "thumbnail_url": e.thumbnail_url,
        "is_premium": e.is_premium,
        "is_ar": e.is_ar,
        "usage_count": e.usage_count,
        "creator_id": e.creator_id,
    }


def _serialize_preset(p: ColorGradingPresetDB) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "category": p.category,
        "settings": json.loads(p.settings) if p.settings else {},
        "is_system": p.is_system,
        "creator_id": p.creator_id,
        "usage_count": p.usage_count,
    }


@router.get("")
def list_effects(
    category: str | None = None,
    is_ar: bool | None = None,
    session: Session = Depends(get_session),
):
    stmt = select(EffectLibraryDB)
    if category:
        stmt = stmt.where(EffectLibraryDB.category == category)
    if is_ar is not None:
        stmt = stmt.where(EffectLibraryDB.is_ar == is_ar)
    effects = session.exec(stmt.order_by(EffectLibraryDB.usage_count.desc())).all()
    return {"success": True, "effects": [_serialize_effect(e) for e in effects]}


@router.get("/{effect_id}")
def get_effect(effect_id: str, session: Session = Depends(get_session)):
    e = session.get(EffectLibraryDB, effect_id)
    if not e:
        raise HTTPException(status_code=404, detail="Effect not found")
    return {"success": True, "effect": _serialize_effect(e)}


@router.post("")
def submit_effect(
    body: dict,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """User-generated effect submission (sandbox JSON shader spec)."""
    name = body.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Effect name required")
    parameters = body.get("parameters")
    e = EffectLibraryDB(
        name=name,
        description=body.get("description"),
        category=body.get("category", "user"),
        effect_type=body.get("effect_type", "shader"),
        parameters=json.dumps(parameters) if parameters is not None else None,
        thumbnail_url=body.get("thumbnail_url"),
        is_premium=bool(body.get("is_premium", False)),
        is_ar=bool(body.get("is_ar", False)),
        creator_id=current_user.id,
    )
    session.add(e)
    session.commit()
    session.refresh(e)
    return {"success": True, "effect": _serialize_effect(e)}


@router.get("/presets/color-grading")
def list_color_presets(session: Session = Depends(get_session)):
    presets = session.exec(
        select(ColorGradingPresetDB).order_by(ColorGradingPresetDB.usage_count.desc())
    ).all()
    return {"success": True, "presets": [_serialize_preset(p) for p in presets]}
