# CE49X Final Project - Task 3: Classification Report

## Dictionary-Based Classification Analysis

### Summary

- **Total Articles Analyzed**: 86
- **Articles with CE Areas**: 68
- **Articles with AI Technologies**: 14
- **Articles with Both**: 13

### Civil Engineering Areas Distribution

| CE Area | Count | Percentage |
|---------|-------|------------|
| Structural | 44 | 51.2% |
| Geotechnical | 25 | 29.1% |
| Transportation | 50 | 58.1% |
| Construction Management | 28 | 32.6% |
| Environmental Engineering | 41 | 47.7% |

### AI Technologies Distribution

| AI Technology | Count | Percentage |
|---------------|-------|------------|
| Computer Vision | 4 | 4.7% |
| Predictive Analytics | 6 | 7.0% |
| Generative Design | 0 | 0.0% |
| Robotics/Automation | 5 | 5.8% |

### Co-occurrence Matrix

The following table shows how often specific CE areas appear with specific AI technologies:

| CE Area | Computer Vision | Predictive Analytics | Generative Design | Robotics/Automation |
|---------|----------------|---------------------|-------------------|-------------------|
| Structural | 3 | 5 | 0 | 4 |
| Geotechnical | 1 | 3 | 0 | 2 |
| Transportation | 3 | 5 | 0 | 4 |
| Construction Management | 3 | 4 | 0 | 3 |
| Environmental Engineering | 4 | 4 | 0 | 4 |

### Temporal Trends

**Date Range**: 2025 - 2025

**Total Years Covered**: 1

**Top Combinations Over Time:**

- Geotechnical + Predictive Analytics: 1 articles
- Structural + Predictive Analytics: 1 articles
- Transportation + Predictive Analytics: 1 articles

### Key Findings

1. **Most Common CE Area**: Transportation (58.1% of articles)
2. **Most Common AI Technology**: Predictive Analytics (7.0% of articles)
3. **Most Common Combination**: Structural + Predictive Analytics
4. **Coverage**: 68 out of 86 articles (79.1%) were tagged with at least one CE area
5. **AI Integration**: 14 articles (16.3%) mention AI technologies in CE context

### Deliverables

1. **Tagging/Classification Script**: `scripts/classify_ce_ai.py`
2. **Tagged Articles**: `data/articles_tagged.csv`
3. **Analysis Results**: `data/classification_analysis.csv`
4. **Co-occurrence Heatmap**: `data/ce_ai_heatmap.png`
5. **Temporal Trends Data**: `data/temporal_trends.csv`
6. **Temporal Trends Visualization**: `data/temporal_trends.png`
7. **Classification Report**: `data/classification_report.md` (this file)
