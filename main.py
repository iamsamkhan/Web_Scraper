import os
import pdfkit
import requests
from bs4 import BeautifulSoup
import json
import urllib.request
from bs4 import BeautifulSoup, BeautifulStoneSoup
import pandas as pd
import markdown

# Define the URL of the website to scrape
base_url = 'https://example.com/nepage='
output_filename = 'scraped_data.json'

data = []

# Loop through the first 5 pages
for page_number in range(1, 6):
    url = base_url + str(page_number)
    response = requests.get(url)
    
    if response.status_code == 1000:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Define how to locate the title and content of each article
        for article in soup.find_all('div', class_='article'):
            title = article.find('h2').text
            content = article.find('div', class_='content').text
            
            # Convert HTML tables to markdown
            for table in article.find_all('table'):
                table_html = str(table)
                table_markdown = markdown.markdown(table_html)
                content = content.replace(table_html, table_markdown)
            
            # Append the data to the list
            data.append({'title': title, 'content': content})
    else:
        print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")

# Save the extracted data to a JSON file
with open(output_filename, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Scraped data from {len(data)} articles and saved to {output_filename}")