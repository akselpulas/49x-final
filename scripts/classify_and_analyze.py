"""
CE49X Final Project - Task 3: Categorization & Trend Analysis
Classification and Trend Analysis Script

This script classifies articles by:
- Civil Engineering Areas (Structural, Geotechnical, Transportation, etc.)
- AI Technologies (Computer Vision, Machine Learning, etc.)
- Creates co-occurrence matrix
- Analyzes temporal trends
- Generates visualizations (heatmaps, bar charts)

Author: [Your Name]
Course: CE49X - Introduction to Data Science for Civil Engineering
Date: Fall 2025
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import re

# Check and import required libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("ERROR: matplotlib or seaborn library is not installed.")
    print("Please install it using: pip install matplotlib seaborn")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "data_raw" / "newsapi_articles.csv"
OUTPUT_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = OUTPUT_DIR / "classified_articles.csv"
RESULTS_DIR = PROJECT_ROOT / "results"

# ============================================================================
# KEYWORD DICTIONARIES FOR CLASSIFICATION
# ============================================================================

# Civil Engineering Areas Keywords
CE_AREAS = {
    "Structural": [
        "structural", "structure", "building", "construction", "design", "analysis",
        "health monitoring", "materials", "steel", "concrete", "beam", "column",
        "foundation", "load", "stress", "strain", "reinforcement", "bridge",
        "skyscraper", "building code", "structural engineering"
    ],
    "Geotechnical": [
        "geotechnical", "soil", "foundation", "tunnel", "excavation", "slope",
        "retaining wall", "earthquake", "seismic", "ground", "subsoil", "rock",
        "geology", "settlement", "bearing capacity", "pile", "deep foundation",
        "underground", "mining", "landslide"
    ],
    "Transportation": [
        "transportation", "traffic", "road", "highway", "autonomous vehicle",
        "logistics", "infrastructure", "urban planning", "smart city", "mobility",
        "public transport", "railway", "airport", "port", "transit", "commute",
        "traffic management", "parking", "pedestrian", "cycling"
    ],
    "Construction Management": [
        "construction management", "scheduling", "safety", "cost estimation",
        "site monitoring", "project management", "bim", "building information modeling",
        "procurement", "quality control", "risk assessment", "contractor",
        "construction site", "workflow", "productivity"
    ],
    "Environmental Engineering": [
        "environmental", "sustainability", "waste management", "green building",
        "recycling", "water treatment", "air quality", "climate", "carbon",
        "renewable energy", "solar", "wind", "energy efficiency", "leed",
        "sustainable design", "pollution", "environmental impact"
    ]
}

# AI Technologies Keywords
AI_TECHNOLOGIES = {
    "Computer Vision": [
        "computer vision", "image recognition", "drone inspection", "safety monitoring",
        "visual inspection", "image processing", "object detection", "camera",
        "surveillance", "monitoring system", "visual", "photogrammetry", "lidar"
    ],
    "Predictive Analytics": [
        "predictive analytics", "risk assessment", "maintenance prediction",
        "forecasting", "prediction", "predictive model", "early warning",
        "failure prediction", "condition monitoring", "prognostics"
    ],
    "Generative Design": [
        "generative design", "optimization", "parametric modeling", "algorithmic design",
        "design optimization", "topology optimization", "automated design", "cad",
        "3d modeling", "parametric", "optimization algorithm"
    ],
    "Robotics/Automation": [
        "robotics", "automation", "robot", "automated", "brick laying robot",
        "autonomous machinery", "drone", "uav", "robotic", "automated construction",
        "3d printing", "additive manufacturing", "automated system"
    ],
    "Machine Learning": [
        "machine learning", "neural network", "deep learning", "ai model",
        "artificial intelligence", "ml", "algorithm", "training data", "model",
        "supervised learning", "unsupervised learning", "reinforcement learning"
    ]
}

# ============================================================================
# CLASSIFICATION FUNCTIONS
# ============================================================================

def normalize_text_for_matching(text: str) -> str:
    """
    Normalize text for keyword matching.
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text string
    """
    if pd.isna(text):
        return ""
    
    text = str(text).lower()
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def classify_text(text: str, keyword_dict: Dict[str, List[str]]) -> List[str]:
    """
    Classify text based on keyword dictionary.
    
    Args:
        text: Input text to classify
        keyword_dict: Dictionary mapping categories to keyword lists
        
    Returns:
        List of matching categories
    """
    normalized_text = normalize_text_for_matching(text)
    if not normalized_text:
        return []
    
    matches = []
    for category, keywords in keyword_dict.items():
        for keyword in keywords:
            # Check for exact phrase match (for multi-word keywords)
            if ' ' in keyword:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, normalized_text):
                    matches.append(category)
                    break
            else:
                # Single word match
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, normalized_text):
                    matches.append(category)
                    break
    
    return list(set(matches))  # Remove duplicates


def classify_article(row: pd.Series) -> Dict:
    """
    Classify a single article by CE area and AI technology.
    
    Args:
        row: DataFrame row containing article data
        
    Returns:
        Dictionary with classification results
    """
    # Combine all text fields for classification
    text_fields = []
    for field in ['title', 'description', 'full_text', 'processed_text']:
        if field in row and pd.notna(row[field]):
            text_fields.append(str(row[field]))
    
    combined_text = ' '.join(text_fields)
    
    # Classify by CE area
    ce_areas = classify_text(combined_text, CE_AREAS)
    
    # Classify by AI technology
    ai_techs = classify_text(combined_text, AI_TECHNOLOGIES)
    
    return {
        'ce_areas': ce_areas,
        'ai_technologies': ai_techs,
        'ce_area_count': len(ce_areas),
        'ai_tech_count': len(ai_techs),
        'is_classified': len(ce_areas) > 0 and len(ai_techs) > 0
    }


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def create_cooccurrence_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create co-occurrence matrix of CE Areas vs AI Technologies.
    
    Args:
        df: DataFrame with classified articles
        
    Returns:
        Co-occurrence matrix as DataFrame
    """
    # Initialize matrix
    ce_areas_list = list(CE_AREAS.keys())
    ai_techs_list = list(AI_TECHNOLOGIES.keys())
    
    matrix = np.zeros((len(ce_areas_list), len(ai_techs_list)))
    
    # Count co-occurrences
    for idx, row in df.iterrows():
        ce_areas = row.get('ce_areas', [])
        ai_techs = row.get('ai_technologies', [])
        
        if isinstance(ce_areas, str):
            ce_areas = [a.strip() for a in ce_areas.split(',') if a.strip()]
        if isinstance(ai_techs, str):
            ai_techs = [t.strip() for t in ai_techs.split(',') if t.strip()]
        
        for ce_area in ce_areas:
            if ce_area in ce_areas_list:
                ce_idx = ce_areas_list.index(ce_area)
                for ai_tech in ai_techs:
                    if ai_tech in ai_techs_list:
                        ai_idx = ai_techs_list.index(ai_tech)
                        matrix[ce_idx][ai_idx] += 1
    
    # Create DataFrame
    cooccurrence_df = pd.DataFrame(
        matrix,
        index=ce_areas_list,
        columns=ai_techs_list
    )
    
    return cooccurrence_df


