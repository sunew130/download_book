import requests
import csv
import os

import requests
import csv
import gzip

# 下载文件
catalog_url = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv.gz"
response = requests.get(catalog_url)
with open("pg_catalog.csv.gz", "wb") as f:
    f.write(response.content)

# 读取解压后的文件
with gzip.open("pg_catalog.csv.gz", 'rt', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    books = [row for row in reader if row["Authors"] != "Austen, Jane" and row["Type"] == "Text"]

# 下载 EPUB 文件
for book in books:
    book_id = book["Text#"]
    title = book["Title"]
    epub_url = f"https://www.gutenberg.org/ebooks/{book_id}.epub.noimages"
    
    response = requests.get(epub_url)
    if response.status_code == 200:
        filename = f"{title}.epub"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download book ID: {book_id}")