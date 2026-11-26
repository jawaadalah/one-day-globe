#!/usr/bin/env python3
"""news-image-20261126 entry: copy the rendered front page to /output/entry.png.

The image is drawn by render_news.py (run before submission); this program
only copies those exact bytes so both graded runs produce the same file.
Standard library only; no network.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.environ.get("OUTPUT_DIR") or "/output"


def main():
    src = os.path.join(HERE, "entry.png")
    os.makedirs(OUT, exist_ok=True)
    shutil.copyfile(src, os.path.join(OUT, "entry.png"))
    print("wrote entry.png", os.path.getsize(src), "bytes")


if __name__ == "__main__":
    sys.exit(main())
