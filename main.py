"""
日语 TTS 生成器 - 将 sources/<章节>.txt 逐行合成音频保存到 output/<章节>/

用法：
  python main.py chapter-5
  python main.py chapter-5 --voice keita
  python main.py chapter-5 --speed +20%
  python main.py           # 列出可用章节
"""

import asyncio
import argparse
import os
import sys
import re
import edge_tts

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")

VOICES = {
    "nanami": "ja-JP-NanamiNeural",
    "keita":  "ja-JP-KeitaNeural",
}
DEFAULT_VOICE = VOICES["nanami"]


def list_chapters():
    files = sorted([
        os.path.splitext(f)[0]
        for f in os.listdir(SOURCES_DIR)
        if f.endswith(".txt")
    ]) if os.path.exists(SOURCES_DIR) else []

    if not files:
        print("[提示] sources/ 目录下还没有任何 txt 文件")
    else:
        print("可用章节：")
        for f in files:
            print(f"  · {f}")
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
    parser = argparse.ArgumentParser(description="日语逐行 TTS 生成器")
    parser.add_argument("chapter", nargs="?",      help="章节名，如 chapter-5")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="nanami（女）/ keita（男）")
    parser.add_argument("--speed", default="+0%",  help="语速，如 +20%% / -20%%")
    parser.add_argument("--force", action="store_true", help="强制重新生成已存在的文件")
    args = parser.parse_args()

    if not args.chapter:
        list_chapters()

    chapter    = args.chapter
    input_path = os.path.join(SOURCES_DIR, f"{chapter}.txt")
    output_dir = os.path.join(BASE_DIR, "output", chapter)
    voice      = VOICES.get(args.voice, args.voice)

    os.makedirs(output_dir, exist_ok=True)
    lines = read_lines(input_path)

    print(f"─────────────────────────────────────")
    print(f" 章节：{chapter}  ({len(lines)} 行)")
    print(f" 音色：{voice}")
    print(f" 语速：{args.speed}")
    print(f" 输出：output/{chapter}/")
    print(f"─────────────────────────────────────")

    skipped = 0
    for i, line in enumerate(lines, start=1):
        output_path = os.path.join(output_dir, f"line{i:03d}.wav")

        # 跳过已存在的文件（除非 --force）
        if os.path.exists(output_path) and not args.force:
            print(f"[{i:>3}/{len(lines)}] 跳过（已存在）：line{i:03d}.wav")
            skipped += 1
            continue

        print(f"[{i:>3}/{len(lines)}] {line}")
        await synthesize_line(line, voice, args.speed, output_path)

    print(f"─────────────────────────────────────")
    if skipped:
        print(f"⏭  跳过已存在：{skipped} 个，新生成：{len(lines) - skipped} 个")
    print(f"✅ 完成，文件保存在：output/{chapter}/")


if __name__ == "__main__":
    asyncio.run(main())