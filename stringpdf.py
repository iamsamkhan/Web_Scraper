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

openai.api_key = openai_key

def sanitize_title(title, max_length=100):
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'\s+', '-', title)
    return title[:max_length]


def clean_text_gpt4(text):
    prompt = f"Clean this text: {text}, Cleaned:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_role},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message['content'].strip()

def remove_non_ascii_chars(text):
    return ''.join(char for char in text if ord(char) < 128)

def remove_non_printable_chars(text):
    printable_chars = set(string.printable)
    return ''.join(filter(lambda x: x in printable_chars, text))

def save_text_to_pdf(text, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    text_object = c.beginText()
    text_object.setTextOrigin(10, 750)
    text_object.setFont("Helvetica", 12)

    wrapper = TextWrapper(width=80)
    lines = text.split('\n')
    for line in lines:
        wrapped_lines = wrapper.wrap(line)
        for wrapped_line in wrapped_lines:
            text_object.textLine(wrapped_line)
        text_object.moveCursor(0, -14)

    c.drawText(text_object)
    c.showPage()
    c.save()


def get_text_from_url(url):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=chrome_options)

    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        title = soup.title.string.replace(' ', '-').replace('|', '-').replace(':', '-').replace('/', '-')

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return (text, title)

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()

def process_urls(urls):
    save_folder = Path("../docs/webscraped-pdfs")
    save_folder.mkdir(parents=True, exist_ok=True)

    for url in urls:
        text, title = get_text_from_url(url)
        title = sanitize_title(title)

        if text:
            pdf_path = str(save_folder / f"{title}.pdf")
            cleaned_text = remove_non_ascii_chars(remove_non_printable_chars(clean_text_gpt4(text)))
            save_text_to_pdf(cleaned_text, pdf_path)
            print(f"\nText saved to {pdf_path}")

if __name__ == "__main__":
    process_urls(urls)