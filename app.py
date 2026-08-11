import streamlit as st
import requests
import os
from pathlib import Path
import json
from PIL import Image
import io

# 페이지 설정
st.set_page_config(page_title="AI 영상 생성기", layout="wide")
st.title("🎬 AI 영상 생성기")
st.write("스크립트를 입력하고 각 장면의 이미지를 검색하면 자동으로 영상을 만들어드립니다!")

# Pexels API 키 입력
st.sidebar.title("⚙️ 설정")
pexels_api_key = st.sidebar.text_input("Pexels API 키:", type="password")

if not pexels_api_key:
    st.warning("⚠️ 왼쪽 사이드바에서 Pexels API 키를 입력하세요!")
    st.stop()

# 메인 폼
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
    
    # 영상 생성 버튼
    if st.button("🎥 영상 생성하기", key="generate_btn"):
        if all(scene_images.values()):
            st.info("📥 이미지를 다운로드 중입니다...")
            
            # 임시 폴더 생성
            temp_dir = Path("temp_images")
            temp_dir.mkdir(exist_ok=True)
            
            image_paths = []
            
            # 각 장면의 이미지 다운로드
            for i, (scene_idx, topic) in enumerate(scene_images.items()):
                try:
                    # Pexels API로 이미지 검색
                    headers = {"Authorization": pexels_api_key}
                    response = requests.get(
                        "https://api.pexels.com/v1/search",
                        headers=headers,
                        params={"query": topic, "per_page": 1}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data["photos"]:
                            photo_url = data["photos"][0]["src"]["large"]
                            
                            # 이미지 다운로드
                            img_response = requests.get(photo_url)
                            img_path = temp_dir / f"scene_{i}.jpg"
                            
                            with open(img_path, 'wb') as f:
                                f.write(img_response.content)
                            
                            image_paths.append(img_path)
                            st.success(f"✅ 장면 {i+1} 이미지 다운로드 완료")
                        else:
                            st.warning(f"⚠️ 장면 {i+1}: '{topic}' 관련 이미지를 찾을 수 없습니다")
                    else:
                        st.error(f"❌ API 오류 (장면 {i+1}): 상태 코드 {response.status_code}")
                
                except Exception as e:
                    st.error(f"❌ 장면 {i+1} 오류: {str(e)}")
            
            # 영상 생성 (FFmpeg 사용)
            if image_paths:
                st.info("🎞️ 영상을 생성 중입니다...")
                
                try:
                    import subprocess
                    
                    # FFmpeg로 이미지들을 영상으로 변환
                    output_video = "output.mp4"
                    
                    # 간단한 영상 생성 (각 이미지 3초)
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
                        
                        # 다운로드 버튼
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