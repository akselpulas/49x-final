"""
Analysis script that reads from PostgreSQL database instead of CSV.
Generates visualizations and co-occurrence matrices.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection

# Check and import required libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("ERROR: matplotlib or seaborn library is not installed.")
    print("Please install it using: pip install matplotlib seaborn")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# CE Areas and AI Technologies (same as original)
CE_AREAS = [
    "Structural", "Geotechnical", "Transportation", 
    "Construction Management", "Environmental Engineering"
]

AI_TECHNOLOGIES = [
    "Computer Vision", "Predictive Analytics", "Generative Design",
    "Robotics/Automation", "Machine Learning"
]


def load_articles_from_db() -> pd.DataFrame:
    """Load articles with classifications from PostgreSQL."""
    with get_db_cursor() as cur:
        query = """
            SELECT 
                a.id,
                a.title,
                a.published_at,
                a.source,
                a.url,
                a.content,
                a.description,
                c.ce_areas,
                c.ai_technologies,
                c.confidence_score,
                c.classification_method
            FROM articles a
            LEFT JOIN LATERAL (
                SELECT * FROM classifications 
                WHERE article_id = a.id 
                ORDER BY created_at DESC 
                LIMIT 1
            ) c ON TRUE
            WHERE c.id IS NOT NULL
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        # Convert to DataFrame
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'title': row['title'],
                'published_at': row['published_at'],
                'source': row['source'],
                'url': row['url'],
                'content': row['content'],
                'description': row['description'],
                'ce_areas': row['ce_areas'] or [],
                'ai_technologies': row['ai_technologies'] or [],
                'confidence_score': row['confidence_score'],
                'classification_method': row['classification_method']
            })
        
        return pd.DataFrame(data)


