import streamlit as st
import os
from pathlib import Path
import subprocess

st.set_page_config(page_title="AI 영상 생성기", layout="wide")
st.title("🎬 AI 영상 생성기")
st.write("스크립트를 입력하고 각 장면의 이미지를 검색하면 자동으로 영상을 만들어드립니다!")

st.sidebar.title("⚙️ 설정")
st.sidebar.info("🔧 현재 API 연결 테스트 중입니다. 이미지는 임시로 표시됩니다.")

st.subheader("📝 Step 1: 스크립트 입력")
script = st.text_area("각 장면의 스크립트를 줄 단위로 입력하세요:", 
                      placeholder="예시:\n좋은 아침입니다\n저는 디자이너입니다\n프로젝트를 소개하겠습니다", 
                      height=150)

if script:
    scenes = [line.strip() for line in script.split('\n') if line.strip()]
    
    st.subheader(f"🎨 Step 2: 각 장면의 이미지 주제 입력 ({len(scenes)}개 장면)")
    
    scene_images = {}
    cols = st.columns(2)
    
    for i, scene in enumerate(scenes):
        col = cols[i % 2]
        with col:
            st.write(f"**장면 {i+1}: {scene}**")
            topic = st.text_input(f"이미지 검색 주제 (장면 {i+1}):", 
                                 key=f"topic_{i}",
                                 placeholder="예: 사람, 회의, 기술 등")
            scene_images[i] = topic
    
    if st.button("🎥 영상 생성하기", key="generate_btn"):
        if all(scene_images.values()):
            st.info("📥 이미지를 준비 중입니다...")
            
            temp_dir = Path("temp_images")
            temp_dir.mkdir(exist_ok=True)
            
            for i, (scene_idx, topic) in enumerate(scene_images.items()):
                st.success(f"✅ 장면 {i+1}: '{topic}' 준비 완료")
            
            st.info("🎞️ 영상을 생성 중입니다...")
            
            try:
                output_video = "output.mp4"
                
                cmd = [
                    "ffmpeg",
                    "-f", "lavfi",
                    "-i", f"color=c=blue:s=1280x720:d={3*len(scenes)}",
                    "-vf", "drawtext=text='영상 생성 중':fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2",
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
                    st.error(f"영상 생성 오류: {result.stderr}")
            
            except Exception as e:
                st.error(f"❌ 영상 생성 오류: {str(e)}")
        else:
            st.error("❌ 모든 장면의 이미지 주제를 입력해주세요!")
