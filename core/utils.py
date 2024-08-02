from newsapi import NewsApiClient
from django.conf import settings
from django.core.cache import cache
from requests.exceptions import RequestException
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)


def log_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper


def format_currency(amount):
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount:,.2f}"


def get_relevant_news(num_articles=5):
    cache_key = "retail_news_articles"
    cached_articles = cache.get(cache_key)
    if cached_articles:
        logger.info("Returning cached retail news articles")
        return cached_articles

    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
    try:
        logger.info("Fetching retail news from API")

        # Set date range for past month
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        logger.info(f"Date range: from {from_date} to {to_date}")

        # First, try to get articles from Retail Dive
        try:
            articles = newsapi.get_everything(
                domains="retaildive.com",
                from_param=from_date,
                to=to_date,
                language="en",
                sort_by="relevancy",
                page_size=num_articles,
            )
            logger.info(
                f"Successfully fetched {len(articles.get('articles', []))} articles from Retail Dive"
            )
        except Exception as e:
            logger.error(f"Error fetching articles from Retail Dive: {str(e)}")
            articles = {"articles": []}

        # If not enough articles from Retail Dive, expand search to other retail sources
        if len(articles.get("articles", [])) < num_articles:
            logger.info("Not enough articles from Retail Dive, expanding search")
            try:
                additional_articles = newsapi.get_everything(
                    q="retail OR ecommerce",
                    from_param=from_date,
                    to=to_date,
                    language="en",
                    sort_by="relevancy",
                    page_size=num_articles - len(articles.get("articles", [])),
                )
                articles["articles"].extend(additional_articles.get("articles", []))
                logger.info(
                    f"Successfully fetched {len(additional_articles.get('articles', []))} additional articles"
                )
            except Exception as e:
                logger.error(f"Error fetching additional articles: {str(e)}")

        logger.info(f"Total fetched articles: {len(articles.get('articles', []))}")

        if "articles" not in articles or not articles["articles"]:
            logger.error(f"No articles found in API response")
            return []

        cleaned_articles = []
        for article in articles["articles"][:num_articles]:
            cleaned_article = {
                "title": article.get("title", "No title available"),
                "url": article.get("url", "#"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "published_at": article.get("publishedAt", "No date available"),
            }
            cleaned_articles.append(cleaned_article)
            logger.info(f"Processed article: {cleaned_article}")

        cache.set(cache_key, cleaned_articles, 3600)  # Cache for 1 hour
        return cleaned_articles
    except RequestException as e:
        logger.error(f"Network error fetching news: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return []
