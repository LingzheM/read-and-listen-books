"""
章节合并工具 - 将一个 section 的所有音频拼接成单个文件

输出：output/<书名>/<part>/<chapter>/<section>.wav

用法：
  python merge.py 活着 part_1 chapter_1 section_1
  python merge.py                                   # 列出所有书籍
  python merge.py 活着                              # 列出 part
  python merge.py 活着 part_1                       # 列出 chapter
  python merge.py 活着 part_1 chapter_1             # 列出 section
"""

import os
import sys
import glob
import argparse

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def list_dir(path: str, label: str):
    if not os.path.exists(path):
        print(f"[错误] 路径不存在：{path}")
        sys.exit(1)

    items = sorted([
        d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ])

    if not items:
        print(f"[提示] {path} 下没有内容")
    else:
        print(f"{label}：")
        for item in items:
            print(f"  · {item}")
    sys.exit(0)


def merge(book: str, part: str, chapter: str, section: str):
    section_dir = os.path.join(OUTPUT_DIR, book, part, chapter, section)
    files = sorted(glob.glob(os.path.join(section_dir, "*.wav")))

    if not files:
        print(f"[错误] {section_dir} 下没有音频文件")
        sys.exit(1)

    output_path = os.path.join(OUTPUT_DIR, book, part, chapter, f"{section}.wav")

    print(f"─────────────────────────────────────")
    print(f" {book} / {part} / {chapter} / {section}  ({len(files)} 句)")
    print(f" 输出：output/{book}/{part}/{chapter}/{section}.wav")
    print(f"─────────────────────────────────────")

    # 直接拼接原始字节，Edge-TTS 输出的是 MP3 数据
    # MP3 字节拼接完全合法，无质量损失
    with open(output_path, "wb") as out:
        for i, path in enumerate(files):
            with open(path, "rb") as f:
                out.write(f.read())
            print(f"[{i+1:>3}/{len(files)}] {os.path.basename(path)}")

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"─────────────────────────────────────")
    print(f"✅ 完成：output/{book}/{part}/{chapter}/{section}.wav  ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Section 合并工具")
    parser.add_argument("book",    nargs="?", help="书名")
    parser.add_argument("part",    nargs="?", help="part")
    parser.add_argument("chapter", nargs="?", help="chapter")
    parser.add_argument("section", nargs="?", help="section")
    args = parser.parse_args()

    if not args.book:
        list_dir(OUTPUT_DIR, "可用书籍")
    if not args.part:
        list_dir(os.path.join(OUTPUT_DIR, args.book), f"《{args.book}》的 part")
    if not args.chapter:
        list_dir(os.path.join(OUTPUT_DIR, args.book, args.part), f"{args.part} 的 chapter")
    if not args.section:
        list_dir(os.path.join(OUTPUT_DIR, args.book, args.part, args.chapter), f"{args.chapter} 的 section")

    merge(args.book, args.part, args.chapter, args.section)


if __name__ == "__main__":
    main()