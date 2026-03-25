# =============================================================================
# BATTERY WASTE OPTIMIZATION - Streamlit LP Application
# =============================================================================

"""
Aplikasi Optimisasi Pengolahan Limbah Baterai
Menggunakan Linear Programming (LP) dengan PuLP solver (Simplex/CBC)
"""

import streamlit as st
import pulp
import pandas as pd
import numpy as np
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Optimisasi Limbah Baterai | LP Optimizer",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# GLOBAL CSS STYLING (Tailwind-inspired design system)
# =============================================================================
def inject_css():
    st.markdown("""
    <style>
    /* ---- Google Fonts ---- */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

    /* ---- Root Variables ---- */
    :root {
        --primary:    #2563EB;
        --primary-lt: #DBEAFE;
        --success:    #16A34A;
        --success-lt: #DCFCE7;
        --warning:    #D97706;
        --warning-lt: #FEF3C7;
        --danger:     #DC2626;
        --danger-lt:  #FEE2E2;
        --slate-50:   #F8FAFC;
        --slate-100:  #F1F5F9;
        --slate-200:  #E2E8F0;
        --slate-600:  #475569;
        --slate-700:  #334155;
        --slate-800:  #1E293B;
        --slate-900:  #0F172A;
        --card-shadow: 0 4px 24px rgba(15,23,42,0.08);
        --radius:     14px;
    }

    /* ---- Global ---- */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--slate-50) !important;
        color: var(--slate-800) !important;
    }

    /* ---- Main container ---- */
    .main .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 1400px !important;
    }

    /* ---- App Header ---- */
    .app-header {
        background: linear-gradient(135deg, #1E293B 0%, #1d4ed8 100%);
        border-radius: var(--radius);
        padding: 28px 36px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 18px;
        box-shadow: 0 8px 32px rgba(37,99,235,0.25);
    }
    .app-header h1 {
        font-family: 'Syne', sans-serif !important;
        color: #fff !important;
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.5px;
    }
    .app-header p {
        color: #BAD4FB !important;
        font-size: 0.85rem !important;
        margin: 4px 0 0 0 !important;
        font-weight: 400 !important;
    }

    /* ---- Card ---- */
    .card {
        background: #fff;
        border-radius: var(--radius);
        box-shadow: var(--card-shadow);
        padding: 22px 24px;
        margin-bottom: 18px;
        border: 1px solid var(--slate-200);
    }
    .card-title {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: var(--slate-800) !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--primary-lt);
        margin-bottom: 16px !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ---- Section label ---- */
    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--primary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        margin-top: 14px;
    }

    /* ---- Badges ---- */
    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.3px;
    }
    .badge-optimal  { background: var(--success-lt); color: var(--success); }
    .badge-infeasible { background: var(--danger-lt); color: var(--danger); }
    .badge-unbounded  { background: var(--warning-lt); color: var(--warning); }
    .badge-notrun   { background: var(--slate-100); color: var(--slate-600); }

    /* ---- Result value ---- */
    .result-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.2rem;
        font-weight: 600;
        color: var(--primary);
        line-height: 1;
    }
    .result-label {
        font-size: 0.78rem;
        color: var(--slate-600);
        font-weight: 500;
        margin-top: 4px;
    }

    /* ---- Metric grid ---- */
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 10px;
    }
    .metric-box {
        background: var(--slate-50);
        border: 1px solid var(--slate-200);
        border-radius: 10px;
        padding: 12px 16px;
    }
    .metric-box .mval {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--slate-800);
    }
    .metric-box .mlabel {
        font-size: 0.73rem;
        color: var(--slate-600);
        margin-top: 2px;
    }

    /* ---- Table styling ---- */
    .styled-table-wrap { overflow-x: auto; border-radius: 10px; }
    table.result-table {
        width: 100%; border-collapse: collapse;
        font-size: 0.83rem; font-family: 'IBM Plex Mono', monospace;
    }
    table.result-table thead tr {
        background: var(--primary); color: #fff;
    }
    table.result-table thead th {
        padding: 10px 14px; text-align: center; font-weight: 600;
        white-space: nowrap;
    }
    table.result-table tbody tr:nth-child(even) { background: var(--slate-50); }
    table.result-table tbody tr:nth-child(odd)  { background: #fff; }
    table.result-table tbody td {
        padding: 9px 14px; text-align: center; border-bottom: 1px solid var(--slate-100);
    }
    table.result-table tbody td:first-child { text-align: left; font-weight: 600; color: var(--slate-700); font-family: 'Inter', sans-serif; }
    table.result-table tbody tr:hover { background: var(--primary-lt) !important; }

    /* ---- Sensitivity table ---- */
    table.sens-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
    table.sens-table thead tr { background: var(--slate-800); color: #fff; }
    table.sens-table thead th { padding: 9px 12px; text-align: left; font-weight: 600; }
    table.sens-table tbody tr:nth-child(even) { background: var(--slate-50); }
    table.sens-table tbody td { padding: 8px 12px; border-bottom: 1px solid var(--slate-100); }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background: var(--slate-900) !important;
    }
    [data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #fff !important;
        font-family: 'Syne', sans-serif !important;
    }
    [data-testid="stSidebar"] .stMarkdown p { color: #94A3B8 !important; font-size: 0.83rem !important; }

    /* ---- Streamlit overrides ---- */
    div[data-testid="stNumberInput"] > label, div[data-testid="stSelectbox"] > label,
    div[data-testid="stFileUploader"] > label, .stTextInput > label {
        font-size: 0.8rem !important; font-weight: 600 !important;
        color: var(--slate-700) !important;
    }
    div[data-testid="stNumberInput"] input {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.9rem !important;
    }
    .stButton > button {
        border-radius: 8px !important; font-weight: 600 !important;
        font-size: 0.83rem !important; letter-spacing: 0.2px;
        transition: all 0.15s;
    }
    .stButton > button[kind="primary"] {
        background: var(--primary) !important;
        border: none !important; color: #fff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1D4ED8 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37,99,235,0.4) !important;
    }

    /* ---- Expander ---- */
    details { border-radius: 10px !important; }

    /* ---- Divider ---- */
    hr { border-color: var(--slate-200) !important; margin: 10px 0 !important; }

    /* ---- LaTeX block ---- */
    .katex-display { font-size: 0.95rem !important; }

    /* ---- Interpretation text ---- */
    .interp-block {
        background: var(--slate-50);
        border-left: 3px solid var(--primary);
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 8px 0;
        font-size: 0.82rem;
        color: var(--slate-700);
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# =============================================================================
# DEFAULT DATA CONSTANTS
# =============================================================================
BATTERY_TYPES  = ["Li-ion", "Lead-Acid", "NiMH", "NiCd", "Solid-State"]
FACILITIES     = ["Fasilitas A (Peleburan)", "Fasilitas B (Hidrometalurgi)",
                  "Fasilitas C (Pirometalurgi)", "Fasilitas D (Daur Ulang Langsung)"]
FAC_SHORT      = ["Fas. A", "Fas. B", "Fas. C", "Fas. D"]

DEFAULT_DEMAND      = [500, 300, 200, 150, 100]          # kg
DEFAULT_CAPACITY    = [600, 500, 400, 300]                # kg/bulan
DEFAULT_RECOVERY    = [0.92, 0.98, 0.85, 0.80, 0.75]     # %
DEFAULT_MAT_VALUE   = [8.0, 3.5, 5.0, 4.5, 10.0]         # $/kg
DEFAULT_MIN_RECOVER = [460, 294, 170, 120, 75]            # kg

DEFAULT_PROC_COST = [
    [3.2, 4.1, 5.0, 6.2],
    [2.5, 3.8, 4.5, 5.9],
    [4.0, 3.5, 5.5, 6.0],
    [3.8, 4.0, 4.8, 5.5],
    [5.5, 6.0, 7.0, 8.0],
]
DEFAULT_TRANS_COST = [
    [1.2, 1.5, 2.0, 2.5],
    [1.0, 1.3, 1.8, 2.2],
    [1.5, 1.4, 2.1, 2.8],
    [1.3, 1.6, 1.9, 2.4],
    [2.0, 2.3, 2.7, 3.5],
]

# =============================================================================
# SESSION STATE INIT
# =============================================================================
def init_state():
    defaults = {
        "demand":       list(DEFAULT_DEMAND),
        "capacity":     list(DEFAULT_CAPACITY),
        "recovery":     list(DEFAULT_RECOVERY),
        "mat_value":    list(DEFAULT_MAT_VALUE),
        "min_recover":  list(DEFAULT_MIN_RECOVER),
        "proc_cost":    [row[:] for row in DEFAULT_PROC_COST],
        "trans_cost":   [row[:] for row in DEFAULT_TRANS_COST],
        "lp_result":    None,
        "uploaded_data": None,
        "sheet_names":   [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 20px 0;">
        <div style="font-size:3rem;">🔋</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800;
                    color:#fff; margin-top:6px; line-height:1.3;">
            Battery Waste<br>LP Optimizer
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Deskripsi Model")
    st.markdown("""
    Aplikasi ini menggunakan **Linear Programming** untuk
    meminimalkan **biaya bersih pengolahan** limbah baterai
    pada 4 fasilitas, dengan mempertimbangkan:
    - Permintaan minimum per jenis baterai
    - Kapasitas fasilitas
    - Regulasi tingkat pemulihan
    """)

# =============================================================================
# APP HEADER
# =============================================================================
st.markdown("""
<div class="app-header">
    <div>
        <h1>Optimisasi Pengolahan Limbah Baterai</h1>
        <p>Linear Programming Solver · PuLP/CBC · Metode Simplex</p>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# LP MATH FORMULATION EXPANDER
# =============================================================================
with st.expander("Lihat Formulasi Matematika LP", expanded=False):
    st.markdown("**Variabel Keputusan:**")
    st.latex(r"x_{ij} = \text{kuantitas (kg) baterai jenis } i \text{ yang diproses di fasilitas } j")

    st.markdown("**Fungsi Objektif — Minimasi Biaya Bersih:**")
    st.latex(r"""
    \min Z = \sum_{i}\sum_{j}
    \left[(c_{ij}^{\text{proses}} + c_{ij}^{\text{transport}}) \cdot x_{ij}\right]
    - \sum_{i}\sum_{j}
    \left[r_i \cdot v_i \cdot x_{ij}\right]
    """)

    st.markdown("**Constraints:**")
    st.latex(r"\text{(1) Permintaan: } \sum_{j} x_{ij} \geq d_i \quad \forall i")
    st.latex(r"\text{(2) Kapasitas: } \sum_{i} x_{ij} \leq K_j \quad \forall j")
    st.latex(r"\text{(3) Pemulihan: } \sum_{j} r_i \cdot x_{ij} \geq m_i \quad \forall i")
    st.latex(r"\text{(4) Non-negatif: } x_{ij} \geq 0 \quad \forall i,j")

    st.markdown("""
    **Keterangan:**
    - $c_{ij}^{\\text{proses}}$ = biaya proses baterai $i$ di fasilitas $j$ (\\$/kg)
    - $c_{ij}^{\\text{transport}}$ = biaya transportasi baterai $i$ ke fasilitas $j$ (\\$/kg)
    - $r_i$ = tingkat pemulihan material baterai $i$
    - $v_i$ = nilai material terpulihkan baterai $i$ (\\$/kg)
    - $d_i$ = permintaan minimum baterai $i$ (kg)
    - $K_j$ = kapasitas fasilitas $j$ (kg/bulan)
    - $m_i$ = minimum volume pemulihan baterai $i$ (kg)
    """)

# =============================================================================
# HELPER: Parse uploaded file
# =============================================================================
def parse_uploaded_file(uploaded_file):
    """Membaca file Excel/CSV yang diunggah dan mengembalikan data sebagai dict."""
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".xlsx") or name.endswith(".xls"):
            xf = pd.ExcelFile(uploaded_file)
            sheets = xf.sheet_names
            data = {s: xf.parse(s) for s in sheets}
            return data, sheets, None
        elif name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            return {"csv_data": df}, ["csv_data"], None
        else:
            return None, [], "Format file tidak didukung. Gunakan .xlsx atau .csv"
    except Exception as e:
        return None, [], f"Error membaca file: {str(e)}"


