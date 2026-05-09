"""
TTS 生成器 - 支持中文和日语

目录结构：
  input/<书名>/chapter_1.txt
  input/<书名>/chapter_2.txt
  output/<书名>/chapter_1/line001.mp3
  output/<书名>/chapter_2/line001.mp3

用法：
  python main.py <书名> <章节>
  python main.py 活着 chapter_1
  python main.py 活着 chapter_1 --voice yunyang
  python main.py 活着 chapter_1 --speed +20%
  python main.py 活着 chapter_1 --force
  python main.py                    # 列出所有书名
  python main.py 活着               # 列出该书所有章节
"""

import asyncio
import argparse
import os
import sys
import re
import edge_tts

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR  = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

VOICES = {
    "yunxi":    "zh-CN-YunxiNeural",
    "yunyang":  "zh-CN-YunyangNeural",
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "nanami":   "ja-JP-NanamiNeural",
    "keita":    "ja-JP-KeitaNeural",
}
DEFAULT_VOICE = "yunxi"


def list_books():
    books = sorted([
        d for d in os.listdir(INPUT_DIR)
        if os.path.isdir(os.path.join(INPUT_DIR, d))
    ]) if os.path.exists(INPUT_DIR) else []

    if not books:
        print("[提示] input/ 下还没有任何书籍目录")
    else:
        print("可用书籍：")
        for b in books:
            chapters = sorted([
                os.path.splitext(f)[0]
                for f in os.listdir(os.path.join(INPUT_DIR, b))
                if f.endswith(".txt")
            ])
            print(f"  · {b}  ({len(chapters)} 章：{', '.join(chapters)})")
    sys.exit(0)


def list_chapters(book: str):
    book_dir = os.path.join(INPUT_DIR, book)
    if not os.path.exists(book_dir):
        print(f"[错误] 找不到书籍：input/{book}/")
        sys.exit(1)

    chapters = sorted([
        os.path.splitext(f)[0]
        for f in os.listdir(book_dir)
        if f.endswith(".txt")
    ])
    if not chapters:
        print(f"[提示] input/{book}/ 下还没有任何章节")
    else:
        print(f"《{book}》章节列表：")
        for c in chapters:
            print(f"  · {c}")
    sys.exit(0)


def read_lines(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        print(f"[错误] 文件不存在：{file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    lines = [l for l in lines if l and not re.fullmatch(r'[-=*#_/|\s]+', l)]

    if not lines:
        print("[错误] 文件内容为空或全部是符号行")
        sys.exit(1)

    return lines


async def synthesize_line(text: str, voice: str, rate: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(output_path)


async def main():
    parser = argparse.ArgumentParser(description="TTS 生成器")
    parser.add_argument("book",    nargs="?",              help="书名，如 活着")
    parser.add_argument("chapter", nargs="?",              help="章节名，如 chapter_1")
    parser.add_argument("--voice", default=DEFAULT_VOICE,  help="音色：yunxi / yunyang / xiaoxiao / nanami / keita")
    parser.add_argument("--speed", default="+0%",          help="语速，如 +20%% / -20%%")
    parser.add_argument("--force", action="store_true",    help="强制重新生成已存在的文件")
    args = parser.parse_args()

    if not args.book:
        list_books()

    if not args.chapter:
        list_chapters(args.book)

    book       = args.book
    chapter    = args.chapter
    input_path = os.path.join(INPUT_DIR, book, f"{chapter}.txt")
    output_dir = os.path.join(OUTPUT_DIR, book, chapter)
    voice      = VOICES.get(args.voice, args.voice)

    os.makedirs(output_dir, exist_ok=True)
    lines = read_lines(input_path)

    print(f"─────────────────────────────────────")
    print(f" 书名：{book}")
    print(f" 章节：{chapter}  ({len(lines)} 行)")
    print(f" 音色：{voice}")
    print(f" 语速：{args.speed}")
    print(f" 输出：output/{book}/{chapter}/")
    print(f"─────────────────────────────────────")

    skipped = 0
    for i, line in enumerate(lines, start=1):
        output_path = os.path.join(output_dir, f"line{i:03d}.wav")


        if os.path.exists(output_path) and not args.force:
            print(f"[{i:>3}/{len(lines)}] 跳过（已存在）")
            skipped += 1
            continue

        print(f"[{i:>3}/{len(lines)}] {line}")
        await synthesize_line(line, voice, args.speed, output_path)

    print(f"─────────────────────────────────────")
    if skipped:
        print(f"⏭  跳过 {skipped} 个，新生成 {len(lines) - skipped} 个")
    print(f"✅ 完成：output/{book}/{chapter}/")


if __name__ == "__main__":
    asyncio.run(main())