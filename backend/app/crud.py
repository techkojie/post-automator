from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Post
from app.schemas import PostCreate

async def create_post(db: AsyncSession, post: PostCreate):
    db_post = Post(
        title=post.title,
        content=post.content,
        platform=post.platform,
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post