def apply_imported_data(data_dict):
    """Memuat data dari dict sheet ke session state LP."""
    msgs = []
    try:
        if "harga" in data_dict:
            df = data_dict["harga"].values
            if df.shape[0] >= 5 and df.shape[1] >= 4:
                st.session_state.proc_cost = [[float(df[i][j]) for j in range(4)] for i in range(5)]
                msgs.append("Matriks biaya proses dimuat dari sheet 'harga'")
        if "transport" in data_dict:
            df = data_dict["transport"].values
            if df.shape[0] >= 5 and df.shape[1] >= 4:
                st.session_state.trans_cost = [[float(df[i][j]) for j in range(4)] for i in range(5)]
                msgs.append("Matriks biaya transportasi dimuat dari sheet 'transport'")
        if "params" in data_dict:
            df = data_dict["params"]
            row = df.iloc[0]
            # Try to load demand, capacity, etc.
            for idx in range(5):
                k = f"permintaan_{idx+1}"
                if k in row: st.session_state.demand[idx] = float(row[k])
            for idx in range(4):
                k = f"kapasitas_{idx+1}"
                if k in row: st.session_state.capacity[idx] = float(row[k])
            for idx in range(5):
                k = f"pemulihan_{idx+1}"
                if k in row: st.session_state.recovery[idx] = float(row[k])
            for idx in range(5):
                k = f"nilai_{idx+1}"
                if k in row: st.session_state.mat_value[idx] = float(row[k])
            for idx in range(5):
                k = f"min_recover_{idx+1}"
                if k in row: st.session_state.min_recover[idx] = float(row[k])
            msgs.append("Parameter dimuat dari sheet 'params'")
        return msgs if msgs else [" Tidak ada sheet yang dikenali (harga/transport/params)"]
    except Exception as e:
        return [f" Error saat memuat data: {str(e)}"]

