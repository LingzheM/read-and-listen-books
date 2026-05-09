"""
有声书播放器

用法：
  python play.py 活着 part_1 chapter_1 section_1
  python play.py 活着 part_1 chapter_1 section_1 --gap 1
  python play.py                                   # 列出所有书籍
  python play.py 活着                              # 列出 part
  python play.py 活着 part_1                       # 列出 chapter
  python play.py 活着 part_1 chapter_1             # 列出 section
"""

import os
import sys
import time
import glob
import argparse
import subprocess

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def play(path: str):
    if sys.platform == "win32":
        import ctypes
        winmm = ctypes.windll.winmm
        winmm.mciSendStringW(f'open "{path}" type mpegvideo alias track', None, 0, None)
        winmm.mciSendStringW('play track wait', None, 0, None)
        winmm.mciSendStringW('close track', None, 0, None)
    elif sys.platform == "darwin":
        subprocess.run(["afplay", path])
    else:
        for player in ["mpg123", "ffplay"]:
            if subprocess.run(["which", player], capture_output=True).returncode == 0:
                args = [player, path] if player == "mpg123" else ["ffplay", "-nodisp", "-autoexit", path]
                subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return


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


def get_audio_files(book: str, part: str, chapter: str, section: str) -> list[str]:
    directory = os.path.join(OUTPUT_DIR, book, part, chapter, section)
    if not os.path.exists(directory):
        print(f"[错误] 找不到：output/{book}/{part}/{chapter}/{section}/")
        print(f"       请先运行：python main.py {book} {part} {chapter} {section}")
        sys.exit(1)

    files = sorted(glob.glob(os.path.join(directory, "*.wav")))
    if not files:
        print(f"[错误] 该目录下没有音频文件")
        sys.exit(1)
    return files


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description="有声书播放器")
    parser.add_argument("book",    nargs="?", help="书名")
    parser.add_argument("part",    nargs="?", help="part")
    parser.add_argument("chapter", nargs="?", help="chapter")
    parser.add_argument("section", nargs="?", help="section")
    parser.add_argument("--gap", type=float, default=0.0, help="句子间停顿秒数")
    args = parser.parse_args()

    if not args.book:
        list_dir(OUTPUT_DIR, "可用书籍")
    if not args.part:
        list_dir(os.path.join(OUTPUT_DIR, args.book), f"《{args.book}》的 part")
    if not args.chapter:
        list_dir(os.path.join(OUTPUT_DIR, args.book, args.part), f"{args.part} 的 chapter")
    if not args.section:
        list_dir(os.path.join(OUTPUT_DIR, args.book, args.part, args.chapter), f"{args.chapter} 的 section")

    files = get_audio_files(args.book, args.part, args.chapter, args.section)
    total = len(files)

    print(f"─────────────────────────────────────")
    print(f" {args.book} / {args.part} / {args.chapter} / {args.section}  ({total} 句)")
    print(f"─────────────────────────────────────")

    start_time = time.time()
    for i, path in enumerate(files, start=1):
        print(f"[{i:>3}/{total}] {os.path.basename(path)}")
        play(path)
        if args.gap > 0 and i < total:
            time.sleep(args.gap)

    elapsed = time.time() - start_time
    print(f"─────────────────────────────────────")
    print(f"✅ 播放完毕，用时 {format_time(elapsed)}")


if __name__ == "__main__":
    main()