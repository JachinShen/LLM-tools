import argparse
from pathlib import Path
from ebooklib import epub

def initialize_Ebook(title, identifier='id123456', lang='zh'):
    book = epub.EpubBook()
    book.set_title(title)
    book.set_identifier(identifier)
    book.set_language(lang)
    return book

def convert_md_to_html(file):
    data = open(file).read()
    return '\n'.join([f"<p>{p}</p>" for p in data.split("\n\n")])

def add_Chapters(book, base_dir):
    pages = []
    toc = []
    filelist = sorted(list(base_dir.glob("*.md")))
    for file in filelist:
        html_filename = file.name.replace(".md", ".html")
        content = convert_md_to_html(file)
        c1 = epub.EpubHtml(title=file.name, file_name=html_filename, lang="zh", content=content)
        book.add_item(c1)
        toc.append(epub.Link(html_filename, file.name, file.name))
        pages.append(c1)
    return pages, toc

def define_toc_and_spine(book, pages, toc):
    book.toc = tuple(toc)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + pages

def write_epub(book, output_fp):
    epub.write_epub(output_fp, book, {})

def main():
    parser = argparse.ArgumentParser(description='Convert markdown files to an ePub book.')
    parser.add_argument('--md-dir', type=Path, required=True, help='Input markdown directory')
    parser.add_argument('--output', type=Path, help='Output ePub file path')
    args = parser.parse_args()

    md_dir = args.md_dir
    output_fp = args.output or md_dir / Path(f"{md_dir.name}.epub")

    book = initialize_Ebook(md_dir.name)
    pages, toc = add_Chapters(book, md_dir)
    define_toc_and_spine(book, pages, toc)
    write_epub(book, output_fp)

if __name__ == "__main__":
    main()