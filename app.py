import streamlit as st
import numpy as np
from PIL import Image
import io
import os
import zipfile
import csv
import time


os.system("pip uninstall -y opencv-python opencv-python-headless")
os.system("pip install opencv-python-headless==4.8.1.78")

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SARShield · Maritime SAR Analysis",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLES ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

:root {
    --bg:        #06090f;
    --surface:   #0c1220;
    --surface2:  #111a2e;
    --border:    rgba(56,189,248,0.12);
    --border2:   rgba(56,189,248,0.25);
    --sky:       #38bdf8;
    --emerald:   #34d399;
    --amber:     #fbbf24;
    --slate:     #94a3b8;
    --text:      #e2e8f0;
    --text-dim:  #64748b;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

.wordmark { font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800; letter-spacing:-0.01em; color:var(--text); }
.wordmark span { color:var(--sky); }

.page-title { font-family:'Syne',sans-serif; font-size:2.6rem; font-weight:800; letter-spacing:-0.03em; color:var(--text); line-height:1.1; margin:0; }
.page-sub { font-family:'Inter',sans-serif; font-size:0.88rem; color:var(--text-dim); margin-top:0.4rem; }

.divider { height:1px; background:var(--border); margin:1.5rem 0; }

.stats-row { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--border); border:1px solid var(--border); border-radius:10px; overflow:hidden; margin-bottom:2rem; }
.stat-cell { background:var(--surface); padding:1.1rem 1.4rem; }
.stat-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:var(--text-dim); letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.35rem; }
.stat-value { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:700; color:var(--text); line-height:1; }
.stat-value.sky { color:var(--sky); }
.stat-value.emerald { color:var(--emerald); }

.section-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:500; letter-spacing:0.18em; text-transform:uppercase; color:var(--text-dim); margin-bottom:0.75rem; }

.upload-hint { text-align:center; padding:3rem 1rem; border:1px dashed var(--border2); border-radius:10px; background:var(--surface); }
.upload-hint-icon { font-size:2.2rem; margin-bottom:0.6rem; }
.upload-hint-text { font-size:0.85rem; color:var(--text-dim); line-height:1.6; }

.result-card { background:var(--surface); border:1px solid var(--border); border-radius:10px; overflow:hidden; margin-bottom:2rem; }
.result-card-header { padding:1rem 1.4rem; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; }
.result-card-title { font-family:'Inter',sans-serif; font-size:0.82rem; font-weight:600; color:var(--text); }
.result-card-meta { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:var(--text-dim); }
.result-card-body { padding:1.2rem 1.4rem; }

.count-badge { display:inline-flex; align-items:center; gap:0.4rem; background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); border-radius:20px; padding:0.25rem 0.75rem; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--sky); }
.count-badge.zero { background:rgba(100,116,139,0.1); border-color:rgba(100,116,139,0.3); color:var(--text-dim); }

.det-table { width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace; font-size:0.72rem; }
.det-table th { font-size:0.6rem; font-weight:500; letter-spacing:0.12em; text-transform:uppercase; color:var(--text-dim); padding:0.5rem 0.8rem; border-bottom:1px solid var(--border); text-align:left; }
.det-table td { padding:0.55rem 0.8rem; color:var(--text); border-bottom:1px solid rgba(56,189,248,0.05); }
.det-table tr:last-child td { border-bottom:none; }
.det-table tr:hover td { background:rgba(56,189,248,0.03); }
.conf-pill { display:inline-block; padding:1px 8px; border-radius:10px; font-size:0.65rem; font-weight:500; }
.conf-high { background:rgba(52,211,153,0.12); color:#34d399; }
.conf-med  { background:rgba(56,189,248,0.12); color:#38bdf8; }
.conf-low  { background:rgba(251,191,36,0.12);  color:#fbbf24; }

.summary-bar { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--border); border:1px solid var(--border); border-radius:10px; overflow:hidden; margin-top:2rem; }
.summary-cell { background:var(--surface2); padding:1rem 1.2rem; text-align:center; }
.summary-num { font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:700; color:var(--sky); }
.summary-lbl { font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:var(--text-dim); letter-spacing:0.1em; text-transform:uppercase; margin-top:0.2rem; }

.nav-label { font-family:'JetBrains Mono',monospace; font-size:0.58rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--text-dim); padding:0.3rem 0; margin-top:1.2rem; margin-bottom:0.4rem; }

.stProgress > div > div { background:linear-gradient(90deg,var(--sky),var(--emerald)) !important; }

.stButton > button { background:var(--sky) !important; border:none !important; border-radius:7px !important; color:#06090f !important; font-family:'Inter',sans-serif !important; font-size:0.85rem !important; font-weight:600 !important; padding:0.65rem 1.5rem !important; width:100% !important; transition:opacity 0.2s !important; }
.stButton > button:hover { opacity:0.85 !important; }

[data-testid="stFileUploader"] section { background:var(--surface) !important; border:1px dashed var(--border2) !important; border-radius:10px !important; padding:1.2rem !important; }
[data-testid="stFileUploader"] section:hover { border-color:var(--sky) !important; }

div[data-testid="stImage"] img { border-radius:8px; border:1px solid var(--border); }
.stCheckbox label { color:var(--slate) !important; font-size:0.82rem !important; }
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility:hidden; display:none; }
[data-testid="stExpander"] { background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)


# ── MODEL ───────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
@st.cache_resource(show_spinner=False)
def load_model():
    try:
        from ultralytics import YOLO
        import os

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "model", "best.pt")

        if not os.path.exists(MODEL_PATH):
            st.error(f"Model not found at: {MODEL_PATH}")
            return None

        return YOLO(MODEL_PATH)

    except Exception as e:
        st.error(f"Model load error: {e}")
        return None

