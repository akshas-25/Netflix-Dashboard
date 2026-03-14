"""
charts.py
---------
All Plotly chart functions.
Color palette:
  #F3F4F4  cream background
  #853953  dusty rose — primary
  #612D53  deep plum  — secondary
  #2C2C2C  near-black  — text
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
CREAM   = "#F3F4F4"
ROSE    = "#853953"
PLUM    = "#612D53"
DARK    = "#2C2C2C"
MID     = "#A0566B"
LIGHT   = "#C4899A"
PALE    = "#E8D5DA"

CHART_COLORS = [ROSE, PLUM, MID, "#B5446E", LIGHT, "#7A3048", "#D4A0B0",
                "#4A1535", "#CF6F8A", "#3D0F2F"]

# ---------------------------------------------------------------------------
# Shared layout
# ---------------------------------------------------------------------------
LAYOUT = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(243,244,244,0.5)",
    font          = dict(family="Inter, sans-serif", color=DARK, size=12),
    margin        = dict(l=40, r=40, t=50, b=40),
    colorway      = CHART_COLORS,
    legend        = dict(
        bgcolor     = "rgba(255,255,255,0.85)",
        bordercolor = "#D0C0C8",
        borderwidth = 1,
        font        = dict(color=DARK, size=11),
    ),
)

AXIS = dict(
    gridcolor     = "rgba(133,57,83,0.10)",
    linecolor     = "#D0C0C8",
    tickfont      = dict(color="#666666", size=11),
    title_font    = dict(color="#555555", size=12),
    zerolinecolor = "rgba(133,57,83,0.15)",
)

def _layout(fig, title="", height=400):
    fig.update_layout(
        **LAYOUT,
        height = height,
        title  = dict(
            text = f"<b>{title}</b>",
            font = dict(size=14, color=DARK),
            x    = 0,
            xanchor = "left",
        ),
    )
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(**AXIS)
    return fig


# ---------------------------------------------------------------------------
# 1. Movies vs TV Shows — donut
# ---------------------------------------------------------------------------
def pie_movies_vs_shows(df: pd.DataFrame) -> go.Figure:
    counts = df["type"].value_counts().reset_index()
    counts.columns = ["Type", "Count"]
    fig = px.pie(
        counts, names="Type", values="Count",
        color_discrete_sequence=[ROSE, PLUM],
        hole=0.60,
    )
    fig.update_traces(
        textinfo  = "percent+label",
        textfont  = dict(size=13, color=DARK),
        marker    = dict(line=dict(color=CREAM, width=3)),
        hovertemplate = "<b>%{label}</b><br>%{value:,} titles<br>%{percent}<extra></extra>",
    )
    fig.add_annotation(
        text="Content<br>Split", x=0.5, y=0.5,
        font=dict(size=13, color=DARK), showarrow=False,
    )
    return _layout(fig, "Content Type Split", height=380)


# ---------------------------------------------------------------------------
# 2. Rating distribution
# ---------------------------------------------------------------------------
def bar_rating_distribution(df: pd.DataFrame) -> go.Figure:
    counts = (
        df["rating"].value_counts()
        .reset_index()
        .rename(columns={"rating": "Rating", "count": "Count"})
    )
    counts = counts[~counts["Rating"].isin(["Unknown", "Not Rated", "NR", "UR"])]
    counts = counts.sort_values("Count", ascending=False)

    fig = px.bar(
        counts, x="Rating", y="Count",
        color="Rating",
        color_discrete_sequence=CHART_COLORS,
        text="Count",
    )
    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        marker_line_width=0,
    )
    fig.update_layout(showlegend=False)
    return _layout(fig, "Content Rating Distribution", height=380)


# ---------------------------------------------------------------------------
# 3. Duration histogram
# ---------------------------------------------------------------------------
def histogram_duration(df: pd.DataFrame) -> go.Figure:
    movies = df[df["type"] == "Movie"]["duration_int"].dropna()
    shows  = df[df["type"] == "TV Show"]["duration_int"].dropna()

    fig = go.Figure()
    if not movies.empty:
        fig.add_trace(go.Histogram(
            x=movies, name="Movies",
            marker_color=ROSE, opacity=0.85, nbinsx=40,
            hovertemplate="Duration: %{x} min<br>Count: %{y}<extra></extra>",
        ))
    if not shows.empty:
        fig.add_trace(go.Histogram(
            x=shows, name="TV Shows (seasons)",
            marker_color=PLUM, opacity=0.85, nbinsx=15,
            hovertemplate="Seasons: %{x}<br>Count: %{y}<extra></extra>",
        ))
    fig.update_layout(barmode="overlay")
    return _layout(fig, "Duration Distribution", height=360)


# ---------------------------------------------------------------------------
# 4. Top genres — horizontal bar
# ---------------------------------------------------------------------------
def bar_top_genres(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    genres = df["listed_in"].dropna().str.split(", ").explode().str.strip()
    counts = genres.value_counts().head(top_n).reset_index()
    counts.columns = ["Genre", "Count"]

    fig = px.bar(
        counts, x="Count", y="Genre",
        orientation="h",
        color="Count",
        color_continuous_scale=[[0, PALE], [0.5, ROSE], [1, PLUM]],
        text="Count",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", marker_line_width=0)
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    return _layout(fig, f"Top {top_n} Genres by Title Count", height=520)


# ---------------------------------------------------------------------------
# 5. Genre trends over time
# ---------------------------------------------------------------------------
def line_genre_trends(df: pd.DataFrame, top_n: int = 6) -> go.Figure:
    df2 = df.dropna(subset=["year_added", "listed_in"]).copy()
    df2["genre_list"] = df2["listed_in"].str.split(", ")
    exploded   = df2.explode("genre_list")
    top_genres = exploded["genre_list"].value_counts().head(top_n).index.tolist()
    filtered   = exploded[exploded["genre_list"].isin(top_genres)]
    grouped    = (
        filtered.groupby(["year_added", "genre_list"])
        .size().reset_index(name="Count")
    )
    grouped["year_added"] = grouped["year_added"].astype(int)
    grouped = grouped[grouped["year_added"] >= 2010]

    fig = px.line(
        grouped, x="year_added", y="Count", color="genre_list",
        color_discrete_sequence=CHART_COLORS, markers=True,
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
    return _layout(fig, "Genre Popularity Trends Over Time", height=420)


# ---------------------------------------------------------------------------
# 6. Genre breakdown — Movies vs TV Shows stacked
# ---------------------------------------------------------------------------
def bar_genre_type_comparison(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    df2 = df.dropna(subset=["listed_in", "type"]).copy()
    df2["genre_list"] = df2["listed_in"].str.split(", ")
    exploded   = df2.explode("genre_list")
    top_genres = exploded["genre_list"].value_counts().head(top_n).index.tolist()
    filtered   = exploded[exploded["genre_list"].isin(top_genres)]
    grouped    = (
        filtered.groupby(["genre_list", "type"])
        .size().reset_index(name="Count")
    )

    fig = px.bar(
        grouped, x="genre_list", y="Count", color="type",
        barmode="group",
        color_discrete_map={"Movie": ROSE, "TV Show": PLUM},
        text="Count",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", marker_line_width=0)
    fig.update_xaxes(tickangle=-35)
    return _layout(fig, "Genre Breakdown — Movies vs TV Shows", height=440)


# ---------------------------------------------------------------------------
# 7. Top countries
# ---------------------------------------------------------------------------
def bar_top_countries(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    countries = (
        df["country"].dropna()
        .pipe(lambda s: s[s != "Unknown"])
        .str.split(", ").explode().str.strip()
    )
    counts = countries.value_counts().head(top_n).reset_index()
    counts.columns = ["Country", "Count"]

    fig = px.bar(
        counts, x="Count", y="Country",
        orientation="h",
        color="Count",
        color_continuous_scale=[[0, PALE], [0.5, ROSE], [1, PLUM]],
        text="Count",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", marker_line_width=0)
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    return _layout(fig, f"Top {top_n} Content-Producing Countries", height=520)


# ---------------------------------------------------------------------------
# 8. Choropleth
# ---------------------------------------------------------------------------
def choropleth_countries(df: pd.DataFrame) -> go.Figure:
    countries = (
        df["country"].dropna()
        .pipe(lambda s: s[s != "Unknown"])
        .str.split(", ").explode().str.strip()
    )
    counts = countries.value_counts().reset_index()
    counts.columns = ["Country", "Count"]

    fig = px.choropleth(
        counts, locations="Country", locationmode="country names",
        color="Count",
        color_continuous_scale=[[0, PALE], [0.4, ROSE], [1, PLUM]],
        hover_name="Country",
        hover_data={"Count": ":,"},
    )
    fig.update_geos(
        showcoastlines=True,  coastlinecolor="#BBBBBB",
        showland=True,        landcolor="#E8E4E8",
        showocean=True,       oceancolor="#D8E4EC",
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_coloraxes(colorbar=dict(tickfont=dict(color=DARK)))
    return _layout(fig, "Global Content Distribution Map", height=460)


# ---------------------------------------------------------------------------
# 9. Country content type comparison
# ---------------------------------------------------------------------------
def bar_country_type_split(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    df2 = df.dropna(subset=["country", "type"]).copy()
    df2 = df2[df2["country"] != "Unknown"]
    df2["primary_country"] = df2["country"].str.split(", ").str[0].str.strip()
    top_countries = df2["primary_country"].value_counts().head(top_n).index.tolist()
    filtered = df2[df2["primary_country"].isin(top_countries)]
    grouped  = (
        filtered.groupby(["primary_country", "type"])
        .size().reset_index(name="Count")
    )

    fig = px.bar(
        grouped, x="primary_country", y="Count", color="type",
        barmode="stack",
        color_discrete_map={"Movie": ROSE, "TV Show": PLUM},
        text="Count",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="inside", marker_line_width=0)
    fig.update_xaxes(tickangle=-30)
    return _layout(fig, "Movies vs TV Shows by Country (Top 10)", height=420)


# ---------------------------------------------------------------------------
# 10. Titles added per year
# ---------------------------------------------------------------------------
def line_titles_per_year(df: pd.DataFrame) -> go.Figure:
    data   = df.dropna(subset=["year_added"])
    counts = (
        data.groupby(["year_added", "type"])
        .size().reset_index(name="Count")
    )
    counts["year_added"] = counts["year_added"].astype(int)
    counts = counts[counts["year_added"] >= 2010]

    fig = px.line(
        counts, x="year_added", y="Count", color="type",
        color_discrete_map={"Movie": ROSE, "TV Show": PLUM},
        markers=True,
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
    return _layout(fig, "Titles Added to Netflix Per Year", height=400)


# ---------------------------------------------------------------------------
# 11. Release year distribution
# ---------------------------------------------------------------------------
def bar_release_year(df: pd.DataFrame) -> go.Figure:
    counts = (
        df.dropna(subset=["release_year"])
        .groupby(["release_year", "type"])
        .size().reset_index(name="Count")
    )
    counts["release_year"] = counts["release_year"].astype(int)
    counts = counts[counts["release_year"] >= 1990]

    fig = px.bar(
        counts, x="release_year", y="Count", color="type",
        barmode="stack",
        color_discrete_map={"Movie": ROSE, "TV Show": PLUM},
    )
    fig.update_traces(marker_line_width=0)
    return _layout(fig, "Titles by Release Year", height=380)


# ---------------------------------------------------------------------------
# 12. Content added by month (seasonality)
# ---------------------------------------------------------------------------
def bar_monthly_additions(df: pd.DataFrame) -> go.Figure:
    data = df.dropna(subset=["month_added"]).copy()
    month_names = {
        1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
        7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec",
    }
    data["month_name"] = data["month_added"].map(month_names)
    counts = (
        data.groupby(["month_added", "month_name", "type"])
        .size().reset_index(name="Count")
    )
    counts = counts.sort_values("month_added")

    fig = px.bar(
        counts, x="month_name", y="Count", color="type",
        barmode="group",
        color_discrete_map={"Movie": ROSE, "TV Show": PLUM},
    )
    fig.update_traces(marker_line_width=0)
    return _layout(fig, "Content Additions by Month (Seasonality)", height=380)


# ---------------------------------------------------------------------------
# 13. Top actors
# ---------------------------------------------------------------------------
def bar_top_actors(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    cast = (
        df["cast"].dropna()
        .pipe(lambda s: s[s != "Unknown"])
        .str.split(", ").explode().str.strip()
    )
    counts = cast.value_counts().head(top_n).reset_index()
    counts.columns = ["Actor", "Count"]

    fig = px.bar(
        counts, x="Count", y="Actor",
        orientation="h",
        color="Count",
        color_continuous_scale=[[0, PALE], [0.5, ROSE], [1, PLUM]],
        text="Count",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", marker_line_width=0)
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    return _layout(fig, f"Top {top_n} Most Frequent Actors", height=520)


# ---------------------------------------------------------------------------
# 14. Top directors
# ---------------------------------------------------------------------------
def bar_top_directors(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    directors = (
        df["director"].dropna()
        .pipe(lambda s: s[s != "Unknown"])
        .str.split(", ").explode().str.strip()
    )
    counts = directors.value_counts().head(top_n).reset_index()
    counts.columns = ["Director", "Count"]

    fig = px.bar(
        counts, x="Count", y="Director",
        orientation="h",
        color="Count",
        color_continuous_scale=[[0, PALE], [0.5, ROSE], [1, PLUM]],
        text="Count",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", marker_line_width=0)
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    return _layout(fig, f"Top {top_n} Most Frequent Directors", height=520)


# ---------------------------------------------------------------------------
# 15. Rating split — Movies vs TV Shows side by side
# ---------------------------------------------------------------------------
def bar_rating_by_type(df: pd.DataFrame) -> go.Figure:
    counts = (
        df[~df["rating"].isin(["Unknown", "Not Rated", "NR", "UR"])]
        .groupby(["rating", "type"])
        .size().reset_index(name="Count")
    )
    fig = px.bar(
        counts, x="rating", y="Count", color="type",
        barmode="group",
        color_discrete_map={"Movie": ROSE, "TV Show": PLUM},
        text="Count",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", marker_line_width=0)
    return _layout(fig, "Ratings — Movies vs TV Shows Compared", height=400)


# ---------------------------------------------------------------------------
# 16. Forecast — total titles
# ---------------------------------------------------------------------------
def forecast_titles(df: pd.DataFrame, years_ahead: int = 5) -> go.Figure:
    from sklearn.linear_model import LinearRegression

    data   = df.dropna(subset=["year_added"])
    counts = (
        data.groupby("year_added")
        .size().reset_index(name="Count")
    )
    # Only use years with reasonable data (Netflix became major ~2015)
    counts = counts[counts["year_added"] >= 2015].copy()
    counts["year_added"] = counts["year_added"].astype(int)

    X = counts["year_added"].values.reshape(-1, 1)
    y = counts["Count"].values

    model = LinearRegression()
    model.fit(X, y)

    last_year    = int(counts["year_added"].max())
    future_years = np.arange(last_year + 1, last_year + years_ahead + 1)
    predictions  = np.maximum(model.predict(future_years.reshape(-1, 1)), 0)

    residuals = y - model.predict(X)
    std_err   = np.std(residuals)

    fig = go.Figure()

    # Actual
    fig.add_trace(go.Scatter(
        x=counts["year_added"], y=counts["Count"],
        mode="lines+markers", name="Actual",
        line=dict(color=ROSE, width=3),
        marker=dict(size=9, color=ROSE),
        hovertemplate="Year: %{x}<br>Titles: %{y:,}<extra></extra>",
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=future_years, y=predictions,
        mode="lines+markers", name="Forecast",
        line=dict(color=PLUM, width=3, dash="dash"),
        marker=dict(size=9, color=PLUM, symbol="diamond"),
        hovertemplate="Year: %{x}<br>Forecast: %{y:,.0f}<extra></extra>",
    ))

    # Confidence band
    upper = predictions + std_err
    lower = np.maximum(predictions - std_err, 0)
    fig.add_trace(go.Scatter(
        x=np.concatenate([future_years, future_years[::-1]]),
        y=np.concatenate([upper, lower[::-1]]),
        fill="toself",
        fillcolor="rgba(133,57,83,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Confidence Range",
        hoverinfo="skip",
    ))

    return _layout(fig, f"Netflix Catalog Growth Forecast — Next {years_ahead} Years", height=420)


# ---------------------------------------------------------------------------
# 17. Forecast — Movies vs TV Shows split
# ---------------------------------------------------------------------------
def forecast_type_split(df: pd.DataFrame, years_ahead: int = 5) -> go.Figure:
    from sklearn.linear_model import LinearRegression

    data   = df.dropna(subset=["year_added"])
    counts = (
        data.groupby(["year_added", "type"])
        .size().reset_index(name="Count")
    )
    counts["year_added"] = counts["year_added"].astype(int)
    counts = counts[counts["year_added"] >= 2015]

    last_year    = int(counts["year_added"].max())
    future_years = np.arange(last_year + 1, last_year + years_ahead + 1)

    fig = go.Figure()
    styles = {
        "Movie":   {"color": ROSE,  "dash": "dash",  "symbol": "diamond"},
        "TV Show": {"color": PLUM,  "dash": "dot",   "symbol": "square"},
    }

    for content_type, style in styles.items():
        subset = counts[counts["type"] == content_type].sort_values("year_added")
        if subset.empty:
            continue

        X     = subset["year_added"].values.reshape(-1, 1)
        y     = subset["Count"].values
        model = LinearRegression()
        model.fit(X, y)
        preds = np.maximum(model.predict(future_years.reshape(-1, 1)), 0)

        # Historical
        fig.add_trace(go.Scatter(
            x=subset["year_added"], y=subset["Count"],
            mode="lines+markers", name=f"{content_type} — actual",
            line=dict(color=style["color"], width=2.5),
            marker=dict(size=8, color=style["color"]),
            hovertemplate=f"{content_type}<br>Year: %{{x}}<br>Titles: %{{y:,}}<extra></extra>",
        ))
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_years, y=preds,
            mode="lines+markers", name=f"{content_type} — forecast",
            line=dict(color=style["color"], width=2, dash=style["dash"]),
            marker=dict(size=8, color=style["color"], symbol=style["symbol"]),
            hovertemplate=f"{content_type} forecast<br>Year: %{{x}}<br>Titles: %{{y:,.0f}}<extra></extra>",
        ))

    return _layout(fig, "Movies vs TV Shows — Trend Forecast", height=420)


# ---------------------------------------------------------------------------
# 18. Heatmap — content added by year and month
# ---------------------------------------------------------------------------
def heatmap_additions(df: pd.DataFrame) -> go.Figure:
    data = df.dropna(subset=["year_added", "month_added"]).copy()
    data = data[data["year_added"] >= 2015]
    pivot = (
        data.groupby(["year_added", "month_added"])
        .size().reset_index(name="Count")
        .pivot(index="month_added", columns="year_added", values="Count")
        .fillna(0)
    )
    month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]

    fig = go.Figure(go.Heatmap(
        z    = pivot.values,
        x    = [str(int(c)) for c in pivot.columns],
        y    = [month_names[int(i)-1] for i in pivot.index],
        colorscale = [[0, CREAM], [0.4, LIGHT], [0.7, ROSE], [1, PLUM]],
        hovertemplate = "Year: %{x}<br>Month: %{y}<br>Titles Added: %{z:,}<extra></extra>",
        showscale = True,
    ))
    return _layout(fig, "Content Addition Heatmap — Year vs Month", height=380)