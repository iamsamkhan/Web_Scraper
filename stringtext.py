import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import openai
from secret import openai_key, system_role, urls
import re
import string

openai.api_key = openai_key

def sanitize_title(title, max_length=60):
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

def save_text_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def get_text_from_url(url):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=chrome_options)

    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = sanitize_title(soup.title.string.replace(' ', '-').replace('|', '-').replace(':', '-').replace('/', '-'))

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

if __name__ == "__main__":
    save_folder = "../docs/webscraped-texts"
    os.makedirs(save_folder, exist_ok=True)

    for url in urls:
        text, title = get_text_from_url(url)

        if text:
            txt_path = f"{save_folder}/{title}.txt"
            cleaned_text = remove_non_ascii_chars(remove_non_printable_chars(clean_text_gpt4(text)))
            save_text_to_file(cleaned_text, txt_path)
            print(f"\nText saved to {txt_path}")