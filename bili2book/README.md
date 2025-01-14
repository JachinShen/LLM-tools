# Bili2Book

A pipeline to convert education videos from Bilibili to ebooks.

## Pipeline

1. **Download Subtitles**: Use `yt-dlp` to download SRT subtitle files from Bilibili videos.
2. **Convert SRT to Markdown**: Use `bilisubs2md.py` to convert the downloaded SRT files to Markdown format.
3. **Convert Markdown to Ebook**: Use `compose_ebook.py` to convert the Markdown files to an ebook format (e.g., ePub).

## Usage

### 1. Download Subtitles

First, use `yt-dlp` to download the subtitle files from a Bilibili video. Replace `<bili_url>` with the URL of the Bilibili video you want to download.

List available subtitles:

```bash
yt-dlp --list-subs --no-playlist --cookies-from-browser chrome <bili_url>
```

Download subtitles:
```bash
yt-dlp --write-sub --sub-lang ai-zh --skip-download --cookies-from-browser chrome <bili_url>
```

This command will download the subtitles in the specified language (ai-zh for Chinese) and save them as SRT files.

### 2. Convert SRT to Markdown
Navigate to the bili2book directory and run bilisubs2md.py to convert the downloaded SRT files to Markdown:

```bash
cd bili2book
python bilisubs2md.py --srt-dir <path_to_srt_files> --out-dir <path_to_output_markdown_files>
```

Replace <path_to_srt_files> with the path to the directory containing the SRT files, and <path_to_output_markdown_files> with the directory where you want to save the Markdown files.

### 3. Convert Markdown to ePub
Finally, run compose_ebook.py to convert the Markdown files to an ePub book:

```bash
python compose_ebook.py --md-dir <path_to_markdown_files> --output <path_to_output_epub_file>
```

Replace <path_to_markdown_files> with the path to the directory containing the Markdown files, and <path_to_output_epub_file> with the path where you want to save the ePub file.
