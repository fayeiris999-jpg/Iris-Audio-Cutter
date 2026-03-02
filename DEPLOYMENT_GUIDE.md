# Iris Audio Cutter Streamlit Cloud 部署指南

## 部署到Streamlit Cloud

这是一个关于如何将 Iris Audio Cutter 部署到 Streamlit Cloud 的指南。

### 项目结构

```
Iris Audio Cutter/
├── audio_cutter.py          # 核心音频处理逻辑
├── streamlit_app.py         # 主Streamlit应用入口
├── requirements.txt         # 依赖包列表
├── README.md                # 项目说明文档
└── .streamlit/
    └── config.toml          # Streamlit配置文件
```

### 部署步骤

1. **准备GitHub仓库**：
   - 将项目上传到GitHub或其他Git平台
   - 确保包含所有必要的文件

2. **访问Streamlit Cloud**：
   - 访问 https://streamlit.io/cloud
   - 登录并连接您的GitHub账户

3. **创建应用**：
   - 点击"New app"按钮
   - 选择您的仓库
   - 选择分支（通常是main或master）
   - 设置主文件路径为 `streamlit_app.py`
   - 点击"Deploy"按钮

### 注意事项

- Streamlit Cloud 可能需要几分钟时间来构建和部署应用
- 资源有限，大型Whisper模型（如large-v3）可能运行较慢或失败
- 推荐使用较小的模型（tiny或base）以获得更好的性能体验
- 应用在不活动一段时间后可能会进入睡眠状态，首次唤醒可能稍慢

### 依赖项说明

- `faster-whisper`: 高效的语音识别模型
- `pydub`: 音频处理和剪辑
- `rapidfuzz`: 文本相似度匹配
- `streamlit`: Web界面框架
- `static-ffmpeg`: FFmpeg静态链接库，用于音频处理

### 故障排除

如果应用部署失败，请检查：
1. requirements.txt 中的依赖项是否全部正确
2. streamlit_app.py 是否可以直接运行
3. 所有必要的文件是否都包含在仓库中