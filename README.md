# Divar Scraper

================

A web scraping project using Flask and Selenium to extract data from [Divar.ir](https://divar.ir).

## Project Overview

---

This project uses Flask as a web framework and Selenium as a web scraping tool to extract data from Divar.ir, a popular Iranian online marketplace. The project aims to provide a scalable and efficient way to collect data from the website.

## Features

---

- Web scraping using Selenium
- Data extraction from Divar.ir
- Flask API for data retrieval

## Requirements

---

- Python 3.8+
- Flask 2.0+
- Selenium 4.0+
- ChromeDriver (for Selenium)

## Setup

---

1. Clone the repository: `git clone https://github.com/your-username/divar-scraper.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up ChromeDriver: `chromedriver --version` (make sure it's installed and up-to-date)
4. Run the Flask app: `flask run`

## API Endpoints

---

- `/scrape`: Triggers the web scraping process and returns the extracted data

## Example Use Case

---

Send a GET request to `http://localhost:5000/scrape` to trigger the web scraping process and retrieve the extracted data.

## Note

---

This project is for educational purposes only. Web scraping should be done responsibly and in accordance with the website's terms of service.
