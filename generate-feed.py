import feedparser
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import re

RSS_SOURCES = [
    "https://www.usccb.org/news.rss",
    "https://digitalcommons.lmu.edu/jhe/recent.rss",
    "https://epublications.marquette.edu/conversations/recent.rss",
    "https://www.jesuits.global/news/feed/"
]

WEB_FILTERED_SOURCES = [
        {
            "name": "Vatican News AI",
            "url": "https://www.vaticannews.va/en/taglist.cultura-e-societa.Cultura.scienza.intelligenza-artificiale.html"
        },
        {
            "name": "Vatican News Magnifica Humanitas",
            "url": "https://www.vaticannews.va/en/taglist.chiesa-e-religioni.Magistero-pontificio.Magnifica-humanitas.html"
        }
]

WEB_UNFILTERED_SOURCES = [
        {
            "name": "Initiative on Catholic Social Thought and Public Life Newsroom",
            "url": "https://catholicsocialthought.georgetown.edu/newsroom"
        },
        {    
            "name": "Association of Jesuit Colleges and Universities Higher Ed News",
            "url": "https://ajcunet.edu/online-publications/ajcu-higher-ed-news/"
        }
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

def calculate_score(text):

    score = 0

    if "artificial intelligence" in text:
        score += 10

    if "intelligenza artificiale" in text:
        score += 10

    if "magnifica humanitas" in text:
        score += 10

    if "generative ai" in text:
        score += 8

    if "responsible ai" in text:
        score += 8

    if "ai governance" in text:
        score += 8

    if "machine learning" in text:
        score += 5

    if "large language model" in text:
        score += 5

    if "llm" in text:
        score += 3

    if "chatgpt" in text:
        score += 3

    if "ai ethics" in text:
        score += 8

    if re.search(r"\bai\b", text):
        score += 1

    if "Jesuit" in text:
        score += 3

    if "catholic" in text:
        score += 2

    if "ignatian" in text:
        score += 3

    if "human dignity" in text:
        score += 5

    return score

def scrape_web_source(source, curated=False):

    try:

        response = requests.get(
            source["url"],
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for link in soup.find_all("a", href=True):

            href = link["href"]
            
            if ".html" not in href:
                continue
                
            if "/en/" not in href:
                continue

            title = link.get_text(strip=True)

            if len(title) < 15:
                continue

            full_url = requests.compat.urljoin(
                source["url"],
                href
            )

            if curated:

                score = 50

            else:

                text = title.lower()

                score = calculate_score(text)

                if score <= 0:
                    continue

            articles.append({
                "entry": {
                    "title": title,
                    "link": full_url,
                    "summary": "",
                    "published": ""
                },
                "source": source["name"],
                "score": score
            })

            print(
                f"WEB MATCH:: {title}"
            )

    except Exception as e:

        print(
            f"WEB SOURCE ERROR: "
            f"{source['name']} - {e}"
        )


fg = FeedGenerator()

fg.title("Catholic & Jesuit AI News")
fg.link(href="https://github.com")
fg.description(
    "AI and Magnifica Humanitas related news for Creighton University's Institute of Adaptive Intelligence"
)

articles = []

for source in RSS_SOURCES:

    feed = feedparser.parse(source)

    for entry in feed.entries:

        text = (
            entry.get("title", "")
            + " "
            + entry.get("summary", "")
        ).lower()

        score = calculate_score(text)

        if score > 0:

            print(
                f"MATCH:: {entry.get('title','')}"
            )
            articles.append({
                "entry": entry,
                "source": feed.feed.get("title", source),
                "score": score
            })
    

for source in WEB_FILTERED_SOURCES:
    scrape_web_source(source, curated=True)

for source in WEB_UNFILTERED_SOURCES:
    scrape_web_source(source, curated=False)

articles.sort(
    key=lambda x: (
        x.get("score", 0),
        x["entry"].get(
            "published_parsed",
            ()
        )
    ),
    reverse=True
)

SOURCE_LIMITS = {
    "Vatican News AI": 5,
    "Vatican News Magnifica Humanitas": 5
}

source_counts = {}
filtered_articles = []

for article in articles:

    source = article["source"]

    limit = SOURCE_LIMITS.get(
        source,
        999
    )

    current_count = source_counts.get(
        source,
        0
    )

    if current_count < limit:

        filtered_articles.append(
            article
        )

        source_counts[source] = (
            current_count + 1
        )

for article_data in filtered_articles[:50]:

    article = article_data["entry"]
    source_name = article_data["source"]

    fe = fg.add_entry()

    article_title = (
        article.get("title")
        if isinstance(article, dict)
        else article.title
    )

    fe.title(
        f"[{source_name}] {article_title}"
    )

    article_link = (
        article.get("link")
        if isinstance(article, dict)
        else article.link
    )

    fe.link(href=article_link)
    
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

        summary = (
            article.get("summary", "")
            if isinstance(article, dict)
            else article.summary
        )

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
