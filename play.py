"""
有声书播放器 - 按顺序播放某章节的所有 WAV

用法：
  python play.py chapter-5
  python play.py chapter-5 --gap 1
  python play.py           # 不带参数时列出可用章节

依赖：
  pip install playsound==1.2.2
"""

import os
import sys
import time
import glob
import argparse
from playsound import playsound

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def list_chapters():
    dirs = sorted([
        d for d in os.listdir(OUTPUT_DIR)
        if os.path.isdir(os.path.join(OUTPUT_DIR, d))
    ]) if os.path.exists(OUTPUT_DIR) else []

    if not dirs:
        print("[提示] output/ 下还没有任何章节，请先运行 main.py 生成")
    else:
        print("已生成章节：")
        for d in dirs:
            count = len(glob.glob(os.path.join(OUTPUT_DIR, d, "*.wav")))
            print(f"  · {d}  ({count} 句)")
    sys.exit(0)


def get_wav_files(chapter: str) -> list[str]:
    directory = os.path.join(OUTPUT_DIR, chapter)
    if not os.path.exists(directory):
        print(f"[错误] 找不到章节：output/{chapter}/")
        print(f"       请先运行：python main.py {chapter}")
        sys.exit(1)

    files = sorted(glob.glob(os.path.join(directory, "*.wav")))
    if not files:
        print(f"[错误] output/{chapter}/ 下没有 WAV 文件")
        sys.exit(1)

    return files


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description="有声书播放器")
    parser.add_argument("chapter", nargs="?", help="章节名，如 chapter-5")
    parser.add_argument("--gap", type=float, default=0.0, help="句子间停顿秒数（默认：0）")
    args = parser.parse_args()

    if not args.chapter:
        list_chapters()

    files = get_wav_files(args.chapter)
    total = len(files)

    print(f"─────────────────────────────────────")
    print(f" 章节：{args.chapter}  ({total} 句)")
    print(f"─────────────────────────────────────")

    start_time = time.time()

    for i, path in enumerate(files, start=1):
        print(f"[{i:>3}/{total}] {os.path.basename(path)}")
        playsound(path)  # 阻塞播放，播完再播下一句
        if args.gap > 0 and i < total:
            time.sleep(args.gap)

    elapsed = time.time() - start_time
    print(f"─────────────────────────────────────")
    print(f"✅ 播放完毕，用时 {format_time(elapsed)}")


if __name__ == "__main__":
    main()