# tasks.py
import httpx
from readability import Document
from bs4 import BeautifulSoup
from googlesearch import search
import asyncio

async def fetch_single_article_async(url: str, client: httpx.AsyncClient):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = await client.get(url, headers=headers, follow_redirects=True, timeout=30.0) # Timeout here is per-request
        response.raise_for_status()
        doc = Document(response.text)
        article_title = doc.title()
        html_content = doc.summary()
        soup = BeautifulSoup(html_content, "html.parser")
        article_text = soup.get_text(separator="\n", strip=True)
        if not article_text or len(article_text) < 100:
            raise ValueError("Content too short.")
        return {"status": "success", "url": url, "title": article_title, "text": article_text}
    except Exception as e:
        return {"status": "failed", "url": url, "error_message": str(e)}

def search_and_fetch_articles_task(query: str, count: int):
    """
    This is the main function that the RQ worker will execute.
    It's synchronous itself, but it runs an async loop inside.
    """
    urls = []
    try:
        for url in search(query, num_results=count + 10, lang='ar'):
            if not url.startswith('http') or any(d in url for d in ['youtube.com', 'google.com', 'facebook.com']):
                continue
            urls.append(url)
            if len(urls) >= count:
                break
    except Exception as e:
        return {"error": f"Google search failed: {str(e)}"}
    
    if not urls:
        return {"query": query, "articles_count": 0, "articles": []}

    async def main():
        async with httpx.AsyncClient() as client:
            tasks = [fetch_single_article_async(url, client) for url in urls]
            return await asyncio.gather(*tasks)

    results = asyncio.run(main())
    
    successful_articles = [res for res in results if res.get("status") == "success"]
    return {"query": query, "articles_count": len(successful_articles), "articles": successful_articles}