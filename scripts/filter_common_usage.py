"""
CE49X Final Project - Filter Common Usage Articles
This script filters articles that have BOTH CE area AND AI technology classifications.

Author: [Your Name]
Course: CE49X - Introduction to Data Science for Civil Engineering
Date: Fall 2025
"""

import pandas as pd
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "data" / "classified_articles.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "common_usage_articles.csv"

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Filter articles that have both CE area and AI technology classifications.
    """
    print("=" * 70)
    print("Filtering Articles with Common Usage (CE + AI)")
    print("=" * 70)
    print()
    
    # Load classified articles
    print(f"Loading data from {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} total articles")
    except Exception as e:
        print(f"ERROR: Failed to load CSV file: {e}")
        return
    
    # Filter for articles with both classifications
    # is_classified = True means both ce_area_count > 0 AND ai_tech_count > 0
    filtered_df = df[df['is_classified'] == True].copy()
    
    print(f"\nArticles with CE classification only: {df['ce_area_count'].gt(0).sum()}")
    print(f"Articles with AI classification only: {df['ai_tech_count'].gt(0).sum()}")
    print(f"Articles with BOTH classifications: {len(filtered_df)}")
    
    # Save filtered data
    print(f"\nSaving filtered data to {OUTPUT_FILE}...")
    try:
        filtered_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        print(f"[OK] Saved {len(filtered_df)} articles with common usage")
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("Common Usage Summary")
    print("=" * 70)
    
    # Count by CE area
    print("\nCommon Usage by Civil Engineering Area:")
    ce_summary = {}
    for ce_area in ["Structural", "Geotechnical", "Transportation", "Construction Management", "Environmental Engineering"]:
        count = filtered_df['ce_areas'].astype(str).str.contains(ce_area, na=False).sum()
        if count > 0:
            ce_summary[ce_area] = count
    
    for area, count in sorted(ce_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        print(f"  {area}: {count} articles ({percentage:.1f}%)")
    
    # Count by AI technology
    print("\nCommon Usage by AI Technology:")
    ai_summary = {}
    for ai_tech in ["Computer Vision", "Predictive Analytics", "Generative Design", "Robotics/Automation", "Machine Learning"]:
        count = filtered_df['ai_technologies'].astype(str).str.contains(ai_tech, na=False).sum()
        if count > 0:
            ai_summary[ai_tech] = count
    
    for tech, count in sorted(ai_summary.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        print(f"  {tech}: {count} articles ({percentage:.1f}%)")
    
    # Top combinations
    print("\nTop 10 CE Area + AI Technology Combinations:")
    combinations = {}
    for idx, row in filtered_df.iterrows():
        ce_areas = str(row['ce_areas']).split(', ') if pd.notna(row['ce_areas']) else []
        ai_techs = str(row['ai_technologies']).split(', ') if pd.notna(row['ai_technologies']) else []
        for ce in ce_areas:
            if ce and ce.strip():
                for ai in ai_techs:
                    if ai and ai.strip():
                        combo = f"{ce.strip()} + {ai.strip()}"
                        combinations[combo] = combinations.get(combo, 0) + 1
    
    for combo, count in sorted(combinations.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        print(f"  {combo}: {count} articles ({percentage:.1f}%)")
    
    print("\n" + "=" * 70)
    print(f"Filtered {len(filtered_df)} articles saved to: {OUTPUT_FILE}")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

