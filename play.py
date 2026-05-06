"""
有声书播放器 - 按顺序播放 output 目录下的所有 MP3
用法：
  python play.py                        # 播放 output/ 下所有 MP3
  python play.py --dir output/chapter-5 # 指定目录
  python play.py --gap 0.5              # 句子之间停顿 0.5 秒（默认 0）
"""

import os
import sys
import time
import glob
import argparse

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(BASE_DIR, "output")


def get_mp3_files(directory: str) -> list[str]:
    """获取目录下所有 MP3，按文件名自然排序"""
    pattern = os.path.join(directory, "*.mp3")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"[错误] 目录下没有找到 MP3 文件：{directory}")
        sys.exit(1)

    return files


def play(path: str):
    """跨平台播放单个音频，阻塞直到播放完毕"""
    if sys.platform == "darwin":
        os.system(f"afplay '{path}'")

    elif sys.platform == "win32":
        # Windows 用 PowerShell 的 Media.SoundPlayer（仅支持 WAV）
        # 改用 winmm 通过 cmdlet 播放 MP3
        cmd = (
            f'powershell -c "'
            f'$player = New-Object System.Windows.Media.MediaPlayer;'
            f'$player.Open([System.Uri]::new(\'{path}\'));'
            f'$player.Play();'
            f'Start-Sleep -Milliseconds ($player.NaturalDuration.TimeSpan.TotalMilliseconds + 500);'
            f'$player.Close()"'
        )
        os.system(cmd)

    else:
        # Linux
        for player in ["mpg123", "ffplay -nodisp -autoexit", "aplay"]:
            if os.system(f"which {player.split()[0]} > /dev/null 2>&1") == 0:
                os.system(f"{player} '{path}' > /dev/null 2>&1")
                return
        print("[警告] 未找到可用播放器，请安装 mpg123：sudo apt install mpg123")


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

        # 从文件名提取句子编号显示进度
        print(f"[{i:>3}/{total}] {filename}")

        play(path)

        # 句子间停顿
        if args.gap > 0 and i < total:
            time.sleep(args.gap)

    elapsed = time.time() - start_time

    print(f"─────────────────────────────────────")
    print(f"✅ 播放完毕，共 {total} 句，用时 {format_time(elapsed)}")


if __name__ == "__main__":
    main()