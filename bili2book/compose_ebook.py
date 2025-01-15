import argparse
from pathlib import Path
from ebooklib import epub


def get_common_prefix(str_list):
    if not str_list:
        return ""
    min_str = min(str_list, key=len)  # Find the shortest string in the list
    for i, char in enumerate(min_str):
        for other in str_list:
            if other[i] != char:
                return min_str[:i]  # Return the prefix up to the point of divergence
    return min_str  # If all strings are the same, return the shortest string


def initialize_Ebook(title, identifier="id123456", lang="zh"):
    book = epub.EpubBook()
    book.set_title(title)
    book.set_identifier(identifier)
    book.set_language(lang)
    return book


def convert_md_to_html(file):
    data = open(file).read()
    return "\n".join([f"<p>{p}</p>" for p in data.split("\n\n")])


def add_Chapters(book, base_dir):
    pages = []
    toc = []
    filelist = sorted(list(base_dir.glob("*.md")))
    common_prefix = get_common_prefix([f.name for f in filelist])
    print("Clip common prefix: ", common_prefix)
    for file in filelist:
        html_filename = file.name.replace(".md", ".html").replace(common_prefix, "")
        title = html_filename.replace(".html", "")
        content = convert_md_to_html(file)
        c1 = epub.EpubHtml(
            title=title, file_name=html_filename, lang="zh", content=content
        )
        book.add_item(c1)
        toc.append(epub.Link(html_filename, title, title))
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
    parser = argparse.ArgumentParser(
        description="Convert markdown files to an ePub book."
    )
    parser.add_argument(
        "--md-dir", type=Path, required=True, help="Input markdown directory"
    )
    parser.add_argument("--output", type=Path, help="Output ePub file path")
    args = parser.parse_args()

    md_dir = args.md_dir
    output_fp = args.output or md_dir / Path(f"{md_dir.name}.epub")

    book = initialize_Ebook(md_dir.name)
    pages, toc = add_Chapters(book, md_dir)
    define_toc_and_spine(book, pages, toc)
    write_epub(book, output_fp)


if __name__ == "__main__":
    main()
