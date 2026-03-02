# Iris Audio Cutter - 提速版 ⚡

Iris Audio Cutter 是一款专为教师和内容创作者设计的音频剪裁工具，通过文本搜索实现自动化音频片段提取。

**新功能**：一个音频可输入多段文段，同时生成多个剪辑 | **提速**：每个音频只转录一次

## 🚀 使用说明

1. **上传音频**：点击上传区域，支持一次性上传多个音频文件（mp3, wav, m4a, ogg）。
2. **添加文段**：为每个音频文件添加多段你想要截取的文本，支持添加/删除多个匹配项。
3. **一键处理**：点击“开始处理”，系统会为每个音频只进行一次转录（转录最耗时），极大地提升了处理效率。
4. **下载结果**：处理完成后，一键下载包含所有剪辑片段的 ZIP 压缩包，压缩包内按音频文件名分文件夹存放。

## ✨ 核心特性

- **极致性能**：每个音频文件仅需一次 AI 转录，即可完成无限次文本匹配和剪裁。
- **批量并发**：支持多音频、多文段同时提交，自动分类打包。
- **智能定位**：基于 Faster-Whisper 和 RapidFuzz 的模糊匹配，即使发音稍有偏差也能精准定位。
- **环境自适应**：内置 ffmpeg 路径自检测与 `static-ffmpeg` 自动安装，支持 Streamlit Cloud 一键部署。

## 🛠️ 本地运行

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
2. **启动应用**：
   ```bash
   streamlit run streamlit_app.py
   ```

## 📦 技术栈

- **Streamlit**：响应式 Web 界面框架
- **Faster-Whisper**：目前最快的 Whisper 模型实现方案
- **PyDub & static-ffmpeg**：跨平台音频剪辑与格式转换
- **RapidFuzz**：高效的文本模糊匹配算法

---
Powered by Iris AI Education Series.
