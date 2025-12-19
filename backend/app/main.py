from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, init_db
from app.models import Post
from app.schemas import PostCreate
from app.crud import create_post

app = FastAPI(title="AutoPost System")

@app.on_event("startup")
async def startup():
    await init_db()
    print("✅ Database initialized successfully")

@app.post("/posts")
async def add_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    new_post = await create_post(db, post)
    return {"message": "Post added", "post": new_post}
