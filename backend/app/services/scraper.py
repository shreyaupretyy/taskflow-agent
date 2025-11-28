import asyncio
import random
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class WebScraper:
    """Advanced web scraper with anti-bot strategies."""

    def __init__(self):
        self.ua = UserAgent()
        self.session = None

    def _get_headers(self) -> Dict[str, str]:
        """Generate realistic headers with rotating user agents."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    async def scrape_url(self, url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape content from a URL with anti-bot strategies."""
        config = config or {}

        # Random delay to avoid detection
        delay = config.get("delay", random.uniform(1, 3))
        await asyncio.sleep(delay)

        try:
            async with httpx.AsyncClient(
                headers=self._get_headers(), timeout=30.0, follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                return await self._parse_content(response.text, config)

        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    async def _parse_content(self, html: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HTML content based on configuration."""
        soup = BeautifulSoup(html, "html.parser")

        result = {"success": True, "data": {}}

        # Extract based on selectors
        selectors = config.get("selectors", {})
        for key, selector in selectors.items():
            if isinstance(selector, dict):
                css_selector = selector.get("selector")
                attribute = selector.get("attribute")
                multiple = selector.get("multiple", False)

                if multiple:
                    elements = soup.select(css_selector)
                    if attribute:
                        result["data"][key] = [el.get(attribute) for el in elements]
                    else:
                        result["data"][key] = [el.get_text(strip=True) for el in elements]
                else:
                    element = soup.select_one(css_selector)
                    if element:
                        if attribute:
                            result["data"][key] = element.get(attribute)
                        else:
                            result["data"][key] = element.get_text(strip=True)
            else:
                # Simple CSS selector
                element = soup.select_one(selector)
                if element:
                    result["data"][key] = element.get_text(strip=True)

        # If no selectors provided, extract common elements
        if not selectors:
            result["data"] = {
                "title": soup.title.string if soup.title else "",
                "headings": [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])],
                "paragraphs": [p.get_text(strip=True) for p in soup.find_all("p")],
                "links": [a.get("href") for a in soup.find_all("a", href=True)],
            }

        return result

    async def scrape_multiple(
        self, urls: List[str], config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently with rate limiting."""
        config = config or {}
        max_concurrent = config.get("max_concurrent", 5)

        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_limit(url):
            async with semaphore:
                return await self.scrape_url(url, config)

        tasks = [scrape_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks)

        return results

    async def monitor_changes(self, url: str, selector: str, interval: int = 300) -> Dict[str, Any]:
        """Monitor a webpage for changes."""
        previous_content = None

        result = await self.scrape_url(url, {"selectors": {"monitored": selector}})

        if result.get("success"):
            current_content = result["data"].get("monitored")

            if previous_content and current_content != previous_content:
                return {
                    "changed": True,
                    "previous": previous_content,
                    "current": current_content,
                    "url": url,
                }

            return {"changed": False, "content": current_content, "url": url}

        return result
