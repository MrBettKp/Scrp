# Proxy Checker & Tester

A Python Flask application to check, test, and validate proxy servers. This tool helps developers working with web scraping to find reliable proxies.

## Features

- Check individual proxy servers
- Scrape proxies from free sources
- Test multiple proxies asynchronously
- Web interface for easy interaction
- Response time measurement
- Deployable on Render

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Running Locally

1. Run the Flask application: `python app.py`
2. Open your browser and navigate to `http://localhost:5000`

## Deployment on Render

1. Fork this repository to your GitHub account
2. Create a new Web Service on Render and connect your GitHub repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Deploy the application

## Usage

1. **Check Single Proxy**: Enter a proxy in IP:PORT format and a test URL to verify if the proxy is working
2. **Scrape & Test Proxies**: Scrape proxies from free sources and test them against your chosen URL

## API Endpoints

- `POST /check_proxy`: Test a single proxy
- `POST /scrape_proxies`: Scrape and test multiple proxies

## Technologies Used

- Python Flask
- Requests library
- aiohttp for asynchronous testing
- BeautifulSoup for web scraping
- HTML/CSS/JavaScript for the frontend
- Gunicorn for production server

## Note

This tool is for educational purposes. Always respect website terms of service when scraping and using proxies.
