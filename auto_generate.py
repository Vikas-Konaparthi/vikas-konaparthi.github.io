import os
import requests
import datetime
import random
import feedparser
from google import genai

# ------------------------
# Configure Gemini
# ------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

today = datetime.date.today()
filename = f"_posts/{today}-ai-trend.md"

# ------------------------
# Fetch Hacker News
# ------------------------
def fetch_hn():
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        ).json()[:10]

        titles = []
        for id in ids[:5]:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{id}.json",
                timeout=10
            ).json()
            if item and "title" in item:
                titles.append(item["title"])

        return titles
    except:
        return []

# ------------------------
# Fetch arXiv AI
# ------------------------
def fetch_arxiv():
    try:
        feed = feedparser.parse("http://export.arxiv.org/rss/cs.AI")
        return [entry.title for entry in feed.entries[:5]]
    except:
        return []

# ------------------------
# Combine Topics
# ------------------------
hn_titles = fetch_hn()
arxiv_titles = fetch_arxiv()

all_topics = hn_titles + arxiv_titles

if not all_topics:
    print("No topics found. Exiting safely.")
    exit(0)

topic = random.choice(all_topics)

# ------------------------
# Generate Post with Gemini
# ------------------------
prompt = f"""
You are writing for a technical platform called Hilaight.

Write a creative, engaging, educational blog post about:

"{topic}"

Requirements:
- Structured with headings
- Clear explanations
- Real-world context
- 900–1200 words
- Confident and analytical tone
- End with a thought-provoking question
"""

response = client.models.generate_content(
    model="gemini-1.5-flash-latest",
    contents=[{
        "role": "user",
        "parts": [{"text": prompt}]
    }],
)

# Safe extraction
try:
    content = response.candidates[0].content.parts[0].text
except:
    print("Gemini returned unexpected response format.")
    exit(1)

# ------------------------
# Create Markdown
# ------------------------
markdown = f"""---
title: "{topic}"
date: {today}
categories: [ai, system-design, tech-news]
tags: [hacker-news, arxiv]
---

{content}
"""

with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown)

print("Generated:", filename)
