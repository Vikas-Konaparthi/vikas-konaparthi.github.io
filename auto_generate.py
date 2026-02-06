import os
import requests
import datetime
import random
import feedparser
from pytrends.request import TrendReq
import google.generativeai as genai

# ------------------------
# Configure Gemini
# ------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

today = datetime.date.today()
filename = f"_posts/{today}-ai-trend.md"

# ------------------------
# 1. Hacker News
# ------------------------
hn_ids = requests.get(
    "https://hacker-news.firebaseio.com/v0/topstories.json"
).json()[:10]

hn_titles = []
for id in hn_ids[:5]:
    item = requests.get(
        f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
    ).json()
    if item and "title" in item:
        hn_titles.append(item["title"])

# ------------------------
# 2. Google Trends
# ------------------------
pytrends = TrendReq()
trending = pytrends.trending_searches()
trend_titles = trending[0].tolist()[:5]

# ------------------------
# 3. arXiv AI
# ------------------------
feed = feedparser.parse("http://export.arxiv.org/rss/cs.AI")
arxiv_titles = [entry.title for entry in feed.entries[:5]]

# ------------------------
# Combine Topics
# ------------------------
all_topics = hn_titles + trend_titles + arxiv_titles
topic = random.choice(all_topics)

# ------------------------
# Generate Post
# ------------------------
prompt = f"""
You are writing for a technical platform called Hilaight.

Write a creative, engaging, trending, new and educational with examples blog post about:

"{topic}"

Requirements:
- Structured with headings
- Clear explanations
- Real-world context
- 800–1200 words
- Confident and analytical tone
- End with a thought-provoking question
"""

response = model.generate_content(prompt)
content = response.text

markdown = f"""---
title: "{topic}"
date: {today}
categories: [ai, system-design, tech-news]
tags: [automation, trends]
---

{content}
"""

with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown)

print("Generated:", filename)