# =============================================================================
# MAIN TWO-COLUMN LAYOUT
# =============================================================================
col_left, col_right = st.columns([1, 1], gap="large")

# ─────────────────────────────────────────────────────────────────────────────
# PANEL KIRI — Input Data
# ─────────────────────────────────────────────────────────────────────────────
with col_left:
    # ── IMPORT DATA ──────────────────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">Import Data</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload file Excel atau CSV",
        type=["xlsx", "xls", "csv"],
        help="Unggah file .xlsx (multi-sheet) atau .csv untuk mengisi parameter LP secara otomatis.",
        label_visibility="collapsed",
    )

    if uploaded_file:
        data_dict, sheet_names, err = parse_uploaded_file(uploaded_file)
        if err:
            st.error(err)
        else:
            st.session_state.uploaded_data  = data_dict
            st.session_state.sheet_names    = sheet_names

            selected_sheet = st.selectbox(
                "Pilih Sheet untuk Preview",
                options=sheet_names,
                help="Pilih sheet yang ingin ditampilkan di tabel preview."
            )
            n_rows = st.number_input("Jumlah baris preview", min_value=3, max_value=50, value=8, step=1)

            if selected_sheet and selected_sheet in data_dict:
                st.dataframe(
                    data_dict[selected_sheet].head(n_rows),
                    use_container_width=True,
                    height=200,
                )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Muat Data", type="primary", use_container_width=True):
                    msgs = apply_imported_data(data_dict)
                    for m in msgs:
                        if m.startswith(" Matriks biaya proses") or m.startswith("Matriks biaya transportasi") or m.startswith("Parameter dimuat"):
                            st.success(m)
                        elif m.startswith(" Tidak ada sheet yang dikenali"):
                            st.warning(m)
                        else:
                            st.error(m)
            with c2:
                if st.button("Hapus File", use_container_width=True):
                    st.session_state.uploaded_data = None
                    st.session_state.sheet_names   = []
                    st.rerun()
    else:
        st.info("Tidak ada file yang diunggah — gunakan nilai default atau input manual.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── INPUT MANUAL — Demand & Capacity ────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">Input Manual (Demand & Kapasitas)</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Permintaan Minimum per Jenis Baterai (kg)</div>', unsafe_allow_html=True)
    new_demand = []
    cols_d = st.columns(5)
    for idx, bat in enumerate(BATTERY_TYPES):
        with cols_d[idx]:
            v = st.number_input(
                bat, min_value=0.0, value=float(st.session_state.demand[idx]),
                step=10.0, key=f"demand_{idx}",
                help=f"Jumlah minimum baterai {bat} yang harus diproses (kg/bulan)"
            )
            new_demand.append(v)
    st.session_state.demand = new_demand

    st.markdown('<div class="section-label">Kapasitas Fasilitas (kg/bulan)</div>', unsafe_allow_html=True)
    new_cap = []
    cols_c = st.columns(4)
    for idx, fac in enumerate(FAC_SHORT):
        with cols_c[idx]:
            v = st.number_input(
                fac, min_value=0.0, value=float(st.session_state.capacity[idx]),
                step=50.0, key=f"cap_{idx}",
                help=f"Kapasitas maksimum pemrosesan di {FACILITIES[idx]}"
            )
            new_cap.append(v)
    st.session_state.capacity = new_cap

    st.markdown('</div>', unsafe_allow_html=True)

    # ── INPUT MANUAL — Recovery & Material Value ─────────────────────────────
    st.markdown('<div class="card"><div class="card-title">Pemulihan Material & Nilai</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Tingkat Pemulihan (%)</div>', unsafe_allow_html=True)
    new_rec, new_val, new_minr = [], [], []
    cols_r = st.columns(5)
    for idx, bat in enumerate(BATTERY_TYPES):
        with cols_r[idx]:
            v = st.number_input(
                bat, min_value=0.0, max_value=1.0,
                value=float(st.session_state.recovery[idx]),
                step=0.01, format="%.2f", key=f"rec_{idx}",
                help=f"Fraksi material yang dapat dipulihkan dari baterai {bat} (0–1)"
            )
            new_rec.append(v)
    st.session_state.recovery = new_rec

    st.markdown('<div class="section-label">Nilai Material Terpulihkan ($/kg)</div>', unsafe_allow_html=True)
    cols_v = st.columns(5)
    for idx, bat in enumerate(BATTERY_TYPES):
        with cols_v[idx]:
            v = st.number_input(
                bat, min_value=0.0, value=float(st.session_state.mat_value[idx]),
                step=0.5, key=f"val_{idx}",
                help=f"Nilai pasar material yang dipulihkan dari baterai {bat} ($/kg)"
            )
            new_val.append(v)
    st.session_state.mat_value = new_val

    st.markdown('<div class="section-label">Min Volume Pemulihan Regulasi (kg)</div>', unsafe_allow_html=True)
    cols_m = st.columns(5)
    for idx, bat in enumerate(BATTERY_TYPES):
        with cols_m[idx]:
            v = st.number_input(
                bat, min_value=0.0, value=float(st.session_state.min_recover[idx]),
                step=5.0, key=f"minr_{idx}",
                help=f"Volume minimum pemulihan yang diwajibkan regulasi untuk baterai {bat} (kg)"
            )
            new_minr.append(v)
    st.session_state.min_recover = new_minr

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL KANAN — Matriks Biaya
# ─────────────────────────────────────────────────────────────────────────────
with col_right:
    # ── Matriks Biaya Pemrosesan ─────────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">Matriks Biaya Pemrosesan ($/kg)</div>', unsafe_allow_html=True)
    st.caption("Baris = Jenis Baterai · Kolom = Fasilitas")

    new_proc = [[0.0]*4 for _ in range(5)]
    proc_cols = st.columns([2, 1, 1, 1, 1])
    with proc_cols[0]:
        st.markdown('<div class="section-label">Baterai \\ Fasilitas</div>', unsafe_allow_html=True)
    for j, fac in enumerate(FAC_SHORT):
        with proc_cols[j+1]:
            st.markdown(f'<div class="section-label">{fac}</div>', unsafe_allow_html=True)

    for i, bat in enumerate(BATTERY_TYPES):
        cols_p = st.columns([2, 1, 1, 1, 1])
        with cols_p[0]:
            st.markdown(f"<div style='padding:6px 0; font-weight:600; font-size:0.82rem;'>{bat}</div>",
                        unsafe_allow_html=True)
        for j in range(4):
            with cols_p[j+1]:
                v = st.number_input(
                    f"p{i}{j}", min_value=0.0,
                    value=float(st.session_state.proc_cost[i][j]),
                    step=0.1, format="%.2f",
                    label_visibility="collapsed", key=f"proc_{i}_{j}",
                    help=f"Biaya proses {bat} di {FACILITIES[j]} ($/kg)"
                )
                new_proc[i][j] = v
    st.session_state.proc_cost = new_proc

    c_upd, c_rst = st.columns(2)
    with c_upd:
        if st.button("Update Biaya Proses", use_container_width=True):
            st.success("Biaya proses diperbarui.")
    with c_rst:
        if st.button("Reset Default (Proses)", use_container_width=True):
            st.session_state.proc_cost = [row[:] for row in DEFAULT_PROC_COST]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Matriks Biaya Transportasi ───────────────────────────────────────────
    st.markdown('<div class="card"><div class="card-title">Matriks Biaya Transportasi ($/kg)</div>', unsafe_allow_html=True)
    st.caption("Baris = Jenis Baterai · Kolom = Fasilitas")

    new_trans = [[0.0]*4 for _ in range(5)]
    trans_cols = st.columns([2, 1, 1, 1, 1])
    with trans_cols[0]:
        st.markdown('<div class="section-label">Baterai \\ Fasilitas</div>', unsafe_allow_html=True)
    for j, fac in enumerate(FAC_SHORT):
        with trans_cols[j+1]:
            st.markdown(f'<div class="section-label">{fac}</div>', unsafe_allow_html=True)

    for i, bat in enumerate(BATTERY_TYPES):
        cols_t = st.columns([2, 1, 1, 1, 1])
        with cols_t[0]:
            st.markdown(f"<div style='padding:6px 0; font-weight:600; font-size:0.82rem;'>{bat}</div>",
                        unsafe_allow_html=True)
        for j in range(4):
            with cols_t[j+1]:
                v = st.number_input(
                    f"t{i}{j}", min_value=0.0,
                    value=float(st.session_state.trans_cost[i][j]),
                    step=0.1, format="%.2f",
                    label_visibility="collapsed", key=f"trans_{i}_{j}",
                    help=f"Biaya transportasi {bat} ke {FACILITIES[j]} ($/kg)"
                )
                new_trans[i][j] = v
    st.session_state.trans_cost = new_trans

    c_upd2, c_rst2 = st.columns(2)
    with c_upd2:
        if st.button("Update Biaya Transport", use_container_width=True):
            st.success("Biaya transportasi diperbarui.")
    with c_rst2:
        if st.button("Reset Default (Transport)", use_container_width=True):
            st.session_state.trans_cost = [row[:] for row in DEFAULT_TRANS_COST]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# LP SOLVER FUNCTION
# =============================================================================
def solve_lp():
    """
    Membangun dan menyelesaikan model LP menggunakan PuLP/CBC.
    Mengembalikan dict hasil atau None jika terjadi error.
    """
    demand     = st.session_state.demand
    capacity   = st.session_state.capacity
    recovery   = st.session_state.recovery
    mat_value  = st.session_state.mat_value
    min_rec    = st.session_state.min_recover
    proc_cost  = st.session_state.proc_cost
    trans_cost = st.session_state.trans_cost

    n_bat = len(BATTERY_TYPES)
    n_fac = len(FAC_SHORT)

    # ── Definisi Masalah LP ──────────────────────────────────────────────────
    prob = pulp.LpProblem("Optimisasi_Limbah_Baterai", pulp.LpMinimize)

    # Variabel keputusan: x[i][j] >= 0
    x = pulp.LpVariable.dicts(
        "x",
        [(i, j) for i in range(n_bat) for j in range(n_fac)],
        lowBound=0,
        cat='Continuous'
    )

    # ── Fungsi Objektif ──────────────────────────────────────────────────────
    prob += pulp.lpSum(
        (proc_cost[i][j] + trans_cost[i][j] - recovery[i] * mat_value[i]) * x[(i, j)]
        for i in range(n_bat) for j in range(n_fac)
    ), "Total_Biaya_Bersih"

    # ── Constraints ─────────────────────────────────────────────────────────
    # (1) Permintaan minimum
    demand_constraints = {}
    for i in range(n_bat):
        c = pulp.lpSum(x[(i, j)] for j in range(n_fac)) >= demand[i]
        prob += c, f"Demand_{BATTERY_TYPES[i]}"
        demand_constraints[i] = c

    # (2) Kapasitas fasilitas
    capacity_constraints = {}
    for j in range(n_fac):
        c = pulp.lpSum(x[(i, j)] for i in range(n_bat)) <= capacity[j]
        prob += c, f"Kapasitas_{FAC_SHORT[j]}"
        capacity_constraints[j] = c

    # (3) Minimum pemulihan regulasi
    recovery_constraints = {}
    for i in range(n_bat):
        c = pulp.lpSum(recovery[i] * x[(i, j)] for j in range(n_fac)) >= min_rec[i]
        prob += c, f"MinPemulihan_{BATTERY_TYPES[i]}"
        recovery_constraints[i] = c

    # ── Solve ────────────────────────────────────────────────────────────────
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=60)
    prob.solve(solver)

    status     = pulp.LpStatus[prob.status]
    status_num = prob.status   # 1=Optimal, -1=Infeasible, etc.
    obj_value  = pulp.value(prob.objective)

    # Extract variable values
    x_vals = np.zeros((n_bat, n_fac))
    if status_num == 1:
        for i in range(n_bat):
            for j in range(n_fac):
                val = x[(i, j)].varValue
                x_vals[i][j] = val if val is not None else 0.0

    # ── Dual Values / Shadow Prices ──────────────────────────────────────────
    dual_demand    = {}
    dual_capacity  = {}
    dual_recovery  = {}
    slack_demand   = {}
    slack_capacity = {}
    slack_recovery = {}

    for name, constraint in prob.constraints.items():
        try:
            pi  = constraint.pi   if constraint.pi   is not None else 0.0
            slk = constraint.slack if constraint.slack is not None else 0.0
        except Exception:
            pi, slk = 0.0, 0.0

        if name.startswith("Demand_"):
            bat = name.replace("Demand_", "")
            idx = BATTERY_TYPES.index(bat) if bat in BATTERY_TYPES else -1
            if idx >= 0:
                dual_demand[idx]  = pi
                slack_demand[idx] = slk
        elif name.startswith("Kapasitas_"):
            fac = name.replace("Kapasitas_", "")
            idx = FAC_SHORT.index(fac) if fac in FAC_SHORT else -1
            if idx >= 0:
                dual_capacity[idx]  = pi
                slack_capacity[idx] = slk
        elif name.startswith("MinPemulihan_"):
            bat = name.replace("MinPemulihan_", "")
            idx = BATTERY_TYPES.index(bat) if bat in BATTERY_TYPES else -1
            if idx >= 0:
                dual_recovery[idx]  = pi
                slack_recovery[idx] = slk

    return {
        "status":         status,
        "status_num":     status_num,
        "obj_value":      obj_value,
        "x_vals":         x_vals,
        "dual_demand":    dual_demand,
        "dual_capacity":  dual_capacity,
        "dual_recovery":  dual_recovery,
        "slack_demand":   slack_demand,
        "slack_capacity": slack_capacity,
        "slack_recovery": slack_recovery,
        "prob":           prob,
    }

