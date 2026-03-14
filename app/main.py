"""
main.py
-------
Netflix Analytics Dashboard
Run with: streamlit run app/main.py
"""

import streamlit as st
import pandas as pd

from database import load_data_to_mongo, fetch_all_data, apply_filters
from charts import (
    pie_movies_vs_shows,
    bar_rating_distribution,
    histogram_duration,
    bar_top_genres,
    line_genre_trends,
    bar_genre_type_comparison,
    bar_top_countries,
    choropleth_countries,
    bar_country_type_split,
    line_titles_per_year,
    bar_release_year,
    bar_monthly_additions,
    bar_top_actors,
    bar_top_directors,
    bar_rating_by_type,
    forecast_titles,
    forecast_type_split,
    heatmap_additions,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Netflix Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fraunces:opsz,wght@9..144,300;9..144,600;9..144,700&display=swap');

/* ── Base ── */
html, body, .stApp {
    background-color: #F3F4F4 !important;
    font-family: 'Inter', sans-serif;
    color: #2C2C2C;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar — dark plum background ── */
[data-testid="stSidebar"] {
    background-color: #612D53 !important;
    border-right: none !important;
}

/* Labels outside boxes — pale plum */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small {
    color: #E8D5DA !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Sidebar headings */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F3EEF0 !important;
    font-family: 'Fraunces', serif !important;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: rgba(232,213,218,0.25) !important;
}

/* Selectbox / multiselect boxes — pale plum bg, black text */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #E8D5DA !important;
    border: none !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] input {
    color: #2C2C2C !important;
}

/* ── Dropdown popup list — override dark background ── */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] ul,
ul[data-baseweb="menu"] {
    background-color: #F3EEF0 !important;
    border: 1px solid #D4B8C4 !important;
    border-radius: 8px !important;
}
[data-baseweb="menu"] li,
[data-baseweb="option"],
[role="option"] {
    background-color: #F3EEF0 !important;
    color: #2C2C2C !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="option"]:hover,
[role="option"]:hover,
[data-baseweb="option"][aria-selected="true"],
[role="option"][aria-selected="true"] {
    background-color: #E8D5DA !important;
    color: #2C2C2C !important;
}

/* Text inputs — pale plum bg, black text */
[data-testid="stSidebar"] .stTextInput input {
    background-color: #E8D5DA !important;
    border: none !important;
    color: #2C2C2C !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: #7a5060 !important;
}

/* ── SIDEBAR SLIDERS — full override, no red ── */
[data-testid="stSidebar"] [data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
    background: rgba(232,213,218,0.3) !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div:first-child {
    background: #C4899A !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
    background: #E8D5DA !important;
    border: 2px solid #853953 !important;
    box-shadow: 0 0 0 3px rgba(133,57,83,0.25) !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"]:focus {
    box-shadow: 0 0 0 4px rgba(133,57,83,0.4) !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBarMax"],
[data-testid="stSidebar"] [data-testid="stSlider"] span {
    color: #E8D5DA !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div > div {
    background: #C4899A !important;
}

/* Sidebar button */
[data-testid="stSidebar"] .stButton button {
    background-color: #853953 !important;
    color: #F3EEF0 !important;
    border: 1px solid rgba(232,213,218,0.4) !important;
}

/* ── Main headings ── */
h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: #2C2C2C !important;
    font-weight: 600 !important;
}

/* ── Header banner ── */
.page-header {
    background: linear-gradient(120deg, #612D53 0%, #853953 60%, #A0566B 100%);
    border-radius: 12px;
    padding: 36px 48px;
    margin-bottom: 28px;
}
.page-header h1 {
    font-family: 'Fraunces', serif !important;
    font-size: 2.4rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin: 0 !important;
    letter-spacing: -0.02em;
}
.page-header p {
    color: rgba(255,255,255,0.72) !important;
    font-size: 0.95rem;
    margin-top: 6px;
    margin-bottom: 0;
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    letter-spacing: 0.03em;
}

/* ── KPI Cards ── */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E8DDE2 !important;
    border-radius: 10px !important;
    padding: 20px 24px !important;
    box-shadow: 0 2px 8px rgba(133,57,83,0.07) !important;
}
[data-testid="stMetricLabel"] {
    color: #888888 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    color: #853953 !important;
    font-family: 'Fraunces', serif !important;
    font-size: 2rem !important;
    font-weight: 600 !important;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #853953;
    margin-bottom: 4px;
    margin-top: 8px;
}
.section-title {
    font-family: 'Fraunces', serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #2C2C2C;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #E8DDE2;
}

/* ── Chart card wrapper ── */
.chart-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #EDE6EA;
    padding: 4px;
    box-shadow: 0 2px 8px rgba(133,57,83,0.05);
    margin-bottom: 16px;
}

/* ── Rating reference card ── */
.rating-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #EDE6EA;
    padding: 20px 24px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(133,57,83,0.05);
}
.rating-badge {
    display: inline-block;
    background: #612D53;
    color: #F3EEF0;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 4px 10px;
    border-radius: 4px;
    margin-right: 10px;
    vertical-align: middle;
}
.rating-fullname {
    font-family: 'Fraunces', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #2C2C2C;
    vertical-align: middle;
}
.rating-desc {
    font-size: 0.85rem;
    color: #666666;
    margin-top: 6px;
    line-height: 1.5;
}
.rating-applies {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    color: #853953;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 8px;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 2px solid #E8DDE2;
    gap: 0;
}
[data-testid="stTabs"] button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #888888 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    border-radius: 0 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #853953 !important;
    border-bottom: 2px solid #853953 !important;
    font-weight: 600 !important;
}

