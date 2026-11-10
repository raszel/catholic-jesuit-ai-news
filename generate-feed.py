import feedparser
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
from email.utils import parsedate_to_datetime
import re

# defining the RSS sources that will require filtering:
RSS_SOURCES = [
    {
        "name": "United States Catholic Conference of Bishops News",
        "url": "https://www.usccb.org/news.rss",
        "homepage_link": "https://www.usccb.org/news"
    },
    {
        "name": "Jesuit Higher Education: A Journal",
        "url": "https://digitalcommons.lmu.edu/jhe/recent.rss",
        "homepage_link": "https://digitalcommons.lmu.edu/jhe/"
    },
    {
        "name": "https://epublications.marquette.edu/conversations/recent.rss",
        "url": "https://www.jesuits.global/news/feed/",
        "homepage_link": "https://www.jesuits.global/news/"
    }
]

# defining the web sources that already have relevant imposed filters/tags on them and don't require additional filtering for relevance
WEB_FILTERED_SOURCES = [
        {
            "name": "Vatican News AI",
            "url": "https://www.vaticannews.va/en/taglist.cultura-e-societa.Cultura.scienza.intelligenza-artificiale.html",
            "homepage_link": "https://www.vaticannews.va/en"
        },
        {
            "name": "Vatican News Magnifica Humanitas",
            "url": "https://www.vaticannews.va/en/taglist.chiesa-e-religioni.Magistero-pontificio.Magnifica-humanitas.html",
            "homepage_link": "https://www.vaticannews.va/en"
        }
]

# defining general web sources that will require additional filtering for relevance
WEB_UNFILTERED_SOURCES = [
        {
            "name": "Initiative on Catholic Social Thought and Public Life Newsroom",
            "url": "https://catholicsocialthought.georgetown.edu/newsroom",
            "homepage_link": "https://catholicsocialthought.georgetown.edu/newsroom"
        },
        {    
            "name": "Association of Jesuit Colleges and Universities Higher Ed News",
            "url": "https://ajcunet.edu/online-publications/ajcu-higher-ed-news/",
            "homepage_link": "https://ajcunet.edu/online-publications/ajcu-higher-ed-news/"
        },
        {
            "name": "Creighton University News",
            "url": "https://www.creighton.edu/news/",
            "homepage_link": "https://www.creighton.edu/news/"
        },
        {
            "name": "Creighton University Media Coverage",
            "url": "https://www.creighton.edu/about/news-and-events/media-coverage",
            "homepage_link": "https://www.creighton.edu/about/news-and-events/media-coverage"
        }
]

# setting the keywords to search for within the articles
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

# defining how the scoring is calculated based on usage of certain words
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

    if "basketball" in text:
        score -= 20

    if "ncaa" in text:
        score -= 20
    
    if "football" in text:
        score -= 20
    
    if "baseball" in text:
        score -= 20
    
    if "athletics" in text:
        score -= 20
    
    if "volleyball" in text:
        score -= 20
    # only returns "ai" as a standalone word, not in the middle of words like campaign, etc
    # if re.search(r"\bai\b", text):
        # score += 1

    return score

# retrieving images, if there are any, from the articles
def get_image(url):
    
    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        image = soup.find(
            "meta",
            property="og:image"
        )


        if image:
            return image["content"] 

    
    except Exception:
        pass

    return ""


def get_description(url):

     try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        tag = soup.find(
            "meta",
            property="og:description"
        )

        if tag:
            return tag.get("content", "")
     
     except Exception:
         pass
         
     return ""

def format_date(date_string):

    if not date_string:
        return ""

    try:

        if "T" in date_string:
            dt = datetime.fromisoformat(
                date_string
            )

        else:
            dt = parsedate_to_datetime(
                date_string
            )

        formatted = dt.strftime(
            "%B %d, %Y %I:%M %p %Z"
        )

        return formatted.replace(
            " 0",
            " "
        )
        
    except Exception:
        return date_string

def get_publish_date(url):

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        tag = soup.find(
            "meta",
            property="article:published_time"
        )

        if tag:
            return tag.get(
                "content",
                ""
            )

    except Exception:
        pass

    return ""

# defining the parameters for scraping the web sources including to ignore irrelevant links in the webpages
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
            response.content,
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

            image_url = get_image(
                full_url
            )

            print(f"IMAGE URL: {image_url}")
            
            summary = get_description(
                full_url
            )

            publish_date = get_publish_date(
                full_url
            )

            summary = (
                summary
                .replace("â", '"')
                .replace("â", '"')
                .replace("â", "'")
            )

            # articles from the already filtered web sources get an automatic score of 50
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
                    "summary": summary,
                    "published": publish_date,
                    "image": image_url
                },
                "source": source["name"],
                "homepage_link": source["homepage_link"],
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

# building the feed
fg = FeedGenerator()

fg.title("Catholic & Jesuit AI News")
fg.link(href="https://github.com")
fg.description(
    "AI and Magnifica Humanitas related news for Creighton University's Institute of Adaptive Intelligence"
)

articles = []

# naming the metadata contents from RSS-sourced articles
for source in RSS_SOURCES:

    feed = feedparser.parse(
        source["url"]
    )

    for entry in feed.entries:

        text = (
            entry.get("title", "")
            + " "
            + entry.get("summary", "")
        ).lower()

        score = calculate_score(text)

        if score >= 5:

            print(
                f"MATCH:: {entry.get('title','')}"
            )
            articles.append({
                "entry": entry,
                "homepage_link": source["homepage_link"],
                "source": source["name"],
                "score": score
            })
    
