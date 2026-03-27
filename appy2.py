import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import time
import os
import random

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SARShield · Ship Detection",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg-deep:    #050a12;
    --bg-panel:   #0a1628;
    --bg-card:    #0d1f3c;
    --accent:     #00d4ff;
    --accent2:    #00ff9d;
    --warn:       #ff6b35;
    --text:       #c8e0ff;
    --text-dim:   #4a6a99;
    --border:     rgba(0,212,255,0.18);
    --glow:       0 0 20px rgba(0,212,255,0.25);
}

/* ── Global Reset ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg-deep) !important;
    color: var(--text) !important;
    font-family: 'Exo 2', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Hero Header ── */
.hero-header {
    position: relative;
    padding: 2rem 2.5rem 1.5rem;
    background: linear-gradient(135deg, #050a12 0%, #071428 50%, #050a12 100%);
    border-bottom: 1px solid var(--border);
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -20%;
    width: 140%; height: 200%;
    background: radial-gradient(ellipse at 30% 50%, rgba(0,212,255,0.07) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 50%, rgba(0,255,157,0.05) 0%, transparent 60%);
    pointer-events: none;
}
.hero-scanline {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scanline 3s ease-in-out infinite;
}
@keyframes scanline {
    0%   { transform: translateX(-100%); opacity: 0; }
    50%  { opacity: 1; }
    100% { transform: translateX(100%); opacity: 0; }
}
.hero-title {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 3.2rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent2) 60%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
    line-height: 1 !important;
    text-transform: uppercase;
}
.hero-sub {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.82rem !important;
    color: var(--text-dim) !important;
    letter-spacing: 0.2em;
    margin-top: 0.4rem;
    text-transform: uppercase;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.35);
    border-radius: 3px;
    padding: 2px 10px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--accent);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.6rem;
}

/* ── Metric Cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.metric-card:hover { border-color: rgba(0,212,255,0.4); }
.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.metric-unit {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-dim);
    margin-top: 0.2rem;
}

/* ── Upload Zone ── */
.upload-zone {
    border: 2px dashed rgba(0,212,255,0.3);
    border-radius: 8px;
    padding: 2.5rem;
    text-align: center;
    background: rgba(0,212,255,0.02);
    transition: all 0.3s;
    cursor: pointer;
}
.upload-zone:hover {
    border-color: rgba(0,212,255,0.6);
    background: rgba(0,212,255,0.05);
}
.upload-icon {
    font-size: 3rem;
    margin-bottom: 0.8rem;
}
.upload-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    color: var(--text-dim);
    letter-spacing: 0.1em;
}

/* ── Section Headers ── */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-dim);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    border-left: 2px solid var(--accent);
    padding-left: 0.8rem;
    margin-bottom: 1rem;
}

/* ── Detection Result Panel ── */
.result-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    position: relative;
}
.result-panel::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent2), transparent);
}

/* ── Alert Box ── */
.alert-detected {
    background: rgba(255,107,53,0.1);
    border: 1px solid rgba(255,107,53,0.5);
    border-radius: 6px;
    padding: 0.8rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: var(--warn);
    letter-spacing: 0.1em;
    animation: pulse-border 2s ease-in-out infinite;
}
.alert-clear {
    background: rgba(0,255,157,0.08);
    border: 1px solid rgba(0,255,157,0.4);
    border-radius: 6px;
    padding: 0.8rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: var(--accent2);
    letter-spacing: 0.1em;
}
@keyframes pulse-border {
    0%, 100% { border-color: rgba(255,107,53,0.5); }
    50%       { border-color: rgba(255,107,53,1); }
}

/* ── Detection Table ── */
.det-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
}
.det-table th {
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-size: 0.65rem;
    padding: 0.5rem 0.8rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
}
.det-table td {
    padding: 0.5rem 0.8rem;
    color: var(--text);
    border-bottom: 1px solid rgba(0,212,255,0.06);
}
.det-table tr:hover td { background: rgba(0,212,255,0.04); }
.conf-high { color: var(--accent2); }
.conf-med  { color: var(--accent); }
.conf-low  { color: var(--warn); }