/* ── MAIN CONTENT SLIDERS — no red ── */
section.main [data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
    background: #E8DDE2 !important;
}
section.main [data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div:first-child {
    background: #853953 !important;
}
section.main [data-testid="stSlider"] [role="slider"] {
    background: #FFFFFF !important;
    border: 2px solid #853953 !important;
    box-shadow: 0 0 0 3px rgba(133,57,83,0.15) !important;
}
section.main [data-testid="stSlider"] [role="slider"]:focus {
    box-shadow: 0 0 0 4px rgba(133,57,83,0.3) !important;
}
section.main [data-testid="stSlider"] [data-testid="stTickBarMin"],
section.main [data-testid="stSlider"] [data-testid="stTickBarMax"],
section.main [data-testid="stSlider"] span {
    color: #2C2C2C !important;
}
section.main [data-testid="stSlider"] > div > div > div > div {
    background: #853953 !important;
}
[data-baseweb="slider"] [role="slider"] {
    background: #FFFFFF !important;
    border-color: #853953 !important;
}
[data-baseweb="slider"] > div > div > div:first-child {
    background: #853953 !important;
}
:root {
    --primary-color: #853953 !important;
}

/* ── Buttons ── */
.stButton button {
    background-color: #853953 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em;
    padding: 8px 16px !important;
}
.stButton button:hover {
    background-color: #612D53 !important;
}

/* ── Inputs in main content ── */
section.main .stTextInput input {
    background: #FFFFFF !important;
    border: 1px solid #D8CED4 !important;
    border-radius: 6px !important;
    color: #2C2C2C !important;
    font-family: 'Inter', sans-serif !important;
}
section.main .stTextInput input:focus {
    border-color: #853953 !important;
    box-shadow: 0 0 0 2px rgba(133,57,83,0.12) !important;
}
section.main .stTextInput label {
    color: #555555 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: none !important;
    letter-spacing: normal !important;
}

/* ── Divider ── */
hr {
    border-color: #EDE6EA !important;
    margin: 16px 0 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #E8DDE2 !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Info / alert boxes — pale plum, NO blue ── */
div[data-testid="stAlert"],
div[data-testid="stInfo"],
div[role="alert"] {
    background-color: #F0E4E9 !important;
    border: none !important;
    border-left: 3px solid #853953 !important;
    border-radius: 6px !important;
}
div[data-testid="stAlert"] *,
div[data-testid="stInfo"] *,
div[role="alert"] * {
    color: #612D53 !important;
}
div[data-testid="stAlert"] svg,
div[data-testid="stInfo"] svg,
div[role="alert"] svg {
    fill: #853953 !important;
    color: #853953 !important;
}

/* ── Rating reference cards ── */
.rating-card {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #EDE6EA;
    padding: 16px 20px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(133,57,83,0.05);
}
.rating-badge {
    display: inline-block;
    background: #612D53;
    color: #F3EEF0;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 3px 9px;
    border-radius: 4px;
    margin-right: 10px;
    vertical-align: middle;
}
.rating-fullname {
    font-family: 'Fraunces', serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #2C2C2C;
    vertical-align: middle;
}
.rating-desc {
    font-size: 0.82rem;
    color: #666666;
    margin-top: 7px;
    line-height: 1.55;
    margin-bottom: 0;
}

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F3F4F4; }
::-webkit-scrollbar-thumb { background: #C4899A; border-radius: 3px; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #853953 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data — silently, no success banner
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def init_data():
    load_data_to_mongo()
    return fetch_all_data()

with st.spinner("Loading data from MongoDB Atlas..."):
    try:
        df_full = init_data()
    except Exception as e:
        st.error(f"Database error: {e}")
        st.stop()

if df_full.empty:
    st.warning("No data found. Check that netflix_titles.csv is in the data/ folder.")
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
total   = len(df_full)
movies  = len(df_full[df_full["type"] == "Movie"])
shows   = len(df_full[df_full["type"] == "TV Show"])

st.markdown(f"""
<div class="page-header">
    <h1>Netflix Content Analytics</h1>
    <p>
        {total:,} titles &nbsp;·&nbsp;
        {movies:,} movies &nbsp;·&nbsp;
        {shows:,} TV shows &nbsp;·&nbsp;
        Data sourced from MongoDB Atlas
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filters")
    st.markdown("---")

    content_type = st.selectbox(
        "Content Type",
        options=["All", "Movie", "TV Show"],
    )

    all_genres = sorted(set(
        g.strip()
        for cell in df_full["listed_in"].dropna()
        for g in cell.split(",")
        if g.strip()
    ))
    selected_genres = st.multiselect("Genre", options=all_genres)

    all_countries = sorted(set(
        c.strip()
        for cell in df_full["country"].dropna()
        for c in cell.split(",")
        if c.strip() not in ["Unknown", ""]
    ))[:100]
    selected_countries = st.multiselect("Country", options=all_countries)

    min_year = int(df_full["release_year"].dropna().min())
    max_year = int(df_full["release_year"].dropna().max())
    year_range = st.slider(
        "Release Year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    all_ratings      = sorted(df_full["rating"].dropna().unique().tolist())
    selected_ratings = st.multiselect("Rating", options=all_ratings)

    st.markdown("---")
    actor_search    = st.text_input("Actor", placeholder="e.g. Adam Sandler")
    director_search = st.text_input("Director", placeholder="e.g. Steven Spielberg")

    st.markdown("---")
    if st.button("Reset Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown(
        f"<p style='color:#E8D5DA;font-size:0.78rem;line-height:1.6'>"
        f"Source: MongoDB Atlas<br>"
        f"Total records: {len(df_full):,}</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filters = {
    "content_type":    content_type,
    "genres":          selected_genres,
    "countries":       selected_countries,
    "year_range":      year_range,
    "ratings":         selected_ratings,
    "actor_search":    actor_search,
    "director_search": director_search,
}
df = apply_filters(df_full, filters)

is_filtered = len(df) < len(df_full)
if is_filtered:
    st.markdown(
        f"<p style='color:#853953;font-size:0.85rem;font-weight:500'>"
        f"Filters active — showing {len(df):,} of {len(df_full):,} titles</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.metric("Total Titles", f"{len(df):,}")
with k2:
    st.metric("Movies", f"{len(df[df['type'] == 'Movie']):,}")
with k3:
    st.metric("TV Shows", f"{len(df[df['type'] == 'TV Show']):,}")
with k4:
    n_countries = df["country"].dropna().str.split(", ").explode().nunique()
    st.metric("Countries", f"{n_countries:,}")
with k5:
    n_genres = df["listed_in"].dropna().str.split(", ").explode().nunique()
    st.metric("Genres", f"{n_genres:,}")
with k6:
    med_year = int(df["release_year"].dropna().median())
    st.metric("Median Year", f"{med_year}")

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------------------------
# Ratings reference data
# ---------------------------------------------------------------------------
RATINGS_INFO = [
    # (code, full name, description, applies to)
    ("TV-Y",   "All Children",               "Designed for very young audiences aged 2–6. Contains no content that would frighten young children.", "TV Shows"),
    ("TV-Y7",  "Older Children",             "Suitable for children aged 7 and above. May contain mild fantasy violence or comedic elements.", "TV Shows"),
    ("TV-G",   "General Audience",           "Suitable for all ages. Contains little or no violence, no strong language, and little or no sexual dialogue.", "TV Shows"),
    ("TV-PG",  "Parental Guidance",          "Contains material that parents may find unsuitable for younger children. May include mild violence, suggestive dialogue, or brief language.", "TV Shows"),
    ("TV-14",  "Parents Strongly Cautioned", "Contains material that many parents would find unsuitable for children under 14. Includes intense violence, sexual situations, or strong language.", "TV Shows"),
    ("TV-MA",  "Mature Audiences Only",      "Specifically designed for adults. May include graphic violence, explicit sexual activity, or crude language. Not suitable for children under 17.", "TV Shows"),
    ("G",      "General Audiences",          "All ages admitted. Contains nothing offensive. A film that is suitable for general audiences, including young children.", "Movies"),
    ("PG",     "Parental Guidance Suggested","Some material may not be suitable for children. May contain mild violence, language, or brief nudity.", "Movies"),
    ("PG-13",  "Parents Strongly Cautioned", "Some material may be inappropriate for children under 13. May include violence, nudity, sensuality, language, or adult activity.", "Movies"),
    ("R",      "Restricted",                 "Under 17 requires accompanying parent or adult guardian. Contains adult material including hard language, intense or persistent violence, sexual activity, or drug abuse.", "Movies"),
    ("NC-17",  "Adults Only",                "No one 17 and under admitted. Clearly adult content — not necessarily pornographic, but definitively not for children.", "Movies"),
    ("NR",     "Not Rated",                  "The content has not been submitted to or reviewed by a ratings board. Common for older films, foreign productions, or direct-to-streaming content.", "Movies & TV Shows"),
    ("UR",     "Unrated",                    "Similar to NR — the content has not been rated by the MPAA or TV ratings board. Often used for director's cuts or international releases.", "Movies & TV Shows"),
]

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "Overview",
    "Genres",
    "Countries",
    "Time Trends",
    "Cast & Directors",
    "Predictions",
    "Search",
    "Data",
])

# ── Tab 1 — Overview ─────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<p class="section-label">Content Overview</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">What is on Netflix?</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(pie_movies_vs_shows(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_rating_distribution(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(histogram_duration(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_rating_by_type(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Ratings Reference ──
    st.markdown('<p class="section-label" style="margin-top:32px">Rating Reference Guide</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">What do the content ratings mean?</p>', unsafe_allow_html=True)

    tv_ratings    = [r for r in RATINGS_INFO if r[3] == "TV Shows"]
    movie_ratings = [r for r in RATINGS_INFO if r[3] == "Movies"]
    both_ratings  = [r for r in RATINGS_INFO if r[3] == "Movies & TV Shows"]

    ref_col1, ref_col2 = st.columns(2)

    with ref_col1:
        st.markdown("<p style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#612D53;margin-bottom:12px'>TV Show Ratings</p>", unsafe_allow_html=True)
        for code, fullname, desc, applies in tv_ratings:
            st.markdown(f"""
            <div class="rating-card">
                <span class="rating-badge">{code}</span>
                <span class="rating-fullname">{fullname}</span>
                <p class="rating-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    with ref_col2:
        st.markdown("<p style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#612D53;margin-bottom:12px'>Movie Ratings</p>", unsafe_allow_html=True)
        for code, fullname, desc, applies in movie_ratings:
            st.markdown(f"""
            <div class="rating-card">
                <span class="rating-badge">{code}</span>
                <span class="rating-fullname">{fullname}</span>
                <p class="rating-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<p style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#612D53;margin-top:8px;margin-bottom:12px'>Applies to Both</p>", unsafe_allow_html=True)
    both_col1, both_col2 = st.columns(2)
    for i, (code, fullname, desc, applies) in enumerate(both_ratings):
        with both_col1 if i % 2 == 0 else both_col2:
            st.markdown(f"""
            <div class="rating-card">
                <span class="rating-badge">{code}</span>
                <span class="rating-fullname">{fullname}</span>
                <p class="rating-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


# ── Tab 2 — Genres ───────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<p class="section-label">Genre Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">How does content break down by genre?</p>', unsafe_allow_html=True)

    top_n = st.slider("Number of genres to display", 5, 25, 15, key="genre_n")

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(bar_top_genres(df, top_n=top_n), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_genre_type_comparison(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(line_genre_trends(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 3 — Countries ────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<p class="section-label">Geographic Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Where does Netflix content come from?</p>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(choropleth_countries(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_top_countries(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_country_type_split(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 4 — Time Trends ──────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<p class="section-label">Temporal Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">How has the Netflix catalog evolved?</p>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(line_titles_per_year(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_release_year(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_monthly_additions(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(heatmap_additions(df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 5 — Cast & Directors ─────────────────────────────────────────────────
with tabs[4]:
    st.markdown('<p class="section-label">Talent Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Who appears most frequently on Netflix?</p>', unsafe_allow_html=True)

    top_n_cast = st.slider("Top N to display", 5, 30, 15, key="cast_n")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_top_actors(df, top_n=top_n_cast), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(bar_top_directors(df, top_n=top_n_cast), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 6 — Predictions ──────────────────────────────────────────────────────
with tabs[5]:
    st.markdown('<p class="section-label">Predictive Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Where is Netflix headed?</p>', unsafe_allow_html=True)

    st.info(
        "These forecasts use linear regression trained on Netflix catalog growth from 2015 onwards. "
        "The shaded band represents one standard deviation of residual error. "
        "Treat these as directional projections, not guarantees."
    )

    years_ahead = st.slider("Years to forecast", 1, 10, 5, key="forecast_y")

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(forecast_titles(df_full, years_ahead=years_ahead), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(forecast_type_split(df_full, years_ahead=years_ahead), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 7 — Search ───────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown('<p class="section-label">Content Search</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Find a specific title</p>', unsafe_allow_html=True)

    search_term = st.text_input(
        "Search across title, description, cast, and director",
        placeholder="e.g. Breaking Bad, Quentin Tarantino, thriller...",
    )

    if search_term:
        term = search_term.lower()
        mask = (
            df_full["title"].str.lower().str.contains(term, na=False)
            | df_full["description"].str.lower().str.contains(term, na=False)
            | df_full["cast"].str.lower().str.contains(term, na=False)
            | df_full["director"].str.lower().str.contains(term, na=False)
        )
        results = df_full[mask].head(30)
        st.markdown(
            f"<p style='color:#853953;font-weight:500'>{len(results)} result(s) found</p>",
            unsafe_allow_html=True,
        )

        for _, row in results.iterrows():
            label = (
                f"{row.get('title', 'Unknown')}  —  "
                f"{row.get('type', '')}  "
                f"({int(row['release_year']) if pd.notnull(row.get('release_year')) else 'N/A'})"
            )
            with st.expander(label):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Type:** {row.get('type', 'N/A')}")
                    st.markdown(f"**Rating:** {row.get('rating', 'N/A')}")
                    st.markdown(f"**Duration:** {row.get('duration', 'N/A')}")
                    st.markdown(f"**Country:** {row.get('country', 'N/A')}")
                with c2:
                    st.markdown(f"**Director:** {row.get('director', 'N/A')}")
                    st.markdown(f"**Cast:** {str(row.get('cast', 'N/A'))[:120]}")
                    st.markdown(f"**Genres:** {row.get('listed_in', 'N/A')}")
                    st.markdown(f"**Date Added:** {row.get('date_added', 'N/A')}")
                st.markdown(f"*{row.get('description', '')}*")
    else:
        st.info("Type something above to search across all Netflix titles.")


# ── Tab 8 — Data ─────────────────────────────────────────────────────────────
with tabs[7]:
    st.markdown('<p class="section-label">Raw Data</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Browse the dataset</p>', unsafe_allow_html=True)

    display_cols = [
        "title", "type", "director", "cast",
        "country", "release_year", "rating",
        "duration", "listed_in", "date_added",
    ]
    available_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(df[available_cols].head(500), use_container_width=True, height=500)
    st.markdown(
        f"<p style='color:#888;font-size:0.82rem'>Showing first 500 of {len(df):,} filtered records</p>",
        unsafe_allow_html=True,
    )

    st.download_button(
        label     = "Download filtered data as CSV",
        data      = df[available_cols].to_csv(index=False),
        file_name = "netflix_filtered.csv",
        mime      = "text/csv",
    )