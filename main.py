"""
日语 TTS 生成器 - 将 sources/<章节>.txt 逐行合成为 WAV 保存到 output/<章节>/

用法：
  python main.py chapter-5
  python main.py chapter-5 --voice keita
  python main.py chapter-5 --speed +20%
  python main.py           # 不带参数时列出可用章节
"""

import asyncio
import argparse
import os
import sys
import re
import edge_tts

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
SOURCES_DIR = os.path.join(BASE_DIR, "input")

VOICES = {
    "nanami": "ja-JP-NanamiNeural",  # 女声（默认）
    "keita":  "ja-JP-KeitaNeural",   # 男声
}
DEFAULT_VOICE = VOICES["nanami"]


def list_chapters():
    """列出 sources/ 下所有可用的 txt 章节"""
    files = sorted([
        os.path.splitext(f)[0]
        for f in os.listdir(SOURCES_DIR)
        if f.endswith(".txt")
    ])
    if not files:
        print(f"[提示] sources/ 目录下还没有任何 txt 文件")
    else:
        print(f"可用章节：")
        for f in files:
            print(f"  · {f}")
    sys.exit(0)


def read_lines(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        print(f"[错误] 文件不存在：{file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    # 过滤空行 + 纯符号行（如 ---、===、***）
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
    parser.add_argument("chapter", nargs="?", help="章节名，如 chapter-5（对应 sources/chapter-5.txt）")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="音色：nanami（女）/ keita（男）")
    parser.add_argument("--speed", default="+0%",         help="语速，如 +20%% / -20%%")
    args = parser.parse_args()

    # 不带参数时列出可用章节
    if not args.chapter:
        list_chapters()

    chapter     = args.chapter
    input_path  = os.path.join(SOURCES_DIR, f"{chapter}.txt")
    output_dir  = os.path.join(BASE_DIR, "output", chapter)
    voice       = VOICES.get(args.voice, args.voice)

    os.makedirs(output_dir, exist_ok=True)

    lines = read_lines(input_path)

    print(f"─────────────────────────────────────")
    print(f" 章节：{chapter}  ({len(lines)} 行)")
    print(f" 音色：{voice}")
    print(f" 语速：{args.speed}")
    print(f" 输出：output/{chapter}/")
    print(f"─────────────────────────────────────")

    for i, line in enumerate(lines, start=1):
        output_path = os.path.join(output_dir, f"line{i:03d}.wav")
        print(f"[{i:>3}/{len(lines)}] {line}")
        await synthesize_line(line, voice, args.speed, output_path)

    print(f"─────────────────────────────────────")
    print(f"✅ 完成，WAV 文件保存在：output/{chapter}/")


if __name__ == "__main__":
    asyncio.run(main())