def create_cooccurrence_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Create co-occurrence matrix of CE Areas vs AI Technologies."""
    matrix = np.zeros((len(CE_AREAS), len(AI_TECHNOLOGIES)))
    
    for idx, row in df.iterrows():
        ce_areas = row.get('ce_areas', [])
        ai_techs = row.get('ai_technologies', [])
        
        if isinstance(ce_areas, str):
            ce_areas = [a.strip() for a in ce_areas.split(',') if a.strip()]
        if isinstance(ai_techs, str):
            ai_techs = [t.strip() for t in ai_techs.split(',') if t.strip()]
        
        for ce_area in ce_areas:
            if ce_area in CE_AREAS:
                ce_idx = CE_AREAS.index(ce_area)
                for ai_tech in ai_techs:
                    if ai_tech in AI_TECHNOLOGIES:
                        ai_idx = AI_TECHNOLOGIES.index(ai_tech)
                        matrix[ce_idx][ai_idx] += 1
    
    cooccurrence_df = pd.DataFrame(
        matrix,
        index=CE_AREAS,
        columns=AI_TECHNOLOGIES
    )
    
    return cooccurrence_df


def save_cooccurrence_to_db(cooccurrence_df: pd.DataFrame):
    """Save co-occurrence matrix to database."""
    with get_db_cursor() as cur:
        # Clear existing data
        cur.execute("DELETE FROM cooccurrence_matrix")
        
        # Insert new data
        for ce_area in CE_AREAS:
            for ai_tech in AI_TECHNOLOGIES:
                count = int(cooccurrence_df.loc[ce_area, ai_tech])
                cur.execute("""
                    INSERT INTO cooccurrence_matrix (ce_area, ai_technology, count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (ce_area, ai_technology) 
                    DO UPDATE SET count = EXCLUDED.count, last_updated = CURRENT_TIMESTAMP
                """, (ce_area, ai_tech, count))


def create_heatmap(cooccurrence_df: pd.DataFrame, output_path: Path):
    """Create heatmap visualization."""
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        cooccurrence_df,
        annot=True,
        fmt='.0f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Number of Articles'},
        linewidths=0.5
    )
    plt.title('Co-occurrence Matrix: Civil Engineering Areas vs AI Technologies', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('AI Technologies', fontsize=12, fontweight='bold')
    plt.ylabel('Civil Engineering Areas', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved heatmap to {output_path}")


def create_bar_chart(df: pd.DataFrame, output_path: Path, chart_type: str = 'ce'):
    """Create bar chart for CE areas or AI technologies."""
    if chart_type == 'ce':
        counts = {}
        for ce_area in CE_AREAS:
            count = df['ce_areas'].apply(
                lambda x: ce_area in (x if isinstance(x, list) else [])
            ).sum()
            counts[ce_area] = count
        title = 'Number of Articles by Civil Engineering Area'
        color = 'steelblue'
        edge_color = 'navy'
    else:
        counts = {}
        for ai_tech in AI_TECHNOLOGIES:
            count = df['ai_technologies'].apply(
                lambda x: ai_tech in (x if isinstance(x, list) else [])
            ).sum()
            counts[ai_tech] = count
        title = 'Number of Articles by AI Technology'
        color = 'coral'
        edge_color = 'darkred'
    
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_items)
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, values, color=color, edgecolor=edge_color, linewidth=1.5)
    
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(int(value)), ha='center', va='bottom', fontweight='bold')
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(title.split(' by ')[1] if ' by ' in title else '', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Articles', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved bar chart to {output_path}")


def analyze_temporal_trends(df: pd.DataFrame):
    """Analyze and save temporal trends to database."""
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    df = df.dropna(subset=['published_at'])
    df['year_month'] = df['published_at'].dt.to_period('M')
    
    with get_db_cursor() as cur:
        # Clear existing trends
        cur.execute("DELETE FROM temporal_trends")
        
        # Calculate trends
        for period in df['year_month'].unique():
            period_str = str(period)
            period_date = pd.to_datetime(period_str).date()
            
            for ce_area in CE_AREAS:
                count = len(df[
                    (df['year_month'] == period) &
                    (df['ce_areas'].apply(lambda x: ce_area in (x if isinstance(x, list) else [])))
                ])
                if count > 0:
                    cur.execute("""
                        INSERT INTO temporal_trends (period, ce_area, article_count)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (period, ce_area, ai_technology) 
                        DO UPDATE SET article_count = EXCLUDED.article_count
                    """, (period_date, ce_area, count))


def main():
    """Main analysis function."""
    print("=" * 70)
    print("CE49X Final Project - Database-based Analysis")
    print("=" * 70)
    print()
    
    if not test_connection():
        print("ERROR: Cannot connect to PostgreSQL database.")
        print("Make sure Docker containers are running: docker-compose up -d")
        return
    
    print("Loading articles from database...")
    df = load_articles_from_db()
    
    if len(df) == 0:
        print("No classified articles found in database.")
        print("Please run classify_with_llm.py first to classify articles.")
        return
    
    print(f"Loaded {len(df)} classified articles")
    
    # Create co-occurrence matrix
    print("\nCreating co-occurrence matrix...")
    cooccurrence_df = create_cooccurrence_matrix(df)
    print("\nCo-occurrence Matrix (CE Areas vs AI Technologies):")
    print(cooccurrence_df)
    
    # Save to database
    save_cooccurrence_to_db(cooccurrence_df)
    
    # Save to CSV (for compatibility)
    cooccurrence_file = RESULTS_DIR / "cooccurrence_matrix.csv"
    cooccurrence_df.to_csv(cooccurrence_file)
    print(f"\n[OK] Saved co-occurrence matrix to {cooccurrence_file}")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    heatmap_path = RESULTS_DIR / "heatmap_ce_ai.png"
    create_heatmap(cooccurrence_df, heatmap_path)
    
    bar_chart_ce_path = RESULTS_DIR / "bar_chart_ce_areas.png"
    create_bar_chart(df, bar_chart_ce_path, chart_type='ce')
    
    bar_chart_ai_path = RESULTS_DIR / "bar_chart_ai_technologies.png"
    create_bar_chart(df, bar_chart_ai_path, chart_type='ai')
    
    # Analyze temporal trends
    print("\nAnalyzing temporal trends...")
    analyze_temporal_trends(df)
    print("[OK] Temporal trends saved to database")
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("Analysis Summary")
    print("=" * 70)
    
    print(f"\nTotal classified articles: {len(df)}")
    
    print("\nTop Civil Engineering Areas by Article Count:")
    ce_summary = {}
    for ce_area in CE_AREAS:
        count = df['ce_areas'].apply(
            lambda x: ce_area in (x if isinstance(x, list) else [])
        ).sum()
        ce_summary[ce_area] = count
    
    for area, count in sorted(ce_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f"  {area}: {count} articles ({percentage:.1f}%)")
    
    print("\nTop AI Technologies by Article Count:")
    ai_summary = {}
    for ai_tech in AI_TECHNOLOGIES:
        count = df['ai_technologies'].apply(
            lambda x: ai_tech in (x if isinstance(x, list) else [])
        ).sum()
        ai_summary[ai_tech] = count
    
    for tech, count in sorted(ai_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f"  {tech}: {count} articles ({percentage:.1f}%)")
    
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

