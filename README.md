# eBay E-Commerce Scraper###

This project is a Python-based scraper designed to collect product data from eBay. It focuses on three key details:
1. Product name
2. Price
3. Item specifics (unique details like condition, color, or size)

The scraper combines four popular Python libraries to make the process flexible and easy to use:
#### Selenium → to handle pages with heavy JavaScript.
#### BeautifulSoup4 → to parse the rendered HTML.
#### FastAPI → to provide a modern API for triggering the scraper.
#### Typer → to build a clean command-line interface (CLI).
This way, you can run the scraper directly from your terminal or integrate it as an API service.

## Features

1. Scrapes product listings from eBay and extracts product names, prices, and item specifics.
2. Dual access: run it as a CLI for quick use, or as an API for integration with other applications.
3. Scalable design: easy to expand with more product details or even adapt it to other marketplaces.
4. Practical setup: supports headless browsing, custom delays, and error handling to make scraping more reliable.

## Project Structure

The project is organized into separate modules for clarity:
- scraper/ → core scraping logic and helpers.
- api/ → FastAPI service with endpoints.
- cli/ → Typer-based command-line interface.
- tests/ → unit tests for scraper and API.
This separation makes it easier to maintain and extend.

## Installation

1. Clone the repository and create a virtual environment.
2. Install dependencies from requirements.txt (includes Selenium, BeautifulSoup4, FastAPI, Typer, and Pydantic).
3. Make sure you have a browser driver installed, such as ChromeDriver.

## How to Use

There are two main ways to run the scraper:
1. Command Line
- Launch the scraper from your terminal and provide the eBay search URL.
- The output is returned in JSON format.
2. API Service
- Start the FastAPI server with Uvicorn.
- Send a request to the /scrape endpoint with the target URL.
- Receive the scraped results as structured JSON.
Both methods return the same type of data product name, price, and item specifics.

## Why These Tools?

Selenium: eBay pages rely heavily on JavaScript, so a headless browser is the most reliable way to render content.

BeautifulSoup4: makes it much easier to navigate the rendered HTML and extract specific details.

FastAPI: a modern, fast, and well-documented framework for exposing the scraper as an API.

Typer: helps build a simple, intuitive CLI that feels natural to use.

## Testing

Basic tests are included to ensure the scraper works consistently. These cover both the scraping logic and the API endpoints. For reliability, some tests mock browser interactions to reduce runtime.

## Notes

1. Use this project responsibly. Over-scraping may violate eBay’s terms of service.
2. For production use, you should consider:
- Rotating proxies
- Varying user agents
- Adding random delays between requests
These steps reduce the risk of being blocked.

## Roadmap

| Add support for scraping multiple pages automatically.
| Extract additional details like ratings, shipping cost, or availability.
| Export results to CSV/Excel.
| Connect with a database for persistent storage.

## License

This project is released under the MIT License. You are free to use, modify, and share it as long as proper credit is given.