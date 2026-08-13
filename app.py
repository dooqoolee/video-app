import streamlit as st
import requests
import os
from pathlib import Path
from PIL import Image
import io

st.set_page_config(page_title="AI 영상 생성기", layout="wide")
st.title("🎬 AI 영상 생성기")

st.sidebar.title("⚙️ 설정")
unsplash_key = st.sidebar.text_input("Unsplash API 키:", type="password")

st.write("스크립트를 입력하고 영상을 생성합니다!")
st.subheader("📝 Step 1: 스크립트 입력")

script = st.text_area("각 장면의 스크립트를 줄 단위로 입력하세요:", 
                      placeholder="예시:\n좋은 아침입니다\n저는 디자이너입니다", 
                      height=150)

if script:
    scenes = [line.strip() for line in script.split('\n') if line.strip()]
    
    st.subheader(f"🎨 Step 2: 각 장면의 주제 및 시간 입력 ({len(scenes)}개 장면)")
    
    scene_data = {}
    cols = st.columns(2)
    
    for i, scene in enumerate(scenes):
        col = cols[i % 2]
        with col:
            st.write(f"**장면 {i+1}: {scene}**")
            topic = st.text_input(f"주제 (장면 {i+1}):", 
                                 key=f"topic_{i}",
                                 placeholder="예: 사람")
            duration = st.number_input(f"재생시간(초) (장면 {i+1}):", 
                                      key=f"duration_{i}",
                                      min_value=1, value=3)
            scene_data[i] = {"topic": topic, "duration": duration}
    
    if st.button("🎥 영상 생성하기"):
        if not unsplash_key:
            st.error("❌ Unsplash API 키를 입력하세요!")
        elif all(d["topic"] for d in scene_data.values()):
            st.info("📸 이미지 다운로드 중...")
            
            temp_dir = Path(os.getcwd()) / "temp_images"
            temp_dir.mkdir(exist_ok=True)
            
            selected_images = {}
            
            for i, data in scene_data.items():
                topic = data["topic"]
                st.subheader(f"장면 {i+1} - '{topic}' 이미지 선택")
                
                try:
                    image_options = []
                    image_urls = []
                    
                    for j in range(5):
                        url = "https://api.unsplash.com/photos/random"
                        params = {
                            "query": topic,
                            "client_id": unsplash_key,
                            "orientation": "landscape",
                            "w": 1280,
                            "h": 720
                        }
                        
                        response = requests.get(url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            img_url = response.json()["urls"]["small"]
                            image_urls.append(response.json()["urls"]["full"])
                            image_options.append(img_url)
                    
                    if image_options:
                        cols = st.columns(5)
                        selected_idx = None
                        
                        for idx, col in enumerate(cols):
                            with col:
                                st.image(image_options[idx], use_container_width=True)
                                if st.button(f"선택 {idx+1}", key=f"select_{i}_{idx}"):
                                    selected_idx = idx
                        
                        if selected_idx is not None:
                            img_response = requests.get(image_urls[selected_idx], timeout=10)
                            img = Image.open(io.BytesIO(img_response.content))
                            img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                            img.save(temp_dir / f"scene_{i}.jpg")
                            selected_images[i] = True
                            st.success(f"✅ 장면 {i+1} 이미지 선택 완료")
                    else:
                        st.error(f"❌ 장면 {i+1} 이미지 로드 실패")
                
                except Exception as e:
                    st.error(f"❌ 장면 {i+1} 오류: {str(e)}")
            
            if len(selected_images) == len(scenes):
                st.info("🎬 영상 생성 중...")
                try:
                    import imageio
                    output_video = "output.mp4"
                    
                    images = []
                    
                    for i in range(len(scenes)):
                        img_path = temp_dir / f"scene_{i}.jpg"
                        img = imageio.imread(str(img_path))
                        duration = scene_data[i]["duration"]
                        
                        for _ in range(duration * 3):
                            images.append(img)
                    
                    imageio.mimsave(output_video, images, fps=1/3)
                    
                    st.success("✅ 영상 생성 완료!")
                    with open(output_video, "rb") as f:
                        st.download_button(
                            label="📥 영상 다운로드",
                            data=f.read(),
                            file_name="output.mp4",
                            mime="video/mp4"
                        )
                except Exception as e:
                    st.error(f"❌ {str(e)}")
            else:
                st.error("❌ 모든 장면의 이미지를 선택하세요")
        else:
            st.error("❌ 모든 주제를 입력하세요!")
