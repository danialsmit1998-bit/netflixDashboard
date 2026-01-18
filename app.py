import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {background-color: #0f0f0f; color: #ffffff;}
    .metric-card {
        background: linear-gradient(135deg, #e50914 0%, #b20710 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        color: white;
    }
    .header-title {
        text-align: center;
        color: #e50914;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    h2 {color: #e50914; border-bottom: 2px solid #e50914; padding-bottom: 10px;}
    h3 {color: #ffffff;}
    </style>
    """, unsafe_allow_html=True)

# Load and clean data
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('netflix_titles.csv')
    
    # Convert date_added to datetime
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    
    # Remove rows with null values
    df_clean = df.dropna()
    
    return df, df_clean

df_original, df = load_and_clean_data()

# Dashboard Header
st.markdown('<div class="header-title">🎬 NETFLIX CONTENT ANALYSIS DASHBOARD</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #b3b3b3; font-size: 1.1em;">Comprehensive Data Insights & Analytics</p>', unsafe_allow_html=True)
st.divider()

# Data Cleaning Summary
st.markdown("## 🧹 DATA CLEANING SUMMARY")
col_clean1, col_clean2, col_clean3 = st.columns(3)

with col_clean1:
    original_rows = len(df_original)
    st.metric("Original Rows", f"{original_rows:,}")

with col_clean2:
    cleaned_rows = len(df)
    st.metric("Cleaned Rows", f"{cleaned_rows:,}")

with col_clean3:
    removed = original_rows - cleaned_rows
    pct_removed = (removed / original_rows) * 100
    st.metric("Rows Removed", f"{removed:,}", f"{pct_removed:.1f}%")

st.divider()

# Sidebar filters
st.sidebar.markdown("## 📊 FILTERS")
content_types = sorted(df['type'].unique().tolist())
selected_content_types = st.sidebar.multiselect(
    "Content Type",
    options=content_types,
    default=content_types
)

min_year, max_year = st.sidebar.slider(
    "Release Year Range",
    int(df['release_year'].min()),
    int(df['release_year'].max()),
    (int(df['release_year'].min()), int(df['release_year'].max()))
)

# Apply filters to clean data
df_filtered = df[
    (df['type'].isin(selected_content_types)) &
    (df['release_year'].between(min_year, max_year))
]

# Key Metrics
st.markdown("## 📊 KEY METRICS")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Titles", f"{len(df_filtered):,}")

with col2:
    movies = len(df_filtered[df_filtered['type'] == 'Movie'])
    st.metric("Movies", f"{movies:,}")

with col3:
    shows = len(df_filtered[df_filtered['type'] == 'TV Show'])
    st.metric("TV Shows", f"{shows:,}")

with col4:
    countries = df_filtered['country'].str.split(', ').explode().nunique()
    st.metric("Countries", f"{countries:,}")

with col5:
    genres = df_filtered['listed_in'].str.split(', ').explode().nunique()
    st.metric("Genres", f"{genres:,}")

st.divider()

# Row 1: Content Distribution & Release Trends
st.markdown("## 📈 CONTENT OVERVIEW")
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📺 Content Type Distribution")
    type_dist = df_filtered['type'].value_counts()
    fig_type = px.pie(
        values=type_dist.values,
        names=type_dist.index,
        color_discrete_sequence=['#e50914', '#221f1f'],
        hole=0.4
    )
    fig_type.update_traces(textinfo='percent+label', textposition='auto')
    fig_type.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=400,
        showlegend=True
    )
    st.plotly_chart(fig_type, use_container_width=True)

with row1_col2:
    st.subheader("📈 Content Added Over Time")
    added_trend = df_filtered.groupby(df_filtered['date_added'].dt.year).size()
    fig_trend = px.bar(
        x=added_trend.index,
        y=added_trend.values,
        labels={'x': 'Year', 'y': 'Number of Titles'},
        color_discrete_sequence=['#e50914']
    )
    fig_trend.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        hovermode='x unified',
        xaxis_title="Year Added",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Row 2: Top Genres & Ratings
st.markdown("## 🎭 GENRES & RATINGS ANALYSIS")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Top 15 Genres")
    genres_list = df_filtered['listed_in'].str.split(', ').explode()
    top_genres = genres_list.value_counts().head(15)
    fig_genres = px.bar(
        x=top_genres.values,
        y=top_genres.index,
        orientation='h',
        color=top_genres.values,
        color_continuous_scale='Reds',
        labels={'x': 'Count', 'y': 'Genre'}
    )
    fig_genres.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        showlegend=False,
        xaxis_title="Number of Titles"
    )
    st.plotly_chart(fig_genres, use_container_width=True)

with row2_col2:
    st.subheader("Content Ratings Distribution")
    rating_dist = df_filtered['rating'].value_counts().sort_values(ascending=False).head(10)
    fig_rating = px.bar(
        x=rating_dist.index,
        y=rating_dist.values,
        labels={'x': 'Rating', 'y': 'Count'},
        color_discrete_sequence=['#e50914']
    )
    fig_rating.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig_rating, use_container_width=True)

# Row 3: Top Countries & Release Year Analysis
st.markdown("## 🌍 GEOGRAPHICAL & TEMPORAL ANALYSIS")
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("Top 15 Production Countries")
    countries_list = df_filtered['country'].str.split(', ').explode()
    top_countries = countries_list.value_counts().head(15)
    fig_countries = px.bar(
        x=top_countries.values,
        y=top_countries.index,
        orientation='h',
        color=top_countries.values,
        color_continuous_scale='Blues',
        labels={'x': 'Count', 'y': 'Country'}
    )
    fig_countries.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        showlegend=False,
        xaxis_title="Number of Titles"
    )
    st.plotly_chart(fig_countries, use_container_width=True)

with row3_col2:
    st.subheader("Release Year Distribution")
    release_dist = df_filtered['release_year'].value_counts().sort_index()
    fig_release = px.bar(
        x=release_dist.index,
        y=release_dist.values,
        labels={'x': 'Release Year', 'y': 'Count'},
        color_discrete_sequence=['#e50914']
    )
    fig_release.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig_release, use_container_width=True)

# Row 4: Duration Analysis
st.markdown("## ⏱️ DURATION ANALYSIS")
row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    # Movie durations
    movies_df = df_filtered[df_filtered['type'] == 'Movie'].copy()
    if len(movies_df) > 0:
        movies_df['duration_min'] = movies_df['duration'].str.extract(r'(\d+)').astype(float)
        
        st.subheader("Movie Duration Distribution")
        fig_movie_dur = px.histogram(
            movies_df,
            x='duration_min',
            nbins=30,
            labels={'duration_min': 'Duration (minutes)'},
            color_discrete_sequence=['#e50914']
        )
        fig_movie_dur.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=350,
            hovermode='x unified'
        )
        st.plotly_chart(fig_movie_dur, use_container_width=True)
        
        # Stats
        avg_duration = movies_df['duration_min'].mean()
        st.write(f"**Average Movie Duration:** {avg_duration:.0f} minutes")
    else:
        st.info("No movies in selected filters")

with row4_col2:
    # TV show seasons
    shows_df = df_filtered[df_filtered['type'] == 'TV Show'].copy()
    if len(shows_df) > 0:
        shows_df['seasons'] = shows_df['duration'].str.extract(r'(\d+)').astype(float)
        
        st.subheader("TV Show Seasons Distribution")
        fig_show_dur = px.histogram(
            shows_df,
            x='seasons',
            nbins=20,
            labels={'seasons': 'Number of Seasons'},
            color_discrete_sequence=['#e50914']
        )
        fig_show_dur.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=350,
            hovermode='x unified'
        )
        st.plotly_chart(fig_show_dur, use_container_width=True)
        
        # Stats
        avg_seasons = shows_df['seasons'].mean()
        st.write(f"**Average Number of Seasons:** {avg_seasons:.1f}")
    else:
        st.info("No TV shows in selected filters")

st.divider()

# Analysis Insights
st.markdown("## 💡 KEY INSIGHTS")

col_insight1, col_insight2, col_insight3 = st.columns(3)

with col_insight1:
    movies_count = len(df_filtered[df_filtered['type'] == 'Movie'])
    shows_count = len(df_filtered[df_filtered['type'] == 'TV Show'])
    if shows_count > 0:
        ratio = movies_count / shows_count
        st.info(f"**Content Mix**: {ratio:.2f}x more movies than TV shows")
    else:
        st.info(f"**Content Mix**: Only movies selected")

with col_insight2:
    if len(df_filtered) > 0:
        top_genre = df_filtered['listed_in'].str.split(', ').explode().value_counts().index[0]
        st.info(f"**Most Popular Genre**: {top_genre}")
    else:
        st.warning("No data available")

with col_insight3:
    if len(df_filtered) > 0:
        avg_year = df_filtered['release_year'].mean()
        st.info(f"**Average Release Year**: {int(avg_year)}")
    else:
        st.warning("No data available")

st.divider()

# Detailed Data Table
st.markdown("## 📋 DETAILED DATA TABLE")
display_cols = ['type', 'title', 'director', 'country', 'release_year', 'rating', 'listed_in', 'duration']
st.dataframe(df_filtered[display_cols].head(100), use_container_width=True, height=400)

