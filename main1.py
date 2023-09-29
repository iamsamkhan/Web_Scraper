import os
import pdfkit
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import shutil
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openai
from secret import openai_key, system_role, urls
import re
from textwrap import TextWrapper
from pathlib import Path
import string
def save_page_to_pdf(html_contents, pdf_path):
    options = {
        "quiet": "",
        "dpi": 1000,
        "enable-local-file-access": None,
        "disable-javascript": "",  # Disable JavaScript
        "load-error-handling": "ignore",  # Ignore load errors
        "load-media-error-handling": "ignore",  # Ignore media load errors
    }
    html_content = ''.join(str(content) for content in html_contents)
    pdfkit.from_string(html_content, pdf_path, options=options)



def get_multiple_html_contents(urls):
    with ThreadPoolExecutor() as executor:
        html_contents = list(executor.map(get_html_content, urls))
    return html_contents


def get_html_content(url):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    chromedriver_path = os.path.join(os.getenv('APPDATA'), 'undetected_chromedriver', 'undetected_chromedriver.exe')
    if os.path.exists(chromedriver_path):
        shutil.rmtree(chromedriver_path)
                                               
    driver = uc.Chrome(options=chrome_options)

    try:
        driver.get(url)
        html_content = driver.page_source
        return html_content
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    url = input("Enter URL of the webpage: ")
    html_contents = get_multiple_html_contents([url])

    if html_contents:
        save_folder = "docs/webscraped-pdfs"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        num = 1
        while os.path.exists(f"{save_folder}/{num}.pdf"):
            num += 1

        pdf_path = f"{save_folder}/{num}.pdf"
        save_page_to_pdf(html_contents, pdf_path)
        print(f"\nPage saved to {pdf_path}")