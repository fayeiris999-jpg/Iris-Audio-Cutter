import streamlit as st
import os
import tempfile
import logging
import zipfile
import io
import json
from audio_cutter import AudioTextCutter

# Set page configuration
st.set_page_config(
    page_title="Iris Audio Cutter - 提速版",
    page_icon="⚡",
    layout="wide"
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session state for audio data (stores transcriptions)
if 'audio_cache' not in st.session_state:
    st.session_state.audio_cache = {}

@st.cache_resource
def load_model(model_size, compute_type="int8"):
    """加载模型，默认使用int8加速"""
    return AudioTextCutter(model_size=model_size, compute_type=compute_type)

def transcribe_once(audio_path, model_size):
    """只转录一次，返回words"""
    cutter = load_model(model_size)
    words = cutter.transcribe_audio(audio_path)
    return words, cutter

def find_all_timestamps(words, text_queries, threshold):
    """从已转录的内容中查找所有文段的时间戳"""
    results = []
    for text in text_queries:
        ts = st.session_state.current_cutter.find_timestamps(words, text, threshold)
        results.append({
            'text': text,
            'timestamps': ts,
            'success': ts is not None
        })
    return results

def main():
    st.title("⚡ Iris Audio Cutter - 提速版")
    st.markdown("""
    **新功能**：一个音频可输入多段文段，同时生成多个剪辑 | **提速**：每个音频只转录一次
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ 设置")
        
        model_size = st.selectbox(
            "Whisper 模型",
            ["tiny", "base", "small", "medium", "large-v3"],
            index=0,  # 默认 tiny，最快
            help="tiny最快，large-v3最准"
        )
        
        padding = st.slider("前后padding (秒)", 0.0, 2.0, 0.3, 0.1)
        threshold = st.slider("匹配阈值", 50, 100, 75, 5)
        
        st.divider()
        st.markdown("**使用说明：**")
        st.markdown("""
        1. 上传音频
        2. 为每个音频添加多个文段
        3. 一键处理（每个音频只转录一次！）
        4. 下载ZIP
        """)

    # Step 1: 上传音频
    st.header("📁 步骤1：上传音频")
    uploaded_files = st.file_uploader(
        "选择音频文件", 
        type=["mp3", "wav", "m4a", "ogg"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"已上传 {len(uploaded_files)} 个文件")
        
        # Step 2: 为每个音频添加文段
        st.header("📝 步骤2：添加文段")
        
        # 初始化session state
        if 'audio_queries' not in st.session_state:
            st.session_state.audio_queries = {}
        
        # 清理已删除的文件
        current_files = {f.name for f in uploaded_files}
        st.session_state.audio_queries = {
            k: v for k, v in st.session_state.audio_queries.items() 
            if k in current_files
        }
        
        # 为每个音频创建输入区域
        for i, f in enumerate(uploaded_files):
            with st.expander(f"🎵 {f.name}", expanded=True):
                # 获取已有的文段列表
                if f.name not in st.session_state.audio_queries:
                    st.session_state.audio_queries[f.name] = [""]
                
                queries = st.session_state.audio_queries[f.name]
                
                # 显示文段输入
                for j, q in enumerate(queries):
                    col1, col2 = st.columns([9, 1])
                    with col1:
                        st.session_state.audio_queries[f.name][j] = st.text_input(
                            f"文段 {j+1}", 
                            value=q, 
                            key=f"q_{i}_{j}",
                            placeholder="输入要截取的文本"
                        )
                    with col2:
                        if st.button("🗑️", key=f"del_{i}_{j}") and len(queries) > 1:
                            st.session_state.audio_queries[f.name].pop(j)
                            st.rerun()
                
                # 添加新文段按钮
                if st.button(f"+ 添加文段", key=f"add_{i}"):
                    st.session_state.audio_queries[f.name].append("")
                    st.rerun()
                
                # 显示预览
                valid_queries = [q for q in st.session_state.audio_queries[f.name] if q.strip()]
                st.caption(f"已添加 {len(valid_queries)} 个文段")
        
        # Step 3: 处理
        st.header("🚀 步骤3：一键处理")
        
        if st.button("⚡ 开始处理", type="primary", use_container_width=True):
            # 收集有效任务
            tasks = []
            for f in uploaded_files:
                queries = st.session_state.audio_queries.get(f.name, [])
                valid_queries = [q for q in queries if q.strip()]
                if valid_queries:
                    tasks.append({'file': f, 'queries': valid_queries})
            
            if not tasks:
                st.error("请至少添加一个文段！")
                return
            
            # 处理
            all_results = []
            progress_bar = st.progress(0, text="准备中...")
            status = st.empty()
            
            for idx, task in enumerate(tasks):
                f = task['file']
                queries = task['queries']
                status.text(f"🔄 处理 {idx+1}/{len(tasks)}: {f.name}")
                
                try:
                    # 保存临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
                        tmp.write(f.getvalue())
                        tmp_path = tmp.name
                    
                    try:
                        # ⭐ 关键优化：只转录一次！
                        words, cutter = transcribe_once(tmp_path, model_size)
                        st.session_state.current_cutter = cutter
                        
                        # 查找所有文段
                        for j, query in enumerate(queries):
                            ts = cutter.find_timestamps(words, query, threshold)
                            
                            if ts:
                                start, end = ts
                                # 剪辑
                                output_name = f"{os.path.splitext(f.name)[0]}_第{j+1}段_{start:.2f}_{end:.2f}.wav"
                                output_path = os.path.join(tempfile.gettempdir(), output_name)
                                cutter.clip_audio(tmp_path, start, end, output_path, padding=padding)
                                
                                all_results.append({
                                    'audio': f.name,
                                    'text': query,
                                    'success': True,
                                    'output_path': output_path,
                                    'output_name': output_name
                                })
                            else:
                                all_results.append({
                                    'audio': f.name,
                                    'text': query,
                                    'success': False,
                                    'error': f"未找到文本: {query}"
                                })
                    finally:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                            
                except Exception as e:
                    all_results.append({
                        'audio': f.name,
                        'text': queries[0] if queries else "",
                        'success': False,
                        'error': str(e)
                    })
                
                progress_bar.progress((idx + 1) / len(tasks))
            
            progress_bar.empty()
            status.text("✅ 处理完成！")
            
            # Step 4: 下载
            st.header("📥 步骤4：下载结果")
            
            success = [r for r in all_results if r['success']]
            failed = [r for r in all_results if not r['success']]
            
            col1, col2 = st.columns(2)
            col1.metric("成功", f"{len(success)}/{len(all_results)}")
            col2.metric("失败", len(failed))
            
            if failed:
                with st.expander("❌ 查看失败详情"):
                    for r in failed:
                        st.write(f"• {r['audio']} - {r.get('error', '未知错误')}")
            
            if success:
                # 创建ZIP（带文件夹结构）
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for r in success:
                        if os.path.exists(r['output_path']):
                            # 按音频名创建文件夹
                            folder = os.path.splitext(r['audio'])[0]
                            zf.write(r['output_path'], f"{folder}/{r['output_name']}")
                            os.unlink(r['output_path'])
                
                zip_buffer.seek(0)
                
                st.download_button(
                    "📦 下载全部结果 (ZIP)",
                    zip_buffer.getvalue(),
                    "iris_audio_clips.zip",
                    "application/zip",
                    type="primary"
                )
                st.balloons()
    
    else:
        st.info("👆 请先上传音频文件")

if __name__ == "__main__":
    main()