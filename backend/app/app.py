# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, init_db
from app.models import Base, Post
from app.schemas import PostCreate, PostRead
from app.crud import create_post, get_posts
import uvicorn
import logging
import asyncio

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s"
)

app = FastAPI(title="Post Automator Backend")

# Startup event — initialize DB schema
@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        logging.error(f"Startup DB initialization failed: {e}")
        raise

@app.post("/posts/", response_model=PostRead)
async def create_new_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_post = await create_post(db, post)
        logging.info(f"✅ New post created: {post.title}")
        return new_post
    except Exception as e:
        logging.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/posts/", response_model=list[PostRead])
async def list_all_posts(db: AsyncSession = Depends(get_db)):
    try:
        posts = await get_posts(db)
        return posts
    except Exception as e:
        logging.error(f"Error fetching posts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
