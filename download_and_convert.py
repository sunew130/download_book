import os
import subprocess
import tempfile
import argparse
from Zlibrary import Zlibrary

def download_and_convert(title, output_dir, userid, userkey):
    try:
        Z = Zlibrary(remix_userid=userid, remix_userkey=userkey)
    except Exception as e:
        print(f"Failed to initialize Zlibrary: {e}")
        return

    try:
        results = Z.search(message=title)
    except Exception as e:
        print(f"Search failed: {e}")
        return

    if 'books' not in results or not isinstance(results['books'], list):
        print("No books found or invalid search results")
        return

    books = results['books']

    # Priority: EPUB
    for book in books:
        if book.get('extension') == 'epub':
            try:
                filename, content = Z.downloadBook(book)
                epub_path = os.path.join(output_dir, filename)
                with open(epub_path, 'wb') as f:
                    f.write(content)
                print(f"Downloaded {filename} to {epub_path}")
                return
            except Exception as e:
                print(f"Failed to download EPUB: {e}")

    # If no EPUB, look for PDF
    for book in books:
        if book.get('extension') == 'pdf':
            try:
                pdf_filename, pdf_content = Z.downloadBook(book)
                # Save PDF to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                    temp_pdf.write(pdf_content)
                    temp_pdf_path = temp_pdf.name

                # Convert to EPUB
                base_name = os.path.splitext(pdf_filename)[0]
                epub_filename = base_name + '.epub'
                epub_path = os.path.join(output_dir, epub_filename)
                try:
                    subprocess.run(['ebook-convert', temp_pdf_path, epub_path], check=True)
                    print(f"Converted {pdf_filename} to {epub_filename} and saved to {epub_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Conversion failed: {e}")
                finally:
                    os.remove(temp_pdf_path)  # Delete temporary PDF
                return
            except Exception as e:
                print(f"Failed to download PDF: {e}")

    print("No EPUB or PDF found for the book")

def main():
    parser = argparse.ArgumentParser(description="Download book from Z-Library and convert to EPUB if necessary.")
    parser.add_argument("--title", required=True, help="Title of the book to search for")
    parser.add_argument("--output", required=True, help="Output directory for the downloaded book")
    parser.add_argument("--userid", required=True, help="Z-Library remix_userid")
    parser.add_argument("--userkey", required=True, help="Z-Library remix_userkey")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Call the download and convert function
    download_and_convert(args.title, args.output, args.userid, args.userkey)

if __name__ == "__main__":
    main()