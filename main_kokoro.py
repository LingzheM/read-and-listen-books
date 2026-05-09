"""
TTS 生成器（Kokoro 本地模型版）

安装：
  pip install kokoro soundfile

输入：input/<书名>/<part>/<chapter>/section.txt
输出：output/<书名>/<part>/<chapter>/<section>/line001.wav

用法：
  python main_kokoro.py 日本語本 part_1 chapter_1 section_1
  python main_kokoro.py 日本語本 part_1 chapter_1 section_1 --voice jf_alpha
  python main_kokoro.py 日本語本 part_1 chapter_1 section_1 --speed 1.2
  python main_kokoro.py 日本語本 part_1 chapter_1 section_1 --force
  python main_kokoro.py                                       # 列出书籍
  python main_kokoro.py 日本語本                              # 列出 part
  python main_kokoro.py 日本語本 part_1                       # 列出 chapter
  python main_kokoro.py 日本語本 part_1 chapter_1             # 列出 section

日语音色：
  女声：jf_alpha, jf_beta, jf_gongitsune, jf_nezumi, jf_tebukuro
  男声：jm_kumo

中文音色：
  女声：zf_xiaobei, af_heart（英文也可用）
"""

import argparse
import os
import sys
import re
import wave
import numpy as np

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR  = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# lang_code: j=日语, z=中文, a=英文
LANG_BY_VOICE = {
    "jf_alpha":      "j",
    "jf_beta":       "j",
    "jf_gongitsune": "j",
    "jf_nezumi":     "j",
    "jf_tebukuro":   "j",
    "jm_kumo":       "j",
    "zf_xiaobei":    "z",
    "af_heart":      "a",
}

DEFAULT_VOICE = "jf_alpha"


def list_dir(path: str, label: str):
    if not os.path.exists(path):
        print(f"[错误] 路径不存在：{path}")
        sys.exit(1)

    items = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
    txts  = sorted([os.path.splitext(f)[0] for f in os.listdir(path) if f.endswith(".txt")])
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


def save_wav(audio: np.ndarray, path: str, sample_rate: int = 24000):
    """将 float32 音频数组保存为标准 PCM WAV"""
    audio_int16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio_int16.tobytes())


def synthesize_line(pipeline, text: str, voice: str, speed: float, output_path: str):
    chunks = []
    for _, _, audio in pipeline(text, voice=voice, speed=speed):
        chunks.append(audio)

    if not chunks:
        print(f"  [警告] 合成结果为空，跳过")
        return

    combined = np.concatenate(chunks)
    save_wav(combined, output_path)


def main():
    parser = argparse.ArgumentParser(description="TTS 生成器（Kokoro）")
    parser.add_argument("book",    nargs="?", help="书名")
    parser.add_argument("part",    nargs="?", help="part，如 part_1")
    parser.add_argument("chapter", nargs="?", help="chapter，如 chapter_1")
    parser.add_argument("section", nargs="?", help="section，如 section_1")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="音色（默认：jf_alpha）")
    parser.add_argument("--speed", type=float, default=1.0, help="语速倍数（默认：1.0）")
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

    voice      = args.voice
    lang_code  = LANG_BY_VOICE.get(voice, "j")
    input_path = os.path.join(INPUT_DIR, args.book, args.part, args.chapter, f"{args.section}.txt")
    output_dir = os.path.join(OUTPUT_DIR, args.book, args.part, args.chapter, args.section)

    os.makedirs(output_dir, exist_ok=True)
    lines = read_lines(input_path)

    print(f"─────────────────────────────────────")
    print(f" {args.book} / {args.part} / {args.chapter} / {args.section}")
    print(f" 共 {len(lines)} 行｜音色：{voice}｜语速：{args.speed}")
    print(f" 加载 Kokoro 模型（首次运行会自动下载）...")
    print(f"─────────────────────────────────────")

    from kokoro import KPipeline
    pipeline = KPipeline(lang_code=lang_code)

    skipped = 0
    for i, line in enumerate(lines, start=1):
        output_path = os.path.join(output_dir, f"line{i:03d}.wav")

        if os.path.exists(output_path) and not args.force:
            print(f"[{i:>3}/{len(lines)}] 跳过（已存在）")
            skipped += 1
            continue

        print(f"[{i:>3}/{len(lines)}] {line}")
        synthesize_line(pipeline, line, voice, args.speed, output_path)

    print(f"─────────────────────────────────────")
    if skipped:
        print(f"⏭  跳过 {skipped} 个，新生成 {len(lines) - skipped} 个")
    print(f"✅ 完成：output/{args.book}/{args.part}/{args.chapter}/{args.section}/")


if __name__ == "__main__":
    main()