st.write("Current working dir:", os.getcwd())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
st.write("Base dir:", BASE_DIR)

st.write("Files in base:", os.listdir(BASE_DIR))

model_dir = os.path.join(BASE_DIR, "model")
if os.path.exists(model_dir):
    st.write("Model folder contents:", os.listdir(model_dir))
else:
    st.write("Model folder NOT FOUND")

def run_detection(image_pil, model):
    """
    Correct pipeline — avoids the coordinate-scaling bug that caused
    wrong box positions on Streamlit Cloud vs local:
      - Feed original image directly (no manual resize)
      - Use result.plot() for annotation (YOLO handles all scaling)
      - Use xyxyn (normalised coords) for table data
    """
    img_np = np.array(image_pil.convert("RGB"))
    orig_h, orig_w = img_np.shape[:2]

    results = model.predict(img_np, conf=0.35, iou=0.45, verbose=False)
    result  = results[0]

    ann_bgr   = result.plot(line_width=2, font_size=9, conf=True, labels=True)
    annotated = Image.fromarray(ann_bgr[:, :, ::-1])   # BGR → RGB

    detections = []
    for i, box in enumerate(result.boxes):
        xn1, yn1, xn2, yn2 = box.xyxyn[0].tolist()
        x1, y1 = int(xn1 * orig_w), int(yn1 * orig_h)
        x2, y2 = int(xn2 * orig_w), int(yn2 * orig_h)
        conf    = float(box.conf[0])
        cls_id  = int(box.cls[0])
        name    = result.names.get(cls_id, "ship")
        detections.append({
            "id": i + 1, "class": name, "confidence": conf,
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "width": x2 - x1, "height": y2 - y1,
        })
    return annotated, detections


def build_zip(all_results_with_images):
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        csv_rows = [["Image","Ship #","Class","Confidence","X1","Y1","X2","Y2","W","H"]]
        for filename, annotated_img, detections in all_results_with_images:
            img_buf = io.BytesIO()
            annotated_img.save(img_buf, format="PNG")
            zf.writestr(f"annotated/{filename}", img_buf.getvalue())
            for d in detections:
                csv_rows.append([filename, d["id"], d["class"], f"{d['confidence']:.4f}",
                                  d["x1"], d["y1"], d["x2"], d["y2"], d["width"], d["height"]])
        csv_buf = io.StringIO()
        csv.writer(csv_buf).writerows(csv_rows)
        zf.writestr("detections_report.csv", csv_buf.getvalue())
    zip_buf.seek(0)
    return zip_buf.read()


