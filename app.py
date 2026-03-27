import streamlit as st
import numpy as np
from PIL import Image
import os
from ultralytics import YOLO

# Must be the first Streamlit command
st.set_page_config(
    page_title="SAR Ship Detection | AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS FOR PREMIUM UI ─────────────────────────────
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers & Text */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-weight: 700;
    }
    
    .stMarkdown p {
        font-size: 1.1rem;
        color: #8b949e;
    }
    
    /* Styling for glassmorphism card */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 24px;
    }
    
    /* Metrics block styling */
    div[data-testid="stMetricValue"] {
        color: #3fb950 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Upload Box overrides */
    div[data-testid="stFileUploadDropzone"] {
        border-radius: 12px;
        border: 2px dashed #58a6ff;
        background-color: rgba(88, 166, 255, 0.05);
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(88, 166, 255, 0.1);
        border-color: #79c0ff;
    }
    
    hr {
        border-color: rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# ── HEADER SECTION ─────────────────────────────
st.markdown("""
<div class="glass-card">
    <h1 style='text-align: center; margin-bottom: 0px;'>🛰️ SAR Ship Detection Engine</h1>
    <p style='text-align: center; margin-top: 10px; color: #8b949e;'>
        Advanced Synthetic Aperture Radar (SAR) object detection powered by YOLOv8.
    </p>
</div>
""", unsafe_allow_html=True)


# ── MODEL LOADING & ROBUSTNESS ────
@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")

    if not os.path.exists(MODEL_PATH):
        # Fallback to the root if not inside model/
        ROOT_MODEL_PATH = os.path.join(BASE_DIR, "yolov8s.pt")
        if os.path.exists(ROOT_MODEL_PATH):
            MODEL_PATH = ROOT_MODEL_PATH
        else:
            return None, f"Model not found at: {MODEL_PATH} or {ROOT_MODEL_PATH}"
            
    # Check if the file is a Git LFS pointer (typically less than 1KB)
    if os.path.getsize(MODEL_PATH) < 1024:
        # If it's too small, it's definitely an LFS pointer, not a YOLO weights file
        return None, (f"Model file '{MODEL_PATH}' seems to be a Git LFS text pointer! "
                      "Please ensure you have configured Git LFS when pushing to GitHub, "
                      "or manually download the required .pt file and place it in the application folder.")

    try:
        model = YOLO(MODEL_PATH)
        return model, "Success"
    except Exception as e:
        return None, f"Error loading model: {e}"

model, model_status = load_model()

# ── SIDEBAR CONFIGURATION ─────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3256/3256038.png", width=100)
    st.markdown("## ⚙️ Configuration")
    
    confidence_threshold = st.slider(
        "Confidence Threshold", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.35, 
        step=0.05,
        help="Adjust the minimum confidence score for a ship to be detected."
    )
    
    st.markdown("---")
    st.markdown("## 🩺 System Status")
    
    if model is not None:
        st.success("✅ Model: Loaded & Ready")
        st.info("🧠 Engine: YOLOv8")
    else:
        st.error(f"❌ Model Error")
        st.error(model_status)
        st.markdown("**How to fix for Deployment:**")
        st.markdown("If deploying from GitHub, ensure `.gitattributes` tracks `*.pt` files. We already added it to your repo!\n\nJust push the changes.")

    st.markdown("<br><br><br><br><br><p style='text-align: center; color: #484f58; font-size: 0.8rem;'>SAR Engine v2.0 Platform</p>", unsafe_allow_html=True)


# ── MAIN APPLICATION ───────────────────────────
if model is None:
    st.warning("⚠️ The application cannot process images without a valid model.")
    st.stop()

st.markdown("### 📤 Upload Satellite Imagery")
uploaded_file = st.file_uploader(
    "Drag and drop SAR imagery here",
    type=["png", "jpg", "jpeg", "tif", "tiff"],
    label_visibility="collapsed"
)

if uploaded_file is not None:
    # Read the image
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    st.markdown("---")
    
    # Process the image
    with st.spinner("🚀 Analyzing SAR imagery for vessels..."):
        results = model.predict(img_np, conf=confidence_threshold)
    
    result = results[0]
    
    # Extract bounding boxes & metrics
    num_detected = len(result.boxes)
    confidences = [float(box.conf[0]) for box in result.boxes]
    avg_conf = np.mean(confidences) if num_detected > 0 else 0.0
    max_conf = np.max(confidences) if num_detected > 0 else 0.0
    
    # Draw boxes
    annotated = result.plot()
    
    # Layout using Streamlit columns
    st.markdown("### 📊 Detection Results")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Detected Vessels", value=num_detected)
    with col2:
        st.metric(label="Average Confidence", value=f"{avg_conf * 100:.1f}%")
    with col3:
        st.metric(label="Highest Confidence", value=f"{max_conf * 100:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Image Display
    img_col1, img_col2 = st.columns(2)
    
    with img_col1:
        st.markdown("<h4 style='text-align: center; color: #c9d1d9;'>Original Image</h4>", unsafe_allow_html=True)
        st.image(image, use_container_width=True)
        
    with img_col2:
        st.markdown("<h4 style='text-align: center; color: #58a6ff;'>Analyzed Output</h4>", unsafe_allow_html=True)
        # Convert BGR back to RGB for Streamlit displaying correctly
        st.image(annotated[:, :, ::-1], use_container_width=True)
        
    # Detailed Data table if ships are detected
    if num_detected > 0:
        with st.expander("🔍 View Detailed Vessel Logs", expanded=False):
            log_data = []
            for i, box in enumerate(result.boxes):
                c = float(box.conf[0])
                log_data.append({"Vessel ID": f"SHP-{i+1000}", "Confidence": f"{c:.3f}"})
            st.table(log_data)
else:
    # Placeholder when no image is uploaded
    st.info("💡 **Awaiting Input:** Upload a Synthetic Aperture Radar (SAR) image to begin analysis.")