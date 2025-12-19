import os
from dotenv import load_dotenv
from collections import Counter
from database import get_session, Post
from textblob import TextBlob

load_dotenv()

def extract_keywords(text):
    """
    Extracts the most common keywords from the given text.
    """
    blob = TextBlob(text)
    return [word.lower() for word, pos in blob.tags if pos.startswith('NN','NNS','JJ')][:5]

def generate_niche_keywords(posts):
    """analyze posts and return top keywords per platform"""
    platform_keywords = {}
    for platform in set(post.platform for post in posts):
        platform_posts = [post for post in posts if post.platform == platform]
        all_keywords = []
        for post in platform_posts:
            keywords = extract_keywords(post.content)
            all_keywords.extend(keywords)
        most_common = Counter(all_keywords).most_common(5)
        platform_keywords[platform] = [keyword for keyword, count in most_common]
    return platform_keywords

def update_env_file(new_niches):
    """Rewrite the .env file with updated niche values."""
    env_path = ".env"
    lines = []
    
    with open(env_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("WORDPRESS_NICHE"):
            new_lines.append(f"WORDPRESS_NICHE={','.join(new_niches.get('wordpress', []))}\n")
        elif line.startswith("TWITTER_NICHE"):
            new_lines.append(f"TWITTER_NICHE={','.join(new_niches.get('twitter', []))}\n")
        elif line.startswith("TRUTHSOCIAL_NICHE"):
            new_lines.append(f"TRUTHSOCIAL_NICHE={','.join(new_niches.get('truthsocial', []))}\n")
        else:
            new_lines.append(line)

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    print("✅ Niche preferences updated successfully!")

def auto_update_niches():
    """Main function — reads posts, extracts new niches, updates .env."""
    session = get_session()
    posts = session.query(Post).all()
    if not posts:
        print("⚠️ No posts found in database.")
        return
    
    niches = generate_niche_keywords(posts)
    update_env_file(niches)
    print(f"🔁 Updated niches: {niches}")

if __name__ == "__main__":
    auto_update_niches()