# ── SESSION STATE ────────────────────────────────────────────────────────────────
for k, v in [("scans", 0), ("ships", 0), ("avg_conf", 0.0)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── SIDEBAR ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.2rem 0 1.8rem;'>
        <div class='wordmark'>SAR<span>Shield</span></div>
        <div style='font-family:JetBrains Mono,monospace;font-size:0.6rem;
                    color:#1e3a5f;letter-spacing:0.15em;margin-top:0.3rem;'>
            MARITIME INTELLIGENCE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">Display</div>', unsafe_allow_html=True)
    show_original = st.checkbox("Show original image", value=True)
    show_table    = st.checkbox("Show detection table", value=True)

    st.markdown('<div class="nav-label">Export</div>', unsafe_allow_html=True)
    export_zip = st.checkbox("Bundle all results into ZIP", value=True)

    st.markdown('<div class="nav-label">Session</div>', unsafe_allow_html=True)
    if st.button("Reset session"):
        st.session_state.scans    = 0
        st.session_state.ships    = 0
        st.session_state.avg_conf = 0.0
        st.rerun()

    st.markdown("""
    <div style='margin-top:3rem;font-family:JetBrains Mono,monospace;
                font-size:0.58rem;color:#1e293b;line-height:2;'>
        YOLOv8s · SSDD Dataset<br>SAR Ship Detection
    </div>
    """, unsafe_allow_html=True)


# ── HEADER ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:2.5rem 0 0.5rem;'>
    <div class='page-title'>Maritime SAR<br>Ship Detection</div>
    <div class='page-sub'>Upload Synthetic Aperture Radar imagery to detect and analyse vessel presence.</div>
</div>
<div class='divider'></div>
""", unsafe_allow_html=True)

conf_display = f"{st.session_state.avg_conf:.0%}" if st.session_state.avg_conf > 0 else "—"
st.markdown(f"""
<div class='stats-row'>
    <div class='stat-cell'>
        <div class='stat-label'>Images Analysed</div>
        <div class='stat-value sky'>{st.session_state.scans:,}</div>
    </div>
    <div class='stat-cell'>
        <div class='stat-label'>Ships Detected</div>
        <div class='stat-value'>{st.session_state.ships:,}</div>
    </div>
    <div class='stat-cell'>
        <div class='stat-label'>Avg Confidence</div>
        <div class='stat-value emerald'>{conf_display}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── MODEL LOAD ───────────────────────────────────────────────────────────────────
model     = load_model()
demo_mode = model is None


# ── UPLOAD ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Upload Imagery</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "SAR imagery",
    type=["png","jpg","jpeg","tif","tiff"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if not uploaded_files:
    st.markdown("""
    <div class='upload-hint'>
        <div class='upload-hint-icon'>🛰️</div>
        <div class='upload-hint-text'>
            Drop SAR images here — PNG, JPG, or TIFF<br>
            Multiple files supported for batch processing
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    n_files = len(uploaded_files)
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:0.7rem;
                color:#64748b;margin-bottom:1.2rem;letter-spacing:0.08em;'>
        {n_files} file{'s' if n_files > 1 else ''} ready
    </div>
    """, unsafe_allow_html=True)

    run = st.button("Run Analysis")

    if run:
        if demo_mode:
            st.warning("model/best.pt not found — running in demo mode with simulated detections.")

        all_zip_data   = []
        total_detected = 0
        conf_sum = conf_count = 0

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

        for uploaded_file in uploaded_files:
            image_pil = Image.open(uploaded_file).convert("RGB")
            w, h      = image_pil.size
            fname     = uploaded_file.name

            prog = st.progress(0, text="")
            for step, label in enumerate(["Loading","Running inference","Rendering"], 1):
                prog.progress(step / 3, text=f"{label}…")
                time.sleep(0.15)
            prog.empty()

            if demo_mode:
                from PIL import ImageDraw
                import random
                annotated = image_pil.copy()
                draw = ImageDraw.Draw(annotated)
                detections = []
                for i in range(random.randint(1, 4)):
                    bw = random.randint(w // 20, w // 8)
                    bh = random.randint(h // 20, h // 8)
                    x1 = random.randint(0, w - bw)
                    y1 = random.randint(0, h - bh)
                    x2, y2 = x1 + bw, y1 + bh
                    conf = round(random.uniform(0.55, 0.97), 2)
                    c = (52, 211, 153)
                    draw.rectangle([x1, y1, x2, y2], outline=c, width=2)
                    draw.rectangle([x1, y1-16, x1+70, y1], fill=(0,0,0))
                    draw.text((x1+3, y1-15), f"ship {conf:.0%}", fill=c)
                    detections.append({"id":i+1,"class":"ship","confidence":conf,
                                       "x1":x1,"y1":y1,"x2":x2,"y2":y2,"width":bw,"height":bh})
            else:
                annotated, detections = run_detection(image_pil, model)

            n_det = len(detections)
            total_detected += n_det
            for d in detections:
                conf_sum   += d["confidence"]
                conf_count += 1

            all_zip_data.append((fname, annotated, detections))

            # ── Card ──
            bc = "count-badge" if n_det > 0 else "count-badge zero"
            bt = f"{'⬡ ' if n_det else '○ '}{n_det} ship{'s' if n_det!=1 else ''} detected"

            st.markdown(f"""
            <div class='result-card'>
              <div class='result-card-header'>
                <div class='result-card-title'>{fname}</div>
                <div style='display:flex;align-items:center;gap:1rem;'>
                  <div class='result-card-meta'>{w} × {h} px</div>
                  <div class='{bc}'>{bt}</div>
                </div>
              </div>
              <div class='result-card-body'>
            """, unsafe_allow_html=True)

            if show_original:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="section-label">Original</div>', unsafe_allow_html=True)
                    st.image(image_pil, use_container_width=True)
                with col2:
                    st.markdown('<div class="section-label">Detection Result</div>', unsafe_allow_html=True)
                    st.image(annotated, use_container_width=True)
            else:
                st.markdown('<div class="section-label">Detection Result</div>', unsafe_allow_html=True)
                st.image(annotated, use_container_width=True)

            if show_table and detections:
                st.markdown('<div class="section-label" style="margin-top:1.2rem;">Detection Log</div>',
                            unsafe_allow_html=True)
                rows = ""
                for d in detections:
                    c  = d["confidence"]
                    pc = "conf-high" if c >= 0.75 else "conf-med" if c >= 0.5 else "conf-low"
                    rows += f"""<tr>
                        <td>{d['id']:02d}</td><td>{d['class'].title()}</td>
                        <td><span class='conf-pill {pc}'>{c:.1%}</span></td>
                        <td>{d['x1']}, {d['y1']}</td><td>{d['x2']}, {d['y2']}</td>
                        <td>{d['width']} × {d['height']}</td></tr>"""
                st.markdown(f"""
                <table class='det-table'>
                  <thead><tr><th>#</th><th>Class</th><th>Confidence</th>
                  <th>Top-Left</th><th>Bottom-Right</th><th>Size (px)</th></tr></thead>
                  <tbody>{rows}</tbody>
                </table>""", unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

            # Per-image download
            img_buf = io.BytesIO()
            annotated.save(img_buf, format="PNG")
            st.download_button(
                label=f"↓  Download annotated image — {fname}",
                data=img_buf.getvalue(),
                file_name=f"sarshield_{fname}",
                mime="image/png",
                key=f"dl_{fname}",
            )
            st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # Update session stats
        st.session_state.scans    += len(uploaded_files)
        st.session_state.ships    += total_detected
        st.session_state.avg_conf  = conf_sum / conf_count if conf_count else 0.0

        # Summary (batch only)
        if len(uploaded_files) > 1:
            avg = f"{conf_sum/conf_count:.1%}" if conf_count else "—"
            st.markdown(f"""
            <div class='summary-bar'>
                <div class='summary-cell'><div class='summary-num'>{len(uploaded_files)}</div><div class='summary-lbl'>Images</div></div>
                <div class='summary-cell'><div class='summary-num'>{total_detected}</div><div class='summary-lbl'>Ships Found</div></div>
                <div class='summary-cell'><div class='summary-num'>{avg}</div><div class='summary-lbl'>Avg Confidence</div></div>
                <div class='summary-cell'><div class='summary-num'>{total_detected/len(uploaded_files):.1f}</div><div class='summary-lbl'>Ships / Image</div></div>
            </div>
            """, unsafe_allow_html=True)

        # ZIP / CSV export
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
        if export_zip:
            zip_bytes = build_zip(all_zip_data)
            st.download_button(
                label="↓  Download all results — annotated images + CSV report (ZIP)",
                data=zip_bytes,
                file_name="sarshield_results.zip",
                mime="application/zip",
                key="dl_zip",
            )
        else:
            csv_buf = io.StringIO()
            w2 = csv.writer(csv_buf)
            w2.writerow(["Image","Ship #","Class","Confidence","X1","Y1","X2","Y2","W","H"])
            for fname, _, dets in all_zip_data:
                for d in dets:
                    w2.writerow([fname, d["id"], d["class"], f"{d['confidence']:.4f}",
                                  d["x1"], d["y1"], d["x2"], d["y2"], d["width"], d["height"]])
            st.download_button(
                label="↓  Download detection report (CSV)",
                data=csv_buf.getvalue(),
                file_name="sarshield_report.csv",
                mime="text/csv",
                key="dl_csv",
            )


# ── ABOUT ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
with st.expander("About SARShield"):
    st.markdown("""
    **SARShield** is a maritime intelligence tool for detecting ships in Synthetic Aperture Radar (SAR) imagery.
    SAR satellites image the ocean through clouds and at night — making them essential for maritime
    monitoring, search and rescue, and traffic analysis.

    The detection model is based on **YOLOv8s**, trained on the SSDD (SAR Ship Detection Dataset)
    with SAR-specific augmentation and background balancing for improved performance on radar imagery.

    **Usage:** Upload one or more SAR images → click *Run Analysis* → review annotated results.
    Each vessel is labelled with its confidence score. Download individual results or export a full
    ZIP archive with all annotated images and a CSV report.
    """)