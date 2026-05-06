"""
有声书播放器 - 按顺序播放 output 目录下的所有 MP3
用法：
  python play.py                 # 播放 output/ 下所有 MP3
  python play.py --dir output/   # 指定目录
  python play.py --gap 1         # 句子之间停顿 1 秒
"""

import os
import sys
import time
import glob
import argparse

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(BASE_DIR, "output")


def get_mp3_files(directory: str) -> list[str]:
    pattern = os.path.join(directory, "*.mp3")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"[错误] 目录下没有找到 MP3 文件：{directory}")
        sys.exit(1)
    return files


def play(path: str):
    if sys.platform == "darwin":
        os.system(f"afplay '{path}'")

    elif sys.platform == "win32":
        # 将路径反斜杠换成正斜杠，PowerShell URI 可正常识别
        p = path.replace("\\", "/")
        ps = (
            "Add-Type -AssemblyName PresentationCore; "
            "$player = New-Object System.Windows.Media.MediaPlayer; "
            f"$player.Open([uri]'{p}'); "
            "$player.Play(); "
            "Start-Sleep -Seconds 1; "
            "$ms = [int]$player.NaturalDuration.TimeSpan.TotalMilliseconds; "
            "Start-Sleep -Milliseconds $ms; "
            "$player.Close();"
        )
        os.system(f'powershell -NoProfile -Command "{ps}"')

    else:
        for player in ["mpg123", "ffplay -nodisp -autoexit", "aplay"]:
            cmd = player.split()[0]
            if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
                os.system(f"{player} '{path}' > /dev/null 2>&1")
                return
        print("[警告] 未找到可用播放器，请安装：sudo apt install mpg123")


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description="有声书播放器")
    parser.add_argument("--dir", default=DEFAULT_DIR, help="MP3 目录（默认：output/）")
    parser.add_argument("--gap", type=float, default=0.0, help="句子间停顿秒数（默认：0）")
    args = parser.parse_args()

    files = get_mp3_files(args.dir)
    total = len(files)

    print(f"─────────────────────────────────────")
    print(f" 目录：{args.dir}")
    print(f" 共 {total} 句，开始播放...")
    print(f"─────────────────────────────────────")

    start_time = time.time()

    for i, path in enumerate(files, start=1):
        filename = os.path.basename(path)
        print(f"[{i:>3}/{total}] {filename}")
        play(path)

        if args.gap > 0 and i < total:
            time.sleep(args.gap)

    elapsed = time.time() - start_time
    print(f"─────────────────────────────────────")
    print(f"✅ 播放完毕，共 {total} 句，用时 {format_time(elapsed)}")


if __name__ == "__main__":
    main()