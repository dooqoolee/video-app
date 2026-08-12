import streamlit as st
import requests
from pathlib import Path
import subprocess
from PIL import Image
import io

st.set_page_config(page_title="AI 영상 생성기", layout="wide")
st.title("🎬 AI 영상 생성기")

# Sidebar에서 API 키 입력
st.sidebar.title("⚙️ 설정")
unsplash_key = st.sidebar.text_input("Unsplash API 키:", type="password")

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
        if not unsplash_key:
            st.error("❌ Unsplash API 키를 입력하세요!")
        elif all(scene_topics.values()):
            st.info("📸 이미지 다운로드 중...")
            
            temp_dir = Path("temp_images")
            temp_dir.mkdir(exist_ok=True)
            
            # Unsplash에서 이미지 다운로드
            success_count = 0
            for i, topic in scene_topics.items():
                try:
                    # Unsplash API 호출
                    url = "https://api.unsplash.com/photos/random"
                    params = {
                        "query": topic,
                        "client_id": unsplash_key,
                        "w": 1280,
                        "h": 720
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        image_url = response.json()["urls"]["full"]
                        
                        # 이미지 다운로드
                        img_response = requests.get(image_url, timeout=10)
                        img = Image.open(io.BytesIO(img_response.content))
                        
                        # 1280x720으로 리사이징
                        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                        img.save(temp_dir / f"scene_{i}.jpg")
                        
                        st.success(f"✅ 장면 {i+1} (주제: {topic}) 완료")
                        success_count += 1
                    else:
                        st.error(f"❌ 장면 {i+1} 실패: API 오류")
                
                except Exception as e:
                    st.error(f"❌ 장면 {i+1} 오류: {str(e)}")
            
            if success_count == len(scenes):
