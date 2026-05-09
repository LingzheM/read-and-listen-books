"""
TTS 生成器

输入：input/<书名>/<part>/<chapter>/section.txt
输出：output/<书名>/<part>/<chapter>/<section>/line001.wav

用法：
  python main.py 活着 part_1 chapter_1 section_1
  python main.py 活着 part_1 chapter_1 section_1 --voice yunyang
  python main.py 活着 part_1 chapter_1 section_1 --speed +20%
  python main.py 活着 part_1 chapter_1 section_1 --force
  python main.py                                   # 列出所有书籍
  python main.py 活着                              # 列出 part
  python main.py 活着 part_1                       # 列出 chapter
  python main.py 活着 part_1 chapter_1             # 列出 section
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


def list_dir(path: str, label: str):
    if not os.path.exists(path):
        print(f"[错误] 路径不存在：{path}")
        sys.exit(1)

    items = sorted([
        d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ])

    txts = sorted([
        os.path.splitext(f)[0]
        for f in os.listdir(path)
        if f.endswith(".txt")
    ])

    entries = items + txts
    if not entries:
        print(f"[提示] {path} 下没有内容")
    else:
        print(f"{label}：")
        for e in entries:
            print(f"  · {e}")
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
    parser.add_argument("book",    nargs="?", help="书名")
    parser.add_argument("part",    nargs="?", help="part，如 part_1")
    parser.add_argument("chapter", nargs="?", help="chapter，如 chapter_1")
    parser.add_argument("section", nargs="?", help="section，如 section_1")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="yunxi/yunyang/xiaoxiao/nanami/keita")
    parser.add_argument("--speed", default="+0%",         help="语速，如 +20%%")
    parser.add_argument("--force", action="store_true",   help="强制重新生成已存在文件")
    args = parser.parse_args()

    if not args.book:
        list_dir(INPUT_DIR, "可用书籍")

    if not args.part:
        list_dir(os.path.join(INPUT_DIR, args.book), f"《{args.book}》的 part")

    if not args.chapter:
        list_dir(os.path.join(INPUT_DIR, args.book, args.part), f"{args.part} 的 chapter")

    if not args.section:
        list_dir(os.path.join(INPUT_DIR, args.book, args.part, args.chapter), f"{args.chapter} 的 section")

    input_path = os.path.join(INPUT_DIR, args.book, args.part, args.chapter, f"{args.section}.txt")
    output_dir = os.path.join(OUTPUT_DIR, args.book, args.part, args.chapter, args.section)
    voice      = VOICES.get(args.voice, args.voice)

    os.makedirs(output_dir, exist_ok=True)
    lines = read_lines(input_path)

    print(f"─────────────────────────────────────")
    print(f" {args.book} / {args.part} / {args.chapter} / {args.section}")
    print(f" 共 {len(lines)} 行｜音色：{voice}｜语速：{args.speed}")
    print(f" 输出：output/{args.book}/{args.part}/{args.chapter}/{args.section}/")
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
    print(f"✅ 完成：output/{args.book}/{args.part}/{args.chapter}/{args.section}/")


if __name__ == "__main__":
    asyncio.run(main())