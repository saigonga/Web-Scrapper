 
# Web Scrapper

## 🚀 Overview

Web Scrapper is a modern, Python-powered web scraping platform built with FastAPI, Playwright, and BeautifulSoup. It demonstrates advanced Python engineering, asynchronous programming, and robust API design. This project is a showcase of my coding skills and a foundation for future data-driven applications.

## Live Project
Check Out : https://web-scrapper-kohl.vercel.app/

## ✨ Why Use This Project?

- **Versatile Scraping:** handles both static and JavaScript-heavy sites using hybrid scraping (httpx + Playwright).
- **Structured Extraction:** Breaks down web pages into semantic sections, capturing headings, text, links, images, lists, and tables.
- **Meta Intelligence:** Extracts page metadata (title, description, language, canonical URL) for SEO and analytics.
- **Automated Interactions:** Simulates user actions (clicks, scrolls, pagination) for deep content extraction.
- **Extensible Models:** Uses Pydantic for type-safe, extensible data models—ideal for ML, analytics, or further automation.
- **API & UI:** Offers both a REST API and a sleek web interface for instant results and easy integration.
- **Testing Suite:** Includes automated endpoint tests to ensure reliability and correctness.

## 🧑‍💻 Python Skills Demonstrated

- **Async Programming:** Efficient use of async/await for high-performance scraping and API handling.
- **OOP & Design Patterns:** Modular scraper classes, inheritance, and clean separation of concerns.
- **Error Handling:** Graceful fallback between static and dynamic scraping, robust exception management.
- **Data Modeling:** Advanced use of Pydantic for request/response validation and serialization.
- **API Engineering:** FastAPI endpoints, response models, and template rendering.
- **Automation:** Shell scripting for environment setup and browser installation.
- **Testing:** Automated verification of endpoints and scraping logic.

## 🔮 Future Use Cases

- **AI-Powered Data Mining:** Feed structured web data into machine learning models for NLP, recommendation, or sentiment analysis.
- **Business Intelligence:** Aggregate competitor data, pricing, reviews, and trends from multiple sources.
- **SEO & Content Analysis:** Analyze page structure, metadata, and content for optimization and reporting.
- **Automated Monitoring:** Track changes on news, e-commerce, or social media sites for alerts and dashboards.
- **Custom Integrations:** Plug into data pipelines, ETL workflows, or cloud functions for scalable automation.

## 🛠️ Setup & Run

```bash
chmod +x run.sh
./run.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies from `requirements.txt`
- Install Playwright browsers
- Start the FastAPI server at [http://localhost:8000](http://localhost:8000)

## 🌐 Usage

- **Web UI:** Open [http://localhost:8000](http://localhost:8000) and enter a URL to scrape.
- **API:** POST to `/scrape` with JSON:
	```json
	{ "url": "https://example.com" }
	```
- **Health Check:** GET `/healthz` returns `{ "status": "ok" }`

## 📝 Example URLs

- Static: https://en.wikipedia.org/wiki/Artificial_intelligence
- JS Heavy: https://vercel.com/
- Pagination: https://news.ycombinator.com/

## ✅ Testing

Run `verify.py` to test endpoints and scraping logic:
```bash
python verify.py
```

## 📁 File Structure

- `main.py` — FastAPI app and endpoints
- `scraper.py` — Static and dynamic scraping logic
- `models.py` — Pydantic models for requests and responses
- `verify.py` — Endpoint and feature tests
- `templates/index.html` — Web UI
- `requirements.txt` — Python dependencies
- `run.sh` — Setup and launch script

## ⚠️ Limitations & Roadmap

- Currently, only static scraping is fully supported. JavaScript rendering is in progress.
- Some sites may block scraping or require additional headers/cookies.
- Planned features: advanced anti-bot bypass, cloud deployment, and real-time dashboards.

## 📜 License

MIT License