# =============================================================================
# EXPORT HELPER
# =============================================================================
def build_excel_export(result):
    """Membuat file Excel dari hasil LP menggunakan BytesIO."""
    output = BytesIO()
    x_vals = result["x_vals"]

    # Allocation matrix
    df_alloc = pd.DataFrame(
        x_vals,
        index=BATTERY_TYPES,
        columns=FAC_SHORT,
    )
    df_alloc["Total (kg)"] = df_alloc.sum(axis=1)

    # Dual/sensitivity table
    rows_sens = []
    for i, bat in enumerate(BATTERY_TYPES):
        rows_sens.append({
            "Jenis": bat,
            "Tipe": "Demand",
            "Shadow Price": result["dual_demand"].get(i, 0),
            "Slack": result["slack_demand"].get(i, 0),
        })
        rows_sens.append({
            "Jenis": bat,
            "Tipe": "Min Pemulihan",
            "Shadow Price": result["dual_recovery"].get(i, 0),
            "Slack": result["slack_recovery"].get(i, 0),
        })
    for j, fac in enumerate(FAC_SHORT):
        rows_sens.append({
            "Jenis": fac,
            "Tipe": "Kapasitas",
            "Shadow Price": result["dual_capacity"].get(j, 0),
            "Slack": result["slack_capacity"].get(j, 0),
        })
    df_sens = pd.DataFrame(rows_sens)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_alloc.to_excel(writer, sheet_name="Alokasi")
        df_sens.to_excel(writer, sheet_name="Sensitivitas", index=False)
        ws = writer.sheets["Alokasi"]
        ws.write(0, 0, f"Nilai Objektif: ${result['obj_value']:.4f}" if result['obj_value'] else "N/A")
        ws.write(1, 0, f"Status: {result['status']}")

    output.seek(0)
    return output

