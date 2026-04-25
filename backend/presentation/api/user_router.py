from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ...application.dtos.follow_dto import FollowResponseDTO, FollowStatusDTO
from ...application.dtos.profile_dto import ProfileResponseDTO
from ...application.use_cases.get_user_profile import GetUserProfileUseCase
from ...application.use_cases.manage_follows import ManageFollowsUseCase
from ...domain.ports.repository_ports import (
    FollowRepositoryPort,
    UserRepositoryPort,
    VideoRepositoryPort,
)
from ...application.use_cases.block_user import BlockUserUseCase, UnblockUserUseCase
from ..dependencies import (
    get_block_user_use_case,
    get_current_user as _resolve_current_user,
    get_follow_repo,
    get_unblock_user_use_case,
    get_user_block_repo,
    get_user_repo,
    get_video_repo,
)
from ...domain.ports.user_block_port import UserBlockRepositoryPort

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(user=Depends(_resolve_current_user)):
    return {"user_id": user.id, "username": user.username}

@router.get("/{username}", response_model=ProfileResponseDTO)
def get_user_profile(
    username: str,
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    video_repo: VideoRepositoryPort = Depends(get_video_repo)
):
    try:
        use_case = GetUserProfileUseCase(user_repo, video_repo)
        return use_case.execute(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{user_id}/follow", response_model=FollowResponseDTO, status_code=status.HTTP_201_CREATED)
def follow_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    follow_repo: FollowRepositoryPort = Depends(get_follow_repo)
):
    use_case = ManageFollowsUseCase(user_repo, follow_repo)
    try:
        return use_case.follow(current_user["user_id"], user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    follow_repo: FollowRepositoryPort = Depends(get_follow_repo)
):
    use_case = ManageFollowsUseCase(user_repo, follow_repo)
    try:
        if not use_case.unfollow(current_user["user_id"], user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow relationship not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{user_id}/follow_status", response_model=FollowStatusDTO)
def get_user_follow_status(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    user_repo: UserRepositoryPort = Depends(get_user_repo),
    follow_repo: FollowRepositoryPort = Depends(get_follow_repo)
):
    use_case = ManageFollowsUseCase(user_repo, follow_repo)
    return use_case.get_follow_status(current_user["user_id"], user_id)


# --- Block / unblock (Apple Guideline 1.2 — UGC apps must let users block) ---


@router.post("/{user_id}/block", status_code=status.HTTP_201_CREATED)
def block_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    use_case: BlockUserUseCase = Depends(get_block_user_use_case),
):
    try:
        use_case.execute(blocker_id=current_user["user_id"], blocked_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "blocked": user_id}


@router.delete("/{user_id}/block", status_code=status.HTTP_204_NO_CONTENT)
def unblock_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    use_case: UnblockUserUseCase = Depends(get_unblock_user_use_case),
):
    use_case.execute(blocker_id=current_user["user_id"], blocked_id=user_id)
    return None


@router.get("/blocks/list")
def list_blocked_users(
    current_user: Annotated[dict, Depends(get_current_user)],
    repo: UserBlockRepositoryPort = Depends(get_user_block_repo),
):
    return {"blocked_user_ids": repo.list_blocked_ids(current_user["user_id"])}
