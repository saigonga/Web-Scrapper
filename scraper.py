import httpx
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timezone
from urllib.parse import urljoin
from typing import List, Optional
import asyncio

# Playwright
from playwright.async_api import async_playwright, Page

from models import ScrapeResult, MetaInfo, Section, SectionContent, Interactions, ErrorLog

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class BaseScraper:
    def __init__(self, url: str):
        self.url = url
        self.errors = []
        self.visited_pages = set()
        self.clicks_attempted = []
        self.scroll_count = 0

    def _extract_meta(self, soup: BeautifulSoup, url: str) -> MetaInfo:
        title = soup.title.string if soup.title else ""
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "")

        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")
        
        language = "en"
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            language = html_tag.get("lang")
            
        canonical = None
        link_canon = soup.find("link", rel="canonical")
        if link_canon:
            canonical = link_canon.get("href")
            
        return MetaInfo(
            title=str(title).strip(),
            description=str(description).strip(),
            language=str(language).strip(),
            canonical=canonical
        )

    def _extract_sections(self, soup: BeautifulSoup, base_url: str) -> List[Section]:
        sections = []
        body = soup.body
        if not body:
            return []

        # Limit candidates to prevent processing huge DOMs - top 100 semantic elements
        candidates = body.find_all(['header', 'nav', 'main', 'section', 'footer', 'article'], limit=100)
        if not candidates:
            candidates = [body]
        
        processed_nodes = set()
        
        for i, node in enumerate(candidates):
            if node in processed_nodes:
                continue
                
            sec_type = "section"
            if node.name == 'nav': sec_type = 'nav'
            elif node.name == 'footer': sec_type = 'footer'
            elif node.name == 'header': sec_type = 'hero'
            
            content = self._extract_content(node, base_url)
            
            # Simple content filter
            if not content.text and not content.images and not content.links:
                continue

            label = "Section"
            if content.headings:
                label = content.headings[0]
            else:
                words = content.text.split()
                if words:
                    label = " ".join(words[:7]) + "..."
            
            raw_html = str(node)
            truncated = False
            if len(raw_html) > 1000:
                raw_html = raw_html[:1000] + "..."
                truncated = True

            sec_id = f"{sec_type}-{i}"

            sections.append(Section(
                id=sec_id,
                type=sec_type,
                label=label,
                sourceUrl=base_url,
                content=content,
                rawHtml=raw_html,
                truncated=truncated
            ))
            processed_nodes.add(node)
            
        return sections

    def _extract_content(self, element: Tag, base_url: str) -> SectionContent:
        # Extract text once for reuse
        text = element.get_text(separator=" ", strip=True)
        
        # Batch all heading extractions in one pass
        headings = [h.get_text(strip=True) for h in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], limit=20)]
        
        # Limit and extract links efficiently
        links = []
        for a in element.find_all('a', href=True, limit=50):
            href = urljoin(base_url, a['href'])
            links.append({"text": a.get_text(strip=True), "href": href})
            
        # Limit and extract images efficiently
        images = []
        for img in element.find_all('img', src=True, limit=20):
            src = urljoin(base_url, img['src'])
            alt = img.get('alt', '')
            images.append({"src": src, "alt": alt})
            
        # Extract lists with early termination
        lists = []
        for ul in element.find_all(['ul', 'ol'], limit=10):
            items = [li.get_text(strip=True) for li in ul.find_all('li', limit=20)]
            if items:
                lists.append(items)
                
        return SectionContent(
            headings=headings,
            text=text,
            links=links,
            images=images,
            lists=lists,
            tables=[]
        )

class StaticScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0, headers=DEFAULT_HEADERS) as client:
                response = await client.get(self.url)
                response.raise_for_status()
                html = response.text
                final_url = str(response.url)
        except Exception as e:
            self.errors.append(ErrorLog(message=str(e), phase="fetch"))
            result = ScrapeResult(
                url=self.url,
                scrapedAt=datetime.now(timezone.utc).isoformat(),
                meta=MetaInfo(),
                sections=[],
                interactions=Interactions(),
                errors=self.errors
            )
            return result

        soup = BeautifulSoup(html, 'html.parser')
        
        # Heuristic: If content is very short, maybe we need JS?
        text_len = len(soup.get_text(strip=True))
        if text_len < 500:
             # Fallback to Dynamic
             # NOTE: In a real system, we might return a specific signal to the caller.
             # For this assignment, we'll just switch to DynamicScraper here or let the caller decide.
             # I will implement self-switching logic in main or here.
             # For now, let's keep it simple: Static is Static. The main.py will handle fallback? 
             # Or better: StaticScraper can delegate?
             pass

        meta = self._extract_meta(soup, final_url)
        sections = self._extract_sections(soup, final_url)
        
        return ScrapeResult(
            url=self.url,
            scrapedAt=datetime.now(timezone.utc).isoformat(),
            meta=meta,
            sections=sections,
            interactions=Interactions(pages=[final_url]),
            errors=self.errors
        )

class DynamicScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=DEFAULT_HEADERS["User-Agent"], ignore_https_errors=True)
            page = await context.new_page()
            
            try:
                # 1. Navigate
                await page.goto(self.url, timeout=30000, wait_until="networkidle")
                self.visited_pages.add(page.url)
                
                # 2. Interactions (Click tabs / Load More)
                await self._perform_clicks(page)
                
                # 3. Pagination / Infinite Scroll
                await self._perform_scroll_or_pagination(page)
                
                # 4. Extract Content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                meta = self._extract_meta(soup, page.url)
                sections = self._extract_sections(soup, page.url)
                
                return ScrapeResult(
                    url=self.url,
                    scrapedAt=datetime.now(timezone.utc).isoformat(),
                    meta=meta,
                    sections=sections,
                    interactions=Interactions(
                        clicks=self.clicks_attempted,
                        scrolls=self.scroll_count,
                        pages=list(self.visited_pages)
                    ),
                    errors=self.errors
                )
                
            except Exception as e:
                self.errors.append(ErrorLog(message=str(e), phase="playwright_interaction"))
                # Try to return whatever we have
                return ScrapeResult(
                    url=self.url,
                    scrapedAt=datetime.now(timezone.utc).isoformat(),
                    meta=MetaInfo(),
                    sections=[],
                    interactions=Interactions(clicks=self.clicks_attempted, scrolls=self.scroll_count, pages=list(self.visited_pages)),
                    errors=self.errors
                )
            finally:
                await browser.close()

    async def _perform_clicks(self, page: Page):
        # Optimized: Use combined selector and limit iterations to reduce query overhead
        # Selectors consolidated for efficiency
        selectors = [
            'button[role="tab"], div[role="tab"]',  # Combined tab selectors
            'button:has-text("Load more"), button:has-text("Show more"), .load-more, #load-more'  # Combined load more selectors
        ]
        
        for sel in selectors:
            try:
                # Limit to first 3 visible elements to avoid excessive clicking
                elements = await page.locator(sel).all()
                for i, el in enumerate(elements):
                    if i >= 3:  # Early termination after 3 clicks per selector group
                        break
                    if await el.is_visible():
                        txt = await el.text_content()
                        await el.click(timeout=2000)
                        await page.wait_for_timeout(500) # Reduced wait time from 1000ms
                        self.clicks_attempted.append(f"{sel} (text: {txt.strip()[:20]})")
            except Exception:
                pass

    async def _perform_scroll_or_pagination(self, page: Page):
        # 1. Infinite scroll check - optimized with adaptive waiting
        for i in range(3):
            previous_height = await page.evaluate("document.body.scrollHeight")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # Adaptive wait: shorter for subsequent scrolls if no change
            wait_time = 1500 if i == 0 else 1000  # Reduced from 2000ms
            await page.wait_for_timeout(wait_time)
            new_height = await page.evaluate("document.body.scrollHeight")
            self.scroll_count += 1
            if new_height <= previous_height:
                break  # Early termination if no new content loaded
        
        # 2. Pagination check (Next button)
        # Optimized: Combined selector query instead of multiple checks
        depth = 0
        while depth < 3:
            # Use combined selector for efficiency
            next_link = page.locator('a:has-text("Next"), a[aria-label="Next"], a:has-text("More")').first
            
            if await next_link.count() and await next_link.is_visible():
                try:
                    await next_link.click()
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    self.visited_pages.add(page.url)
                    depth += 1
                except Exception:
                    break
            else:
                break
