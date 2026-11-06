import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime
import re

SOURCES = [
    "https://www.vaticannews.va/en.rss.xml",
    "https://www.usccb.org/news.rss",
    "https://digitalcommons.lmu.edu/jhe/recent.rss",
    "https://epublications.marquette.edu/conversations/recent.rss",
    "https://www.jesuits.global/news/feed/"
]

KEYWORDS = [
    "magnifica humanitas",
    "artificial intelligence",
    "intelligenza artificiale",
    "machine learning",
    "generative ai",
    "large language model",
    "llm",
    "digital ethics",
    "technology ethics",
    "ethics of technology",
    "algorithmic",
    "algorithms",
    "responsible ai",
    "ai governance",
    "digital humanity",
    "human dignity"
]

fg = FeedGenerator()

fg.title("Catholic & Jesuit AI News")
fg.link(href="https://github.com")
fg.description(
    "AI and Magnifica Humanitas related news for Creighton University's Institute of Adaptive Intelligence"
)

articles = []

for source in SOURCES:

    feed = feedparser.parse(source)

    for entry in feed.entries:

        text = (
            entry.get("title", "")
            + " "
            + entry.get("summary", "")
        ).lower()

        keyword_match = any(
            keyword in text
            for keyword in KEYWORDS
        )

        ai_match = re.search(r"\bai\b", text)

        if keyword_match or ai_match:

            articles.append(entry)
    for entry in feed.entries:
        

articles.sort(
    key=lambda x: x.get("published_parsed", ()),
    reverse=True
)

for article in articles[:50]:

    fe = fg.add_entry()

    fe.title(article.title)
    fe.link(href=article.link)

    if "summary" in article:
        fe.description(article.summary)

rss_path = "docs/rss.xml"

print(f"Found {len(articles)} matching articles")

fg.rss_file(rss_path)

print(f"Wrote {rss_path}")


print("RSS feed generated.")
