# Iris Audio Cutter - 批量版

Iris Audio Cutter 是一款强大的音频剪辑工具，能够根据文本内容在音频中查找并自动剪辑相应片段。

## 功能特点

- **批量处理**：支持一次上传多个音频文件进行批量处理
- **文本驱动剪辑**：输入想要查找的文本，自动定位并剪辑相应的音频片段
- **Whisper语音识别**：使用OpenAI Whisper模型进行高精度语音识别和时间戳定位
- **模糊匹配**：支持模糊文本匹配，即使音频中的语音不够清晰也能准确找到所需片段
- **灵活配置**：可调整Whisper模型大小、匹配阈值、前后静音填充等参数

## 技术栈

- **Streamlit**：构建交互式Web界面
- **Faster-Whisper**：高效的语音识别模型推理
- **PyDub**：音频处理和剪辑
- **RapidFuzz**：文本相似度匹配算法

## 安装与使用

### 本地运行

1. 克隆项目
```bash
git clone https://github.com/fayeiris999-jpg/Iris-Audio-Cutter.git
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
streamlit run streamlit_app.py
```

### 配置选项

- **Whisper模型**：tiny, base, small, medium, large-v3（模型越大越准确但速度越慢）
- **前后填充**：为剪辑的音频片段添加前后静音
- **匹配阈值**：设置文本匹配的最低相似度分数

## 应用场景

- 教育培训：快速提取课程中的重点讲解片段
- 播客制作：自动剪辑访谈中的精彩回答
- 会议记录：提取重要决策相关的发言内容
- 内容创作：快速从长音频中提取可用素材