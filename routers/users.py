from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from deps import templates, SessionDep, CurrentUserDep
from sqlalchemy import select
from models import User, Post, Follow

router = APIRouter()

@router.get('/users/{username}')
def user_profile(
  request: Request,
  username: str,
  db: SessionDep,
  user: CurrentUserDep
):
  # 보려고 하는 프로필 유저
  owner = db.scalar( select(User).where(User.username == username) )
  
  if owner is None:
    raise HTTPException(status_code=404, detail='해당 사용자가 없습니다.')

  # 프로필 유저가 작성한 모든 게시물
  posts = db.scalars(select(Post).where(Post.user_id == owner.id).order_by(Post.created_at.desc())).all()

  # 해당프로필에 팔로우가 몇명인지
  follower_list = db.scalars(select(Follow).where(Follow.follower_id == owner.id)).all()
  # 해당프로필에 팔로잉이 몇명인지
  following_list = db.scalars(select(Follow).where(Follow.following_id == owner.id)).all()


  return templates.TemplateResponse(
    request=request,
    name='profile.html',
    context={
      'owner': owner,
      'posts': posts,
      'user': user,
      'follower_list': follower_list,
      'following_list': following_list
    }
  )


@router.post('/users/{username}/follows')
def user_follow(
  username: str,
  db: SessionDep,
  user: CurrentUserDep
):
  # 비로그인 유저 로그인페이지로
  if user is None:
    return RedirectResponse('/login', status_code=303)

  owner = db.scalar(  select(User).where(User.username == username)  )

  # 팔로우 했는지 조회
  follow = db.get(Follow, (user.id, owner.id) )

  if follow:
    # 팔로우 했다면 
    db.delete(follow)
  else:
    # 팔로우 안했으면
    follow = Follow(follower_id=user.id, following_id=owner.id )
    db.add(follow)

  db.commit()

  return RedirectResponse(f'/users/{username}', status_code=303)