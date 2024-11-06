import time
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import asyncio

app = Flask(__name__)

url = None


# Database setup
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY,
            url Text,
            title TEXT,
            price TEXT,
            img_url TEXT,
            link TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET", "POST"])
async def index():
    if request.method == "POST":
        target_url = request.form["url"]
        global url
        url = target_url
        pages = request.form["pages"]
        await crawl(target_url, pages)
        return redirect(url_for("result"))
    return render_template("index.html")


async def crawl(target_url, pages):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(target_url)
    # Wait for the page to load (adjust as necessary)
    driver.implicitly_wait(5)
    await asyncio.sleep(1)
    await crawl_target(driver, target_url)
    await auto_scroll(driver, target_url, pages)
    driver.quit()


async def crawl_target(driver, target_url):
    soup = BeautifulSoup(driver.page_source, "lxml")
    data = []
    base_url = target_url.split("//")[0] + target_url.split("//")[1].split("/")[0]

    elements = soup.find_all("div", attrs={"data-item-index": True})

    for element in elements:
        info = {
            "title": (
                element.find("h2", class_="kt-post-card__title").text.strip()
                if element.find("h2", class_="kt-post-card__title")
                else "N/A"
            ),
            "price": (
                element.find("div", class_="kt-post-card__description").text.strip()
                if element.find("div", class_="kt-post-card__description")
                else "N/A"
            ),
            "img_url": (
                element.find("img", class_="kt-image-block__image")["data-src"]
                if element.find("img", class_="kt-image-block__image")
                else "N/A"
            ),
            "link": (
                base_url + element.find("a", class_="kt-post-card__action")["href"]
                if element.find("a", class_="kt-post-card__action")
                else "N/A"
            ),
        }

        # Save image locally
        if info["img_url"] != "N/A":
            img_name = info["img_url"].split("/")[-1]
            img_folder_path = os.path.join("static", "images")
            os.makedirs(img_folder_path, exist_ok=True)
            img_data = requests.get(info["img_url"]).content

            with open(os.path.join(img_folder_path, img_name), "wb") as f:
                f.write(img_data)

            info["img_url"] = f"images/{img_name}"

        data.append(info)

        # Store in SQLite database
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO results (url,title, price, img_url, link) VALUES (?, ?, ?, ?, ?)",
            (target_url, info["title"], info["price"], info["img_url"], info["link"]),
        )
        conn.commit()
        conn.close()

    # driver.quit()


async def auto_scroll(driver, target_url, pages):
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service)

    # scroll part start
    last_height = driver.execute_script("return document.body.scrollHeight")
    i = 0
    pages_scrolls = int(pages) if pages else 1
    while i < pages_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new content to load
        await crawl_target(driver, target_url)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Exit loop if no new content is loaded
        last_height = new_height
        i += 1

    # scroll end


@app.route("/result")
def result():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    global url
    (
        c.execute(f"SELECT * FROM results WHERE `url`== '{url}'")
        if url
        else c.execute("SELECT * FROM results")
    )
    results = c.fetchall()
    conn.close()
    return render_template("result.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
