

## WSL环境配置

```
sudo apt install software-properties-common -y

sudo add-apt-repository ppa:deadsnakes/ppa -y

sudo apt update

sudo apt install python3.11 python3.11-venv python3.11-distutils -y

sudo apt install build-essential cmake -y

sudo apt install python3.11-dev -y

python3.11 -m venv venv_wsl

source venv_wsl/bin/activate

```

## 安装module

```
pip install kokoro soundfile

pip install pyopenjtalk

pip install "misaki[ja]"

pip install unidic

python -m unidic download
```

## 执行

```
python main_kokoro.py book_name1 part1 chapter1 section1 --voice jm_kumo
```