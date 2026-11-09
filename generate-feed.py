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
    "artificial intelligence",
    "intelligenza artificiale",
    "magnifica humanitas",
    "generative ai",
    "responsible ai",
    "ai governance",
    "machine learning",
    "large language model",
    "llm",
    "chatgpt",
    "ai ethics"

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

            print(
                f"MATCH:: {entry.get('title','')}"
            )
            articles.append({
                "entry": entry,
                "source": feed.feed.get("title", source)
            })
    
    
    for entry in feed.entries:


        articles.sort(
            key=lambda x: x["entry"].get("published_parsed", ()),
            reverse=True
        )

for article_data in articles[:50]:

    article = article_data["entry"]
    source_name = article_data["source"]

    fe = fg.add_entry()

    fe.title(
        f"[{source_name}] {article.title}"
    )

    fe.link(href=article.link)
    
    if "media_content" in article:
        
        image_url = article.media_content[0]["url"]
    
        fe.enclosure(
            image_url,
            0,
            "image/jpeg"
        ) 

    pub_date = article.get(
        "published",
        article.get("updated", "Unknown date")
    )

    description = "<div style='margin-left:25px;'>"

    if pub_date:
        description += (
            f"<div><strong>Published:</strong> "
            f"{pub_date}</div>"
        )

    description += (
        f"<div><strong>Source:</strong> "
        f"{source_name}</div>"
    )

    if "summary" in article:

        summary = article.summary

        if len(summary) > 300:
            summary = (
                summary[:300]
                .rsplit(" ", 1)[0]
                + "..."
            )

        description += (
            f"<div style='margin-top:8px;'>"
            f"{summary}"
            "</div>"
        )

    description += (
        f"<div style='margin-top:8px;'>"
        f'<a href="{article.link}">'
        "Read full article</a>"
        "</div>"
    )


    description += "</div>"

    fe.description(description)

    date_struct = (
        article.get("published_parsed")
        or article.get("updated_parsed")
    )
    
    if date_struct:
        try:
            fe.pubDate(
                datetime(*date_struct[:6])
            )
        except Exception:
            pass

rss_path = "docs/rss.xml"

print(f"Found {len(articles)} matching articles")

fg.rss_file(rss_path, pretty=True)

print(f"Wrote {rss_path}")


print("RSS feed generated.")