# =============================================================================
# ACTION BUTTONS
# =============================================================================
st.markdown("---")
st.markdown('<div class="card-title" style="font-family:Syne,sans-serif; font-size:1rem; font-weight:700; color:#1E293B;">Aksi</div>', unsafe_allow_html=True)

btn_cols = st.columns([1.5, 1, 1.2, 1])
with btn_cols[0]:
    run_btn = st.button("Hitung (Solve LP)", type="primary", use_container_width=True)
with btn_cols[1]:
    clear_btn = st.button("Hapus Hasil", use_container_width=True)
with btn_cols[2]:
    export_placeholder = st.empty()
with btn_cols[3]:
    reset_btn = st.button("Reset Semua", use_container_width=True)

if reset_btn:
    for k in ["demand", "capacity", "recovery", "mat_value", "min_recover", "proc_cost", "trans_cost", "lp_result"]:
        if k in st.session_state:
            del st.session_state[k]
    st.success("Semua parameter direset ke default.")
    st.rerun()

if clear_btn:
    st.session_state.lp_result = None
    st.rerun()

if run_btn:
    with st.spinner("Solver berjalan... (PuLP/CBC Simplex)"):
        try:
            result = solve_lp()
            st.session_state.lp_result = result
        except Exception as e:
            st.error(f" Error saat menjalankan solver: {str(e)}")
            st.session_state.lp_result = None

