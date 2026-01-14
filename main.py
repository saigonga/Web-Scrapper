from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from contextlib import asynccontextmanager
from scraper import StaticScraper, DynamicScraper

from models import ScrapeRequest, ScrapeResponse


app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")


# Removing duplicate ScrapeRequest definitions as it is now imported from models


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest):
    # 1. Try Scraper (Static)
    static_scraper = StaticScraper(request.url)
    result = await static_scraper.scrape()
    
    # 2. Check heuristics for fallback
    # Optimized: calculate total text length only once with generator expression
    total_text_len = sum(len(s.content.text) for s in result.sections)
    is_short = total_text_len < 2000
    
    # Check for potential interactivity cues in the static HTML (very crude)
    # We can inspect the rawHtml of sections to see if there are buttons?
    # Or just use the text length heuristic + error check for now.
    # Also, if 0 sections found, definitely fallback.
    
    has_errors = len(result.errors) > 0
    no_sections = len(result.sections) == 0
    
    should_fallback = is_short or has_errors or no_sections
    
    # Force fallback for known dynamic patterns if needed (optional)
    # e.g. "vercel.com" often hides content behind JS
    if "vercel.com" in request.url or "ycombinator.com" in request.url:
         should_fallback = True

    if should_fallback:
        print(f"Static scraping insufficient (len={total_text_len}, errs={len(result.errors)}). Falling back to Dynamic...")
        dynamic_scraper = DynamicScraper(request.url)
        dynamic_result = await dynamic_scraper.scrape()
        
        # If dynamic failed drastically (e.g. browser error) but static had something, maybe keep static?
        # But usually dynamic is better.
        # Check if dynamic has critical error and NO sections, while static HAD sections.
        if (len(dynamic_result.errors) > 0 or len(dynamic_result.sections) == 0) and len(result.sections) > 0:
             print("Dynamic scraping failed or returned no sections; reverting to Static result.")
             # Keep static result (do nothing, dynamic_result ignored)
             pass
        else:
             result = dynamic_result
        
    return ScrapeResponse(result=result)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
