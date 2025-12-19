# ✂️ Iris Audio Cutter | 智能音频切片工具

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://你的应用链接.streamlit.app)

这是一个基于 **OpenAI Whisper** 和 **Streamlit** 构建的智能音频处理工具。它能自动识别音频中的语音内容，允许用户通过搜索关键词或查看转录文本，精准定位并“一键剪切”出想要的音频片段。

不再需要反复听录音找时间点，像编辑文档一样编辑音频！

## ✨ 主要功能

* **🎙️ 智能转录**：利用 OpenAI Whisper 模型（Base）将上传的音频快速转换为文本。
* **🔍 文本定位**：直接搜索文稿中的关键词（如“老虎”、“Meeting”），自动匹配对应的时间轴。
* **✂️ 精准剪切**：基于匹配到的时间段，自动调用 FFmpeg 进行无损音频切割。
* **💾 即时下载**：处理完成后，可直接下载剪切好的 MP3/WAV 片段。

## 🛠️ 技术栈

* **Python 3.11**
* **[Streamlit](https://streamlit.io/)**: 构建交互式 Web 界面
* **[OpenAI Whisper](https://github.com/openai/whisper)**: 强大的语音识别模型
* **[Pydub](https://github.com/jiaaro/pydub)**: 音频处理与操作
* **FFmpeg**: 底层音频编解码支持

## 🚀 在线体验

点击下方链接直接使用（无需安装）：
👉 **[点击这里打开 Iris Audio Cutter](https://iris-audio-cutter-mh23w6cuwvmens7nxangmj.streamlit.app/)**

---

## 💻 本地运行指南

如果你想在自己的电脑上运行或修改代码，请按以下步骤操作：

1. 克隆仓库
```bash
git clone [https://github.com/fayeiris999-jpg/Iris-Audio-Cutter.git](https://github.com/fayeiris999-jpg/Iris-Audio-Cutter.git)
cd Iris-Audio-Cutter

2. 安装系统依赖 (FFmpeg) 
本项目依赖系统级的 FFmpeg 工具，请确保你已安装：
	•	Mac (使用 Homebrew):
```bash

brew install ffmpeg

	•	Windows: 下载 FFmpeg（https://ffmpeg.org/download.html）并配置环境变量。
	•	Ubuntu/Linux:
```bash

sudo apt-get update && sudo apt-get install ffmpeg

3.安装 Python 依赖 
建议使用虚拟环境（Python 3.11 推荐）：
```bash

pip install -r requirements.txt

4. 启动应用
```bash

streamlit run streamlit_app.py

启动后，浏览器会自动打开 http://localhost:8501 。
📂 项目结构
Iris-Audio-Cutter/
├── streamlit_app.py   # 前端界面主程序
├── audio_cutter.py    # 音频处理核心逻辑类
├── requirements.txt   # Python 依赖库列表
├── packages.txt       # Streamlit Cloud 系统依赖 (ffmpeg)
└── README.md          # 项目说明文档

🤝 贡献与反馈
欢迎提交 Issue 或 Pull Request！如果你觉得这个工具有用，请给个 ⭐️ Star！

Created by Faye Iris