def analyze_temporal_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze trends over time.
    
    Args:
        df: DataFrame with classified articles
        
    Returns:
        DataFrame with temporal trends
    """
    # Parse dates
    df['date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Extract year-month
    df['year_month'] = df['date'].dt.to_period('M')
    
    # Count articles by CE area and month
    trends = []
    for ce_area in CE_AREAS.keys():
        for period in df['year_month'].unique():
            count = len(df[
                (df['year_month'] == period) &
                (df['ce_areas'].astype(str).str.contains(ce_area, na=False))
            ])
            trends.append({
                'period': str(period),
                'ce_area': ce_area,
                'count': count
            })
    
    trends_df = pd.DataFrame(trends)
    return trends_df


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_heatmap(cooccurrence_df: pd.DataFrame, output_path: Path):
    """
    Create heatmap visualization of CE Areas vs AI Technologies.
    
    Args:
        cooccurrence_df: Co-occurrence matrix DataFrame
        output_path: Path to save the heatmap
    """
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


def create_bar_chart(df: pd.DataFrame, output_path: Path):
    """
    Create bar chart showing number of articles per CE area.
    
    Args:
        df: DataFrame with classified articles
        output_path: Path to save the chart
    """
    # Count articles by CE area
    ce_counts = {}
    for ce_area in CE_AREAS.keys():
        count = df['ce_areas'].astype(str).str.contains(ce_area, na=False).sum()
        ce_counts[ce_area] = count
    
    # Sort by count
    sorted_areas = sorted(ce_counts.items(), key=lambda x: x[1], reverse=True)
    areas, counts = zip(*sorted_areas)
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(areas, counts, color='steelblue', edgecolor='navy', linewidth=1.5)
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(int(count)), ha='center', va='bottom', fontweight='bold')
    
    plt.title('Number of Articles by Civil Engineering Area', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Civil Engineering Area', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Articles', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved bar chart to {output_path}")


def create_ai_tech_chart(df: pd.DataFrame, output_path: Path):
    """
    Create bar chart showing number of articles per AI technology.
    
    Args:
        df: DataFrame with classified articles
        output_path: Path to save the chart
    """
    # Count articles by AI technology
    ai_counts = {}
    for ai_tech in AI_TECHNOLOGIES.keys():
        count = df['ai_technologies'].astype(str).str.contains(ai_tech, na=False).sum()
        ai_counts[ai_tech] = count
    
    # Sort by count
    sorted_techs = sorted(ai_counts.items(), key=lambda x: x[1], reverse=True)
    techs, counts = zip(*sorted_techs)
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(techs, counts, color='coral', edgecolor='darkred', linewidth=1.5)
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(int(count)), ha='center', va='bottom', fontweight='bold')
    
    plt.title('Number of Articles by AI Technology', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('AI Technology', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Articles', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved AI technology chart to {output_path}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function to classify articles and analyze trends.
    """
    print("=" * 70)
    print("CE49X Final Project - Task 3: Classification & Trend Analysis")
    print("=" * 70)
    print()
    
    # Check if input file exists
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print(f"Loading data from {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} articles")
    except Exception as e:
        print(f"ERROR: Failed to load CSV file: {e}")
        return
    
    # Classify articles
    print("\nClassifying articles...")
    classification_results = []
    
    for idx, row in df.iterrows():
        if (idx + 1) % 200 == 0:
            print(f"  Classified {idx + 1}/{len(df)} articles...")
        
        result = classify_article(row)
        classification_results.append(result)
    
    # Add classification columns to dataframe
    df['ce_areas'] = [', '.join(r['ce_areas']) if r['ce_areas'] else '' for r in classification_results]
    df['ai_technologies'] = [', '.join(r['ai_technologies']) if r['ai_technologies'] else '' for r in classification_results]
    df['ce_area_count'] = [r['ce_area_count'] for r in classification_results]
    df['ai_tech_count'] = [r['ai_tech_count'] for r in classification_results]
    df['is_classified'] = [r['is_classified'] for r in classification_results]
    
    print(f"\n[OK] Classification complete")
    print(f"  Articles with CE area classification: {df['ce_area_count'].gt(0).sum()}")
    print(f"  Articles with AI tech classification: {df['ai_tech_count'].gt(0).sum()}")
    print(f"  Articles with both classifications: {df['is_classified'].sum()}")
    
    # Save classified data
    print(f"\nSaving classified data to {OUTPUT_FILE}...")
    try:
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        print(f"[OK] Saved {len(df)} classified articles")
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return
    
    # Create co-occurrence matrix
    print("\nCreating co-occurrence matrix...")
    cooccurrence_df = create_cooccurrence_matrix(df)
    print("\nCo-occurrence Matrix (CE Areas vs AI Technologies):")
    print(cooccurrence_df)
    
    # Save co-occurrence matrix
    cooccurrence_file = RESULTS_DIR / "cooccurrence_matrix.csv"
    cooccurrence_df.to_csv(cooccurrence_file)
    print(f"\n[OK] Saved co-occurrence matrix to {cooccurrence_file}")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    # Heatmap
    heatmap_path = RESULTS_DIR / "heatmap_ce_ai.png"
    create_heatmap(cooccurrence_df, heatmap_path)
    
    # Bar chart for CE areas
    bar_chart_path = RESULTS_DIR / "bar_chart_ce_areas.png"
    create_bar_chart(df, bar_chart_path)
    
    # Bar chart for AI technologies
    ai_chart_path = RESULTS_DIR / "bar_chart_ai_technologies.png"
    create_ai_tech_chart(df, ai_chart_path)
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("Classification Summary")
    print("=" * 70)
    
    print("\nTop Civil Engineering Areas by Article Count:")
    ce_summary = {}
    for ce_area in CE_AREAS.keys():
        count = df['ce_areas'].astype(str).str.contains(ce_area, na=False).sum()
        ce_summary[ce_area] = count
    
    for area, count in sorted(ce_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f"  {area}: {count} articles ({percentage:.1f}%)")
    
    print("\nTop AI Technologies by Article Count:")
    ai_summary = {}
    for ai_tech in AI_TECHNOLOGIES.keys():
        count = df['ai_technologies'].astype(str).str.contains(ai_tech, na=False).sum()
        ai_summary[ai_tech] = count
    
    for tech, count in sorted(ai_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f"  {tech}: {count} articles ({percentage:.1f}%)")
    
    # Find most common combinations
    print("\nTop 10 CE Area + AI Technology Combinations:")
    combinations = {}
    for idx, row in df.iterrows():
        if row['is_classified']:
            ce_areas = row['ce_areas'].split(', ') if row['ce_areas'] else []
            ai_techs = row['ai_technologies'].split(', ') if row['ai_technologies'] else []
            for ce in ce_areas:
                for ai in ai_techs:
                    combo = f"{ce} + {ai}"
                    combinations[combo] = combinations.get(combo, 0) + 1
    
    for combo, count in sorted(combinations.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {combo}: {count} articles")
    
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)
    print(f"\nOutput files saved to:")
    print(f"  - Classified data: {OUTPUT_FILE}")
    print(f"  - Co-occurrence matrix: {cooccurrence_file}")
    print(f"  - Heatmap: {heatmap_path}")
    print(f"  - CE Areas bar chart: {bar_chart_path}")
    print(f"  - AI Technologies bar chart: {ai_chart_path}")
    print()


if __name__ == "__main__":
    main()

