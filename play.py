"""
有声书播放器

目录结构：
  output/<书名>/chapter_1/line001.mp3
  output/<书名>/chapter_2/line001.mp3

用法：
  python play.py <书名> <章节>
  python play.py 活着 chapter_1
  python play.py 活着 chapter_1 --gap 1
  python play.py                    # 列出所有书籍
  python play.py 活着               # 列出该书已生成章节
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


def list_books():
    books = sorted([
        d for d in os.listdir(OUTPUT_DIR)
        if os.path.isdir(os.path.join(OUTPUT_DIR, d))
    ]) if os.path.exists(OUTPUT_DIR) else []

    if not books:
        print("[提示] output/ 下还没有任何书籍")
    else:
        print("已生成书籍：")
        for b in books:
            chapters = sorted([
                d for d in os.listdir(os.path.join(OUTPUT_DIR, b))
                if os.path.isdir(os.path.join(OUTPUT_DIR, b, d))
            ])
            print(f"  · {b}  ({len(chapters)} 章：{', '.join(chapters)})")
    sys.exit(0)


def list_chapters(book: str):
    book_dir = os.path.join(OUTPUT_DIR, book)
    if not os.path.exists(book_dir):
        print(f"[错误] 找不到书籍：output/{book}/")
        sys.exit(1)

    chapters = sorted([
        d for d in os.listdir(book_dir)
        if os.path.isdir(os.path.join(book_dir, d))
    ])
    if not chapters:
        print(f"[提示] output/{book}/ 下还没有已生成的章节")
    else:
        print(f"《{book}》已生成章节：")
        for c in chapters:
            count = len(glob.glob(os.path.join(book_dir, c, "*.mp3")))
            print(f"  · {c}  ({count} 句)")
    sys.exit(0)


def get_audio_files(book: str, chapter: str) -> list[str]:
    directory = os.path.join(OUTPUT_DIR, book, chapter)
    if not os.path.exists(directory):
        print(f"[错误] 找不到：output/{book}/{chapter}/")
        print(f"       请先运行：python main.py {book} {chapter}")
        sys.exit(1)

    files = sorted(glob.glob(os.path.join(directory, "*.mp3")))
    if not files:
        print(f"[错误] output/{book}/{chapter}/ 下没有音频文件")
        sys.exit(1)
    return files


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description="有声书播放器")
    parser.add_argument("book",    nargs="?", help="书名，如 活着")
    parser.add_argument("chapter", nargs="?", help="章节名，如 chapter_1")
    parser.add_argument("--gap", type=float, default=0.0, help="句子间停顿秒数（默认：0）")
    args = parser.parse_args()

    if not args.book:
        list_books()

    if not args.chapter:
        list_chapters(args.book)

    files = get_audio_files(args.book, args.chapter)
    total = len(files)

    print(f"─────────────────────────────────────")
    print(f" 书名：{args.book}")
    print(f" 章节：{args.chapter}  ({total} 句)")
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