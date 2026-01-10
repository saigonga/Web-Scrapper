from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class ScrapeRequest(BaseModel):
    url: str

class MetaInfo(BaseModel):
    title: Optional[str] = ""
    description: Optional[str] = ""
    language: Optional[str] = "en"
    canonical: Optional[str] = None

class SectionContent(BaseModel):
    headings: List[str] = []
    text: str = ""
    links: List[Dict[str, str]] = [] # {"text": "...", "href": "..."}
    images: List[Dict[str, str]] = [] # {"src": "...", "alt": "..."}
    lists: List[List[str]] = []
    tables: List[Any] = []

class Section(BaseModel):
    id: str
    type: str # hero | section | nav | footer | list | grid | faq | pricing | unknown
    label: str
    sourceUrl: str
    content: SectionContent
    rawHtml: str
    truncated: bool

class Interactions(BaseModel):
    clicks: List[str] = []
    scrolls: int = 0
    pages: List[str] = []

class ErrorLog(BaseModel):
    message: str
    phase: str

class ScrapeResult(BaseModel):
    url: str
    scrapedAt: str
    meta: MetaInfo
    sections: List[Section]
    interactions: Interactions
    errors: List[ErrorLog] = []

class ScrapeResponse(BaseModel):
    result: ScrapeResult
