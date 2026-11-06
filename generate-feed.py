import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime

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
    "AI"
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

        if any(k.lower() in text for k in KEYWORDS):

            articles.append(entry)

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

fg.rss_file(rss_path)

print("RSS feed generated.")