# scraping and naming the metadata from the filtered web sources, giving the auto-score of 50 due to being from an already-curated list
for source in WEB_FILTERED_SOURCES:
    scrape_web_source(source, curated=True)

# scraping and naming the metadata from the unfiltered web sources, including computing the scores of the articles for relevance
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

# setting a limit of no more than 5 articles each from the curated web pages so Vatican News doesn't obliterate the feed
SOURCE_LIMITS = {
    "Vatican News AI": 5,
    "Vatican News Magnifica Humanitas": 5
}

source_counts = {}
filtered_articles = []

# more per-source limits so one source doesn't dominate the feed
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

# selecting which articles to place in the feed
for article_data in filtered_articles[:50]:

    article = article_data["entry"]
    print(type(article))
    source_name = article_data["source"]
    homepage_link = article_data["homepage_link"]

    article_title = (
        article.get("title")
        if isinstance(article, dict)
        else article.title
    )

    article_link = (
        article.get("link")
        if isinstance(article, dict)
        else article.link
    )
    
    article_summary = (
        article.get("summary", "")
        if isinstance(article, dict)
        else article.get("summary", "")
    )

    print(f"WRITING: {article_title}")
    
    fe = fg.add_entry()

    article_title = (
        article.get("title")
        if isinstance(article, dict)
        else article.title
    )

    #have the entry display the source in brackets and then the article title
    fe.title(
        f"[{source_name}] {article_title}"
    )

    article_link = (
        article.get("link")
        if isinstance(article, dict)
        else article.link
    )

    fe.link(href=article_link)


       

    pub_date = article.get(
        "published",
        article.get("updated", "Unknown date")
    )
    
    pub_date = format_date(
        pub_date
    )

#looking for images in the articles
    if "media_content" in article:
        
        image_url = article.media_content[0]["url"]
    
        fe.enclosure(
            image_url,
            0,
            "image/jpeg"
        )
        
    image_html = ""


    if isinstance(article, dict):
    
        image_url = article.get("image")
    
        if image_url:
    
            image_html = (
                f'<img src="{image_url}" '
                'style="width:75px !important;'
                'max-width:75px !important;'
                'height:auto !important;'
                'float:right;'
                'margin-left:10px;'
                'margin-bottom:5px;'
                'border-radius:4px;">'
            )

# DESCRIPTION BLOCK    
    # metadata is indented and slightly smaller
    description = (
    "<div style='margin-left:30px;font-size:16px;'>"
    )


# getting the images, if there are any to get:
    if image_html:
        description += image_html
    
    if (
        hasattr(article, "media_content")
        and article.media_content
    ):
        image_url = article.media_content[0]["url"]
        
        # setting the size and display css of the retrieved image
        image_html = (
            f'<img src="{image_url}" '
            'style="width:75px !important;'
            'max-width:75px !important;'
            'height:auto !important;'
            'float:right;'
            'margin-left:10px;'
            'margin-bottom:5px;'
            'border-radius:4px;">'
        )
    
        description += image_html
    
    description += (
        f"<div><strong>Title:</strong> "
        f"{article_title}</div>"
    )

    description += (
    f"<div><strong>Source:</strong> "
    f'<a href="{homepage_link}"><em>{source_name}</em></a>'
    "</div>"
    )
    
 # f'<a href="{article_link}"><em>Read full article</em></a>'

    # formatting the display of the article's metadata  
    if pub_date:
        description += (
            f"<div><strong>Published:</strong> "
            f"{pub_date}</div>"
        )

    # retrieving the summary or beginning of the article, then displaying it
    if "summary" in article:

        summary = (
            article.get("summary", "")
            if isinstance(article, dict)
            else article.summary
        )

        # if the text is longer than 200 characters, cut it off at 200, then add an ellipses and a link to read the rest of the article text
        if len(summary) > 200:
            summary = (
                summary[:200]
                .rsplit(" ", 1)[0]
                + "..."
            )

        description += (
            f"<div style='margin-top:8px;'>"
            f"{summary}"
            "</div>"
        )

    description += (
        f"<div style='margin-top:8px;margin-bottom:8px;font-size:12px;'>"
        f'<a href="{article_link}"><em>Read full article</em></a>'
        "</div>"
    )

    # end of description block
    description += "</div>"
    

# telling the FeedGenerator to write the description block for each entry
    fe.description(description)
    
    print(f"WRITING: {article_title}")   

    print(f"SUCCESS: {article_title}")

# looking for a posted, published, or updated date to use as the date 
#    date_struct = (
#        article.get("published_parsed")
#        or article.get("updated_parsed")
#    )
    
#    if date_struct:
#        try:
#            fe.pubDate(
#                datetime(*date_struct[:6])
#            )
#        except Exception:
#            pass

# write and post the RSS XML doc
rss_path = "docs/rss.xml"

# internal success message
print(f"Found {len(articles)} matching articles")

# structures the output RSS in a nice way
fg.rss_file(rss_path, pretty=True)

# internal success message
print(f"Wrote {rss_path}")

print("RSS feed generated.")
