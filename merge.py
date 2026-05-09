"""
章节合并工具 - 将一章的所有 WAV 拼接成单个文件

用法：
  python merge.py 活着 chapter_1
  python merge.py              # 列出可用书籍和章节
  python merge.py 活着         # 列出该书已生成章节

输出：output/<书名>/<章节>.wav
"""

import os
import sys
import glob
import wave
import argparse

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def list_books():
    books = sorted([
        d for d in os.listdir(OUTPUT_DIR)
        if os.path.isdir(os.path.join(OUTPUT_DIR, d))
    ]) if os.path.exists(OUTPUT_DIR) else []

    if not books:
        print("[提示] output/ 下还没有任何书籍")
    else:
        print("可用书籍：")
        for b in books:
            chapters = sorted([
                d for d in os.listdir(os.path.join(OUTPUT_DIR, b))
                if os.path.isdir(os.path.join(OUTPUT_DIR, b, d))
            ])
            print(f"  · {b}  ({', '.join(chapters)})")
    sys.exit(0)


def list_chapters(book: str):
    book_dir = os.path.join(OUTPUT_DIR, book)
    chapters = sorted([
        d for d in os.listdir(book_dir)
        if os.path.isdir(os.path.join(book_dir, d))
    ]) if os.path.exists(book_dir) else []

    if not chapters:
        print(f"[提示] output/{book}/ 下还没有已生成的章节")
    else:
        print(f"《{book}》已生成章节：")
        for c in chapters:
            count = len(glob.glob(os.path.join(book_dir, c, "*.wav")))
            print(f"  · {c}  ({count} 句)")
    sys.exit(0)


def merge(book: str, chapter: str):
    chapter_dir = os.path.join(OUTPUT_DIR, book, chapter)
    files = sorted(glob.glob(os.path.join(chapter_dir, "*.wav")))

    if not files:
        print(f"[错误] output/{book}/{chapter}/ 下没有 WAV 文件")
        sys.exit(1)

    output_path = os.path.join(OUTPUT_DIR, book, f"{chapter}.wav")

    print(f"─────────────────────────────────────")
    print(f" 书名：{book}")
    print(f" 章节：{chapter}  ({len(files)} 句)")
    print(f" 输出：output/{book}/{chapter}.wav")
    print(f"─────────────────────────────────────")

    with wave.open(output_path, "wb") as out:
        for i, path in enumerate(files):
            with wave.open(path, "rb") as w:
                if i == 0:
                    out.setparams(w.getparams())
                out.writeframes(w.readframes(w.getnframes()))
            print(f"[{i+1:>3}/{len(files)}] 合并：{os.path.basename(path)}")

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"─────────────────────────────────────")
    print(f"✅ 完成：output/{book}/{chapter}.wav  ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="章节合并工具")
    parser.add_argument("book",    nargs="?", help="书名，如 活着")
    parser.add_argument("chapter", nargs="?", help="章节名，如 chapter_1")
    args = parser.parse_args()

    if not args.book:
        list_books()

    if not args.chapter:
        list_chapters(args.book)

    merge(args.book, args.chapter)


if __name__ == "__main__":
    main()