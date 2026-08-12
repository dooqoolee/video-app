import streamlit as st
from pathlib import Path
import subprocess
from PIL import Image
import io

st.set_page_config(page_title="AI 영상 생성기", layout="wide")
st.title("🎬 AI 영상 생성기")
st.write("스크립트를 입력하고 영상을 생성합니다!")

st.subheader("📝 Step 1: 스크립트 입력")
script = st.text_area("각 장면의 스크립트를 줄 단위로 입력하세요:", 
                      placeholder="예시:\n좋은 아침입니다\n저는 디자이너입니다", 
                      height=150)

if script:
    scenes = [line.strip() for line in script.split('\n') if line.strip()]
    
    st.subheader(f"🎨 Step 2: 각 장면의 주제 입력 ({len(scenes)}개 장면)")
    
    scene_topics = {}
    cols = st.columns(2)
    
    for i, scene in enumerate(scenes):
        col = cols[i % 2]
        with col:
            st.write(f"**장면 {i+1}: {scene}**")
            topic = st.text_input(f"주제 (장면 {i+1}):", 
                                 key=f"topic_{i}",
                                 placeholder="예: 사람")
            scene_topics[i] = topic
    
    if st.button("🎥 영상 생성하기"):
        if all(scene_topics.values()):
            st.info("📸 이미지 준비 중...")
            
            temp_dir = Path("temp_images")
            temp_dir.mkdir(exist_ok=True)
            
            # 더미 이미지 생성
            for i in range(len(scenes)):
                img = Image.new('RGB', (1280, 720), color=(50, 100, 150))
                img.save(temp_dir / f"scene_{i}.jpg")
                st.success(f"✅ 장면 {i+1} 준비 완료")
            
            st.info("🎬 영상 생성 중...")
            
            try:
                output_video = "output.mp4"
                cmd = [
                    "ffmpeg",
                    "-framerate", "1/3",
                    "-pattern_type", "glob",
                    "-i", str(temp_dir / "scene_*.jpg"),
                    "-vf", "scale=1280:720",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    output_video,
                    "-y"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    st.success("✅ 영상 생성 완료!")
                    with open(output_video, "rb") as f:
                        st.download_button(
                            label="📥 영상 다운로드",
                            data=f.read(),
                            file_name="output.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error(f"오류: {result.stderr}")
            except Exception as e:
                st.error(f"❌ {str(e)}")
        else:
            st.error("❌ 모든 주제를 입력하세요!")
