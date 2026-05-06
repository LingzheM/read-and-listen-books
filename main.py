"""
日语 TTS MVP - 基于 Edge-TTS
逐行读取 sources/chapter-5.txt，一句一句合成并播放

用法：
  python jp_tts.py
  python jp_tts.py --voice keita
  python jp_tts.py --speed +20%
  python jp_tts.py --no-play        # 只保存不播放
  python jp_tts.py --file sources/chapter-3.txt  # 指定其他文件
"""

import asyncio
import argparse
import os
import sys
import tempfile
import edge_tts

# ─── 默认配置 ─────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))  # 脚本所在目录
DEFAULT_TXT = os.path.join(BASE_DIR, "sources", "chapter-5.txt")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")           # 音频输出目录

VOICES = {
    "nanami": "ja-JP-NanamiNeural",  # 女声（默认）
    "keita":  "ja-JP-KeitaNeural",   # 男声
}
DEFAULT_VOICE = VOICES["nanami"]


# ─── 读取文本：按行分割，过滤空行 ────────────────────────────
def read_lines(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        print(f"[错误] 文件不存在：{file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    import re
    # 过滤空行 + 无法朗读的符号行（如 ---、***、===）
    lines = [l for l in lines if l and not re.fullmatch(r'[-=*#_/|\s]+', l)]

    if not lines:
        print("[错误] 文件内容为空")
        sys.exit(1)

    return lines


# ─── 合成单句 ────────────────────────────────────────────────
async def synthesize_line(text: str, voice: str, rate: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(output_path)


# ─── 跨平台播放 ──────────────────────────────────────────────
def play_audio(path: str):
    if sys.platform == "darwin":
        os.system(f"afplay '{path}'")
    elif sys.platform == "win32":
        os.system(f'start /wait "" "{path}"')
    else:
        for player in ["mpg123", "ffplay -nodisp -autoexit", "aplay"]:
            if os.system(f"which {player.split()[0]} > /dev/null 2>&1") == 0:
                os.system(f"{player} '{path}' > /dev/null 2>&1")
                return
        print("[警告] 未找到可用播放器，请手动打开音频文件")


# ─── 主流程 ───────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="日语逐行 TTS（Edge-TTS）")
    parser.add_argument("--file",    default=DEFAULT_TXT,       help="文本文件路径（默认：sources/chapter-5.txt）")
    parser.add_argument("--voice",   default=DEFAULT_VOICE,     help="音色：nanami（女）/ keita（男）（默认：nanami）")
    parser.add_argument("--speed",   default="+0%",             help="语速，如 +20%% / -20%%（默认：+0%%）")
    parser.add_argument("--no-play", action="store_true",       help="只保存音频，不播放")
    args = parser.parse_args()

    voice = VOICES.get(args.voice, args.voice)
    lines = read_lines(args.file)

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    chapter_name = os.path.splitext(os.path.basename(args.file))[0]

    print(f"─────────────────────────────────────")
    print(f" 文件：{args.file}")
    print(f" 音色：{voice}")
    print(f" 语速：{args.speed}")
    print(f" 共 {len(lines)} 行")
    print(f"─────────────────────────────────────")

    for i, line in enumerate(lines, start=1):
        output_path = os.path.join(OUTPUT_DIR, f"{chapter_name}_line{i:03d}.mp3")

        print(f"[{i}/{len(lines)}] {line}")

        # 合成
        await synthesize_line(line, voice, args.speed, output_path)

        # 播放
        if not args.no_play:
            play_audio(output_path)

    print(f"─────────────────────────────────────")
    print(f"✅ 完成，音频保存在：{OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())