# =============================================================================
# RESULTS SECTION
# =============================================================================
result = st.session_state.get("lp_result", None)

st.markdown("---")

if result is None:
    st.markdown("""
    <div class="card" style="text-align:center; padding:32px;">
        <div style="font-size:2.5rem;"></div>
        <div style="font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700;
                    color:#475569; margin-top:10px;">Hasil Belum Tersedia</div>
        <div style="font-size:0.83rem; color:#94A3B8; margin-top:6px;">
            Klik tombol <b>Hitung</b> untuk menjalankan solver LP.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # ── Status Badge ─────────────────────────────────────────────────────────
    status = result["status"]
    status_num = result["status_num"]

    badge_map = {
        "Optimal":    ("badge-optimal",   "Optimal"),
        "Infeasible": ("badge-infeasible"," Infeasible"),
        "Unbounded":  ("badge-unbounded", "Unbounded"),
    }
    badge_cls, badge_txt = badge_map.get(status, ("badge-notrun", f"{status}"))

    obj_val = result["obj_value"]
    obj_str = f"${obj_val:,.4f}" if obj_val is not None else "N/A"

    # ── Status feedback ───────────────────────────────────────────────────────
    if status == "Optimal":
        st.success(f"**Solusi Optimal ditemukan!** Nilai Objektif: **{obj_str}**")
    elif status == "Infeasible":
        st.error("**Solusi Tidak Layak (Infeasible):** Constraint tidak dapat dipenuhi secara bersamaan. Coba perlonggar kapasitas atau kurangi permintaan.")
    elif status == "Unbounded":
        st.warning("**Solusi Tak Terbatas (Unbounded):** Periksa fungsi objektif — kemungkinan ada koefisien negatif yang sangat besar.", icon="⚠️")
    else:
        st.info(f"Status solver: {status}")

    # ── Result Panels ─────────────────────────────────────────────────────────
    res_left, res_right = st.columns(2, gap="large")

    # ╔══ KIRI: Hasil LP Deterministik ════════════════════════════════════════
    with res_left:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Hasil LP Deterministik</div>
            <div style="display:flex; align-items:center; gap:14px; margin-bottom:20px;">
                <span class="badge {badge_cls}">{badge_txt}</span>
                <div>
                    <div class="result-value">{obj_str}</div>
                    <div class="result-label">Total Biaya Bersih Minimum ($/bulan)</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if status == "Optimal":
            # Summary metrics
            x_vals = result["x_vals"]
            total_proc   = x_vals.sum()
            total_revenue = sum(
                result["x_vals"][i][j] * st.session_state.recovery[i] * st.session_state.mat_value[i]
                for i in range(5) for j in range(4)
            )
            total_cost_raw = sum(
                result["x_vals"][i][j] * (st.session_state.proc_cost[i][j] + st.session_state.trans_cost[i][j])
                for i in range(5) for j in range(4)
            )

            st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-box">
                    <div class="mval">{total_proc:,.1f} kg</div>
                    <div class="mlabel">Total Volume Diproses</div>
                </div>
                <div class="metric-box">
                    <div class="mval" style="color:#16A34A;">${total_revenue:,.2f}</div>
                    <div class="mlabel">Estimasi Pendapatan Material</div>
                </div>
                <div class="metric-box">
                    <div class="mval" style="color:#DC2626;">${total_cost_raw:,.2f}</div>
                    <div class="mlabel">Total Biaya Kotor</div>
                </div>
                <div class="metric-box">
                    <div class="mval">{len([v for v in x_vals.flatten() if v > 0.01])}</div>
                    <div class="mlabel">Alur Aktif (xᵢⱼ > 0)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Allocation matrix table
            st.markdown('<div style="margin-top:18px; font-weight:700; font-size:0.83rem; color:#475569; margin-bottom:8px;">MATRIKS ALOKASI xᵢⱼ (kg)</div>', unsafe_allow_html=True)
            header_row = "<tr><th>Baterai</th>" + "".join(f"<th>{f}</th>" for f in FAC_SHORT) + "<th>Total</th></tr>"
            body_rows = ""
            for i, bat in enumerate(BATTERY_TYPES):
                cells = "".join(f"<td>{x_vals[i][j]:.1f}</td>" for j in range(4))
                row_total = x_vals[i].sum()
                meets = "" if row_total >= st.session_state.demand[i] - 0.01 else "⚠️"
                body_rows += f"<tr><td>{bat}</td>{cells}<td><b>{row_total:.1f}</b> {meets}</td></tr>"
            # Column totals
            col_totals = "".join(f"<td><b>{x_vals[:, j].sum():.1f}</b></td>" for j in range(4))
            grand_total = x_vals.sum()
            body_rows += f"<tr style='background:#DBEAFE;font-weight:700;'><td>TOTAL</td>{col_totals}<td><b>{grand_total:.1f}</b></td></tr>"

            st.markdown(f"""
            <div class="styled-table-wrap">
            <table class="result-table">
                <thead>{header_row}</thead>
                <tbody>{body_rows}</tbody>
            </table>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ╔══ KANAN: Sensitivitas & Interpretasi ══════════════════════════════════
    with res_right:
        st.markdown("""
        <div class="card">
            <div class="card-title">Analisis Sensitivitas & Ringkasan</div>
        """, unsafe_allow_html=True)

        if status == "Optimal":
            # ── Shadow Prices Demand ──────────────────────────────────────────
            st.markdown('<div class="section-label">Shadow Prices — Constraint Permintaan</div>', unsafe_allow_html=True)
            sens_rows_d = ""
            for i, bat in enumerate(BATTERY_TYPES):
                pi  = result["dual_demand"].get(i, 0)
                slk = result["slack_demand"].get(i, 0)
                binding = "Mengikat" if abs(slk) < 0.01 else f"Slack: {slk:.2f}"
                pi_color = "#DC2626" if pi < 0 else ("#16A34A" if pi > 0 else "#64748B")
                sens_rows_d += f"<tr><td>{bat}</td><td style='color:{pi_color};font-family:monospace;'>{pi:.4f}</td><td>{binding}</td></tr>"

            st.markdown(f"""
            <table class="sens-table">
                <thead><tr><th>Baterai</th><th>Shadow Price</th><th>Status</th></tr></thead>
                <tbody>{sens_rows_d}</tbody>
            </table>
            """, unsafe_allow_html=True)

            # ── Shadow Prices Capacity ────────────────────────────────────────
            st.markdown('<div class="section-label" style="margin-top:14px;">Shadow Prices — Constraint Kapasitas</div>', unsafe_allow_html=True)
            sens_rows_c = ""
            for j, fac in enumerate(FAC_SHORT):
                pi  = result["dual_capacity"].get(j, 0)
                slk = result["slack_capacity"].get(j, 0)
                binding = "Mengikat" if abs(slk) < 0.01 else f"Slack: {slk:.2f}"
                pi_color = "#DC2626" if pi < 0 else ("#16A34A" if pi > 0 else "#64748B")
                sens_rows_c += f"<tr><td>{fac}</td><td style='color:{pi_color};font-family:monospace;'>{pi:.4f}</td><td>{binding}</td></tr>"

            st.markdown(f"""
            <table class="sens-table">
                <thead><tr><th>Fasilitas</th><th>Shadow Price</th><th>Status</th></tr></thead>
                <tbody>{sens_rows_c}</tbody>
            </table>
            """, unsafe_allow_html=True)

            # ── Min Recovery Slack ────────────────────────────────────────────
            st.markdown('<div class="section-label" style="margin-top:14px;">Shadow Prices — Constraint Min Pemulihan</div>', unsafe_allow_html=True)
            sens_rows_r = ""
            for i, bat in enumerate(BATTERY_TYPES):
                pi  = result["dual_recovery"].get(i, 0)
                slk = result["slack_recovery"].get(i, 0)
                binding = "Mengikat" if abs(slk) < 0.01 else f"Slack: {slk:.2f}"
                pi_color = "#DC2626" if pi < 0 else ("#16A34A" if pi > 0 else "#64748B")
                sens_rows_r += f"<tr><td>{bat}</td><td style='color:{pi_color};font-family:monospace;'>{pi:.4f}</td><td>{binding}</td></tr>"

            st.markdown(f"""
            <table class="sens-table">
                <thead><tr><th>Baterai</th><th>Shadow Price</th><th>Status</th></tr></thead>
                <tbody>{sens_rows_r}</tbody>
            </table>
            """, unsafe_allow_html=True)

            # ── Interpretasi ──────────────────────────────────────────────────
            st.markdown('<div class="section-label" style="margin-top:14px;">💬 Interpretasi</div>', unsafe_allow_html=True)

            binding_demand = [BATTERY_TYPES[i] for i in range(5) if abs(result["slack_demand"].get(i, 1)) < 0.01]
            binding_cap    = [FAC_SHORT[j]     for j in range(4) if abs(result["slack_capacity"].get(j, 1)) < 0.01]

            interp_lines = [f"<b>Solusi optimal ditemukan</b> dengan nilai objektif <b>{obj_str}</b>"]
            if binding_demand:
                interp_lines.append(f"Constraint permintaan <b>mengikat</b> pada: {', '.join(binding_demand)}")
            if binding_cap:
                interp_lines.append(f"Kapasitas <b>penuh terisi</b> di: {', '.join(binding_cap)}")
            if not binding_demand and not binding_cap:
                interp_lines.append("Semua constraint memiliki slack — solusi tidak berada pada batas ketat.")

            for line in interp_lines:
                st.markdown(f'<div class="interp-block">{line}</div>', unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="interp-block">
                <b>Status: {status}</b><br>
                Analisis sensitivitas hanya tersedia untuk solusi Optimal.
                Cek parameter input Anda dan pastikan constraint konsisten.
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Export Button (populated after results) ───────────────────────────────
    if status == "Optimal" and obj_val is not None:
        excel_data = build_excel_export(result)
        with export_placeholder:
            st.download_button(
                label="📥 Ekspor Hasil (.xlsx)",
                data=excel_data,
                file_name="hasil_optimisasi_baterai.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.75rem; color:#94A3B8; padding:8px 0 16px 0;">
    Battery Waste LP Optimizer · Dibangun dengan Streamlit
</div>
""", unsafe_allow_html=True)