/* ── Progress / Scan ── */
.scan-line {
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent2), transparent);
    border-radius: 2px;
    animation: scan-anim 1.5s ease-in-out;
}
@keyframes scan-anim {
    0%   { width: 0%; opacity: 0; }
    20%  { opacity: 1; }
    100% { width: 100%; opacity: 0; }
}

/* ── Sidebar ── */
.sidebar-section {
    background: rgba(0,212,255,0.04);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.sidebar-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* ── Streamlit Overrides ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,255,157,0.1)) !important;
    border: 1px solid rgba(0,212,255,0.5) !important;
    border-radius: 4px !important;
    color: var(--accent) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.25), rgba(0,255,157,0.18)) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 15px rgba(0,212,255,0.3) !important;
    transform: translateY(-1px) !important;
}
.stSlider label, .stSelectbox label, .stFileUploader label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    color: var(--text-dim) !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent) !important;
}
[data-testid="stFileUploader"] {
    border: 1px dashed rgba(0,212,255,0.3) !important;
    border-radius: 8px !important;
    background: rgba(0,212,255,0.02) !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,212,255,0.6) !important;
}
div[data-testid="stImage"] img {
    border-radius: 6px;
    border: 1px solid var(--border);
}
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}
h1, h2, h3 { color: var(--text) !important; font-family: 'Rajdhani', sans-serif !important; }
p, li { color: var(--text) !important; }

/* ── Radar Widget ── */
.radar-container {
    display: flex;
    justify-content: center;
    padding: 0.5rem 0;
}

/* ── Status Dot ── */
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent2);
    box-shadow: 0 0 8px var(--accent2);
    animation: blink 2s ease-in-out infinite;
    margin-right: 6px;
    vertical-align: middle;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── Hide Streamlit Cruft ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ─── MODEL LOADER ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    """Load YOLOv8 model — cached so it only loads once."""
    try:
        from ultralytics import YOLO
        model_path = "model/best.pt"
        if not os.path.exists(model_path):
            return None, "⚠️ model/best.pt not found. Place your trained model in the model/ folder."
        model = YOLO(model_path)
        return model, None
    except ImportError:
        return None, "ultralytics not installed. Run: pip install ultralytics"
    except Exception as e:
        return None, str(e)


def run_detection(image_pil, model, conf_threshold, iou_threshold):
    """Run YOLOv8 inference and return annotated image + detection list."""
    img_array = np.array(image_pil)
    orig_h, orig_w = img_array.shape[:2]

    results = model.predict(
        img_array,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=False,
        imgsz=640,
    )
    result = results[0]

    # Use YOLO's own plot() — handles all scaling internally, no manual coord math
    annotated_bgr = result.plot(line_width=2, font_size=10, conf=True, labels=True)
    annotated = Image.fromarray(annotated_bgr[:, :, ::-1])  # BGR → RGB

    # Collect detection metadata using normalized coords (xyxyn) → scale to original
    detections = []
    for i, box in enumerate(result.boxes):
        xn1, yn1, xn2, yn2 = box.xyxyn[0].tolist()
        x1, y1 = int(xn1 * orig_w), int(yn1 * orig_h)
        x2, y2 = int(xn2 * orig_w), int(yn2 * orig_h)
        conf     = float(box.conf[0])
        cls_id   = int(box.cls[0])
        cls_name = result.names.get(cls_id, "ship")
        detections.append({
            "id": i + 1,
            "class": cls_name,
            "confidence": conf,
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "width": x2 - x1,
            "height": y2 - y1,
        })

    return annotated, detections


def demo_detection(image_pil, conf_threshold):
    """Fallback demo when model isn't available — draws fake boxes."""
    import random
    w, h = image_pil.size
    annotated = image_pil.copy()
    draw = ImageDraw.Draw(annotated)
    detections = []

    n = random.randint(2, 5)
    for i in range(n):
        bw = random.randint(w // 12, w // 6)
        bh = random.randint(h // 12, h // 6)
        x1 = random.randint(0, w - bw)
        y1 = random.randint(0, h - bh)
        x2, y2 = x1 + bw, y1 + bh
        conf = random.uniform(conf_threshold, 0.98)
        color = (0, 255, 157) if conf >= 0.75 else (0, 212, 255) if conf >= 0.5 else (255, 107, 53)
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        label = f"#{i+1} SHIP {conf:.0%}"
        draw.rectangle([x1, y1 - 18, x1 + len(label)*7, y1], fill=(0, 0, 0))
        draw.text((x1 + 3, y1 - 16), label, fill=color)
        detections.append({"id": i+1, "class": "ship", "confidence": conf,
                            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                            "width": bw, "height": bh})
    return annotated, detections


# ─── SESSION STATE ───────────────────────────────────────────────────────────────
if "total_scans"      not in st.session_state: st.session_state.total_scans      = 0
if "total_ships"      not in st.session_state: st.session_state.total_ships      = 0
if "last_conf"        not in st.session_state: st.session_state.last_conf        = 0.0
if "history"          not in st.session_state: st.session_state.history          = []


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem;'>
        <div style='font-family:Rajdhani,sans-serif; font-size:1.6rem; font-weight:700;
                    background:linear-gradient(90deg,#00d4ff,#00ff9d);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    letter-spacing:0.15em;'>SARSHIELD</div>
        <div style='font-family:Share Tech Mono,monospace; font-size:0.6rem;
                    color:#4a6a99; letter-spacing:0.2em; margin-top:0.2rem;'>
            <span class='status-dot'></span> SYSTEM ONLINE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">⚙ Detection Parameters</div>', unsafe_allow_html=True)
    conf_thresh = st.slider("Confidence Threshold", 0.10, 0.95, 0.50, 0.05,
                            help="Minimum confidence score to report a detection")
    iou_thresh  = st.slider("IoU Threshold (NMS)", 0.10, 0.90, 0.45, 0.05,
                            help="Non-maximum suppression IoU cutoff")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🖼 Display Options</div>', unsafe_allow_html=True)
    show_original   = st.checkbox("Show Original Image", True)
    show_table      = st.checkbox("Show Detection Table", True)
    show_download   = st.checkbox("Enable Result Download", True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📡 Mission Info</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:Share Tech Mono,monospace; font-size:0.7rem; color:#4a6a99; line-height:1.8;'>
    MODEL &nbsp;· YOLOv8s<br>
    DATASET · SSDD (SAR)<br>
    TASK &nbsp;&nbsp;· Object Detection<br>
    FORMAT · YOLO Labels<br>
    AUG &nbsp;&nbsp;&nbsp;· SAR-Specific
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🗑 Clear Session"):
        st.session_state.total_scans = 0
        st.session_state.total_ships = 0
        st.session_state.last_conf   = 0.0
        st.session_state.history     = []
        st.rerun()


# ─── HERO HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-scanline"></div>
    <div class="hero-title">🛰 SARShield</div>
    <div class="hero-sub">Synthetic Aperture Radar · Maritime Intelligence System</div>
    <div class="hero-badge">⬡ YOLOv8s · Real-Time Ship Detection · SSDD Dataset</div>
</div>
""", unsafe_allow_html=True)


# ─── METRICS ROW ─────────────────────────────────────────────────────────────────
avg_conf = st.session_state.last_conf
st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">▸ Total Scans</div>
    <div class="metric-value">{st.session_state.total_scans:03d}</div>
    <div class="metric-unit">images processed</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">▸ Ships Detected</div>
    <div class="metric-value" style="color:var(--warn);">{st.session_state.total_ships:04d}</div>
    <div class="metric-unit">total detections</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">▸ Avg Confidence</div>
    <div class="metric-value" style="color:var(--accent2);">{avg_conf:.0%}</div>
    <div class="metric-unit">last run</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">▸ Conf Threshold</div>
    <div class="metric-value">{conf_thresh:.0%}</div>
    <div class="metric-unit">active setting</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── LOAD MODEL ──────────────────────────────────────────────────────────────────
model, model_error = load_model()

if model_error:
    st.warning(f"**Demo Mode Active** — {model_error}\n\nBounding boxes below are simulated for UI preview.")
    demo_mode = True
else:
    demo_mode = False
    st.markdown("""
    <div style='background:rgba(0,255,157,0.06); border:1px solid rgba(0,255,157,0.3);
                border-radius:6px; padding:0.6rem 1rem; font-family:Share Tech Mono,monospace;
                font-size:0.75rem; color:#00ff9d; letter-spacing:0.1em; margin-bottom:1rem;'>
        ✓ MODEL LOADED · YOLOv8s · model/best.pt
    </div>
    """, unsafe_allow_html=True)


# ─── UPLOAD ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">UPLOAD SAR IMAGERY</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drop SAR images here (PNG, JPG, TIFF)",
    type=["png", "jpg", "jpeg", "tif", "tiff"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if not uploaded_files:
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-icon">📡</div>
        <div class="upload-text">Awaiting SAR imagery · PNG / JPG / TIFF accepted</div>
        <div style='font-family:Share Tech Mono,monospace; font-size:0.65rem;
                    color:#2a4a70; margin-top:0.5rem; letter-spacing:0.15em;'>
            MULTI-IMAGE BATCH PROCESSING SUPPORTED
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style='font-family:Share Tech Mono,monospace; font-size:0.72rem; color:#4a6a99;
                margin-bottom:1rem; letter-spacing:0.12em;'>
        ▸ {len(uploaded_files)} FILE(S) QUEUED FOR ANALYSIS
    </div>
    """, unsafe_allow_html=True)

    run_btn = st.button("⚡  RUN DETECTION SCAN")

    if run_btn:
        all_detections = []

        for file_idx, uploaded_file in enumerate(uploaded_files):
            image_pil = Image.open(uploaded_file).convert("RGB")
            w, h = image_pil.size

            st.markdown(f"""
            <div class="section-header">
                SCANNING · {uploaded_file.name.upper()} ({w}×{h}px)
            </div>
            """, unsafe_allow_html=True)

            # Scan animation
            progress_bar = st.progress(0)
            status_text  = st.empty()
            steps = ["PREPROCESSING IMAGE", "RUNNING INFERENCE", "APPLYING NMS", "RENDERING RESULTS"]
            for s_idx, step in enumerate(steps):
                status_text.markdown(f"""
                <div style='font-family:Share Tech Mono,monospace; font-size:0.72rem;
                            color:#4a6a99; letter-spacing:0.15em;'>▷ {step}...</div>
                """, unsafe_allow_html=True)
                time.sleep(0.3)
                progress_bar.progress((s_idx + 1) / len(steps))

            progress_bar.empty()
            status_text.empty()

            # Run model
            if demo_mode:
                annotated_img, detections = demo_detection(image_pil, conf_thresh)
            else:
                annotated_img, detections = run_detection(image_pil, model, conf_thresh, iou_thresh)

            # Update session stats
            st.session_state.total_scans += 1
            st.session_state.total_ships += len(detections)
            if detections:
                st.session_state.last_conf = sum(d["confidence"] for d in detections) / len(detections)
            all_detections.extend(detections)

            # Alert
            if detections:
                st.markdown(f"""
                <div class="alert-detected">
                    ⚠ THREAT DETECTED — {len(detections)} VESSEL(S) IDENTIFIED IN SECTOR
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-clear">✓ SECTOR CLEAR — NO VESSELS DETECTED</div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Image display
            col_orig, col_result = st.columns(2) if show_original else (None, st.columns(1)[0])

            if show_original and col_orig:
                with col_orig:
                    st.markdown('<div class="section-header">ORIGINAL IMAGE</div>', unsafe_allow_html=True)
                    st.image(image_pil, use_container_width=True)

            with col_result:
                st.markdown('<div class="section-header">DETECTION RESULT</div>', unsafe_allow_html=True)
                st.image(annotated_img, use_container_width=True)

            # Detection table
            if show_table and detections:
                st.markdown('<div class="section-header">DETECTION LOG</div>', unsafe_allow_html=True)
                rows = ""
                for d in detections:
                    c = d["confidence"]
                    conf_class = "conf-high" if c >= 0.75 else "conf-med" if c >= 0.5 else "conf-low"
                    rows += f"""
                    <tr>
                        <td>#{d['id']:02d}</td>
                        <td>{d['class'].upper()}</td>
                        <td class="{conf_class}">{c:.1%}</td>
                        <td>{d['x1']},{d['y1']}</td>
                        <td>{d['x2']},{d['y2']}</td>
                        <td>{d['width']}×{d['height']}</td>
                    </tr>"""

                st.markdown(f"""
                <div class="result-panel">
                <table class="det-table">
                  <thead>
                    <tr>
                      <th>ID</th><th>Class</th><th>Confidence</th>
                      <th>Top-Left</th><th>Bottom-Right</th><th>Size (px)</th>
                    </tr>
                  </thead>
                  <tbody>{rows}</tbody>
                </table>
                </div>
                """, unsafe_allow_html=True)

            # Download button
            if show_download:
                buf = io.BytesIO()
                annotated_img.save(buf, format="PNG")
                st.download_button(
                    label="⬇  DOWNLOAD RESULT",
                    data=buf.getvalue(),
                    file_name=f"sarshield_result_{uploaded_file.name}",
                    mime="image/png",
                )

            st.markdown("<hr style='border-color:rgba(0,212,255,0.1);margin:2rem 0;'>",
                        unsafe_allow_html=True)

        # Session summary
        if len(uploaded_files) > 1:
            st.markdown('<div class="section-header">MISSION SUMMARY</div>', unsafe_allow_html=True)
            avg_conf_summary = f"{sum(d['confidence'] for d in all_detections)/len(all_detections):.1%}" if all_detections else "N/A"
            st.markdown(f"""
            <div class="result-panel">
              <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:1rem;'>
                <div>
                  <div class="metric-label">Files Scanned</div>
                  <div class="metric-value">{len(uploaded_files)}</div>
                </div>
                <div>
                  <div class="metric-label">Total Detections</div>
                  <div class="metric-value" style="color:var(--warn);">{len(all_detections)}</div>
                </div>
                <div>
                  <div class="metric-label">Avg Confidence</div>
                  <div class="metric-value" style="color:var(--accent2);">{avg_conf_summary}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ─── ABOUT SECTION ───────────────────────────────────────────────────────────────
with st.expander("ℹ️  About SARShield"):
    st.markdown("""
    **SARShield** is a real-time maritime intelligence system built on top of YOLOv8s, 
    trained on the **SSDD (SAR Ship Detection Dataset)**. It detects ships in 
    Synthetic Aperture Radar imagery — a critical tool for maritime surveillance, 
    border security, and environmental monitoring.

    **Key Features:**
    - 🛰 SAR-optimised preprocessing & augmentation
    - ⚡ YOLOv8s inference — fast enough for edge deployment
    - 📦 Batch processing of multiple images
    - 📊 Per-detection confidence scoring & bounding box metadata
    - ⬇️ Downloadable annotated results

    **How to use:**
    1. Upload one or more SAR images using the uploader above
    2. Adjust confidence / IoU thresholds in the sidebar
    3. Click **Run Detection Scan**
    4. Review results and download annotated images

    **Stack:** Python · Streamlit · Ultralytics YOLOv8 · Pillow
    """)