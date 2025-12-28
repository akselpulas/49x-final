# CE49X Final Project - Code List

This documentation lists all scripts used during the project in chronological order.

---

## 📂 Script Categories

### 1. Data Collection Scripts

| Script Name | File Path | Purpose | Output |
|------------|-----------|---------|--------|
| `collect_newsapi.py` | `scripts/collect_newsapi.py` | Collect articles from NewsAPI | `data/newsapi_articles_*.csv` |
| `collect_guardian.py` | `scripts/collect_guardian.py` | Collect articles from Guardian API | `data/guardian_articles_*.csv` |
| `collect_rss.py` | `scripts/collect_rss.py` | Collect articles from RSS feeds | `data/rss_articles_*.csv` |
| `collect_nytimes.py` | `scripts/collect_nytimes.py` | Collect articles from New York Times API | `data/nytimes_articles_*.csv` |
| `import_corpus_to_db.py` | `scripts/import_corpus_to_db.py` | Import corpus data to database | Database |

---

### 2. Preprocessing Scripts

| Script Name | File Path | Purpose | Output |
|------------|-----------|---------|--------|
| `preprocess_newsapi.py` | `scripts/preprocess_newsapi.py` | Clean NewsAPI data | Processed data |
| `generate_preprocessing_report.py` | `scripts/generate_preprocessing_report.py` | ✅ NEW - Generate Task 2 reports | `data/top20_most_frequent_words.csv`, `data/top20_bigrams.csv`, `data/preprocessing_report.md` |
| `create_cleaned_dataset.py` | `scripts/create_cleaned_dataset.py` | ✅ NEW - Create cleaned dataset | `data/cleaned_dataset.csv` |
| `filter_ai_ce_articles.py` | `scripts/filter_ai_ce_articles.py` | Filter AI/CE intersection | `data/filtered_ai_ce_articles.csv` |
| `filter_common_usage.py` | `scripts/filter_common_usage.py` | Filter common usage | `data/common_usage_articles.csv` |

---

### 3. Validation Scripts

| Script Name | Status | Purpose | Output |
|------------|--------|---------|--------|
| `validate_guardian_ce_keywords.py` | ❌ Deleted | Validate Guardian articles with LLM | `data/guardian_ce_keyword_validation.csv` |
| `revalidate_guardian_flexible.py` | ❌ Deleted | Flexible Guardian validation | `data/guardian_ce_keyword_validation_flexible.csv` |
| `save_guardian_valid.py` | ❌ Deleted | Save valid Guardian articles | `data/guardian_valid.csv` |
| `validate_corpus_ce.py` | ❌ Deleted | Validate corpus articles | `data/corpus_valid.csv` |
| `validate_newsapi_flexible.py` | ✅ Available | NewsAPI flexible validation | `data/newsapi_validation_flexible.csv` |
| `validate_newsapi_comprehensive_flexible.py` | ✅ Available | NewsAPI comprehensive validation | `data/newsapi_validation_comprehensive.csv` |
| `validate_newsapi_ce_ai_intersection.py` | ✅ Available | CE-AI intersection check | `data/newsapi_ce_ai_validation.csv` |
| `validate_newsapi_ai_ce_intersection.py` | ✅ Available | AI-CE intersection check | `data/newsapi_ai_ce_validation.csv` |
| `create_newsapi_valid_from_validation.py` | ❌ Deleted | Create valid NewsAPI articles | `data/newsapi_valid.csv` |

---

### 4. Classification Scripts

| Script Name | Status | Purpose | Output |
|------------|--------|---------|--------|
| `classify_ce_ai.py` | ❌ Deleted | Dictionary-based classification | `data/articles_tagged.csv` |
| `classify_ce_ai_llm.py` | ❌ Deleted | LLM-based classification | `data/articles_tagged_llm.csv` |
| `retag_untagged_articles.py` | ❌ Deleted | Re-tag untagged articles | Updated database |
| `classify_and_analyze.py` | ✅ Available | Classification analysis | `data/classification_analysis.csv` |
| `classify_with_llm.py` | ✅ Available | Classification with LLM | Classification results |
| `generate_classification_report.py` | ❌ Deleted | Classification report | `data/classification_report.md` |

---

### 5. Database Management Scripts

| Script Name | Status | Purpose | Output |
|------------|--------|---------|--------|
| `migrate_to_postgres.py` | ✅ Available | Migration from SQLite to PostgreSQL | PostgreSQL database |
| `import_newsapi_csv_to_db.py` | ✅ Available | Import NewsAPI CSVs to database | `newsapi_articles` table |
| `save_valid_newsapi_to_db.py` | ❌ Deleted | Save valid NewsAPI articles | `newsapi_valid` table |
| `merge_all_valid_to_db.py` | ❌ Deleted | Merge all valid articles | `all_valid_articles` table |
| `add_abstracts_to_unified_table.py` | ❌ Deleted | Merge abstracts | Updated `all_valid_articles` |
| `remove_duplicates_from_unified_table.py` | ❌ Deleted | Remove duplicates | Cleaned `all_valid_articles` |
| `generate_abstracts_for_unified_table.py` | ❌ Deleted | Generate abstracts with LLM | Updated `all_valid_articles` |
| `complete_missing_abstracts_and_renumber_ids.py` | ✅ Available | Complete abstracts + ID renumbering | Final `all_valid_articles` |
| `remove_columns_from_unified_table.py` | ✅ Available | Remove unnecessary columns | Cleaned table structure |
| `reorder_columns_id_first.py` | ✅ Available | Move ID column to beginning | Reordered table |

---

### 6. Visualization Scripts

| Script Name | Status | Purpose | Output |
|------------|--------|---------|--------|
| `create_normalized_ce_ai_heatmap.py` | ❌ Deleted | Normalized heatmap | `data/heatmap_ce_ai_specialization_LQ.png` |
| `create_dual_ce_ai_heatmaps.py` | ❌ Deleted | Dual heatmaps (raw + normalized) | `data/heatmap_ce_ai_*.png` |
| `time_series_analysis.py` | ❌ Deleted | Time series analysis | `data/time_series_*.png` |
| `temporal_trends_analysis.py` | ❌ Deleted | Temporal trend analysis | `data/temporal_trends.png` |
| `create_bump_chart_combinations.py` | ❌ Deleted | Bump chart | `data/bump_chart_top10_combinations.png` |
| `create_emergence_scatter.py` | ❌ Deleted | Emergence scatter plot | `data/emergence_scatter_*.png` |
| `analyze_longtail_distribution.py` | ❌ Deleted | Long-tail analysis | `data/loglog_pareto_*.png` |
| `create_source_combination_heatmap.py` | ❌ Deleted | Source combination heatmap | `data/heatmap_source_by_combination.png` |
| `create_wordclouds_by_ce_area.py` | ❌ Deleted | CE area word clouds | `data/wc_*_ai.png` |
| `create_ai_wordclouds_and_contrast.py` | ❌ Deleted | AI word clouds + contrast | `data/wc_*.png` |
| `create_ce_area_top_terms_csv.py` | ❌ Deleted | Top terms CSVs | `data/top_terms_*.csv` |
| `create_keyword_network_graphs.py` | ❌ Deleted | Network graphs | `data/network_*.png` |
| `analyze_ai_specialization_lq.py` | ❌ Deleted | Location Quotient analysis | `data/heatmap_ce_ai_specialization_LQ.png` |
| `rank_ce_areas_by_ai_maturity.py` | ❌ Deleted | AI maturity ranking | `data/ce_ai_maturity_ranking.png` |
| `analyze_from_db.py` | ✅ Available | Analysis from database | Various outputs |

---

### 7. Abstract/Summary Scripts

| Script Name | Status | Purpose | Output |
|------------|--------|---------|--------|
| `add_abstracts.py` | ✅ Available | Add abstracts | Updated articles |
| `add_abstracts_filtered.py` | ✅ Available | Add abstracts to filtered articles | Updated articles |
| `add_summaries_newsapi.py` | ✅ Available | Add summaries to NewsAPI articles | Updated articles |

---

### 8. Duplicate Detection Scripts

| Script Name | Status | Purpose | Output |
|------------|--------|---------|--------|
| `detect_duplicates_by_summary.py` | ✅ Available | Summary-based duplicate detection | `data/duplicate_articles_*.csv` |

---

### 9. Helper Scripts

| Script Name | Status | Purpose |
|------------|--------|---------|
| `llm_api.py` | ✅ Available | LLM API wrapper |
| `collect_articles.py` | ✅ Available | General article collection |
| `collect_articles_advanced.py` | ✅ Available | Advanced article collection |
| `collect_articles_search.py` | ✅ Available | Search-based collection |
| `collect_articles_db.py` | ✅ Available | Collection from database |

---

## 🔄 Execution Order (Chronological)

### Phase 1: Data Collection
1. `collect_newsapi.py` - Collect NewsAPI data
2. `collect_guardian.py` - Collect Guardian data
3. `collect_rss.py` - Collect from RSS feeds
4. `import_corpus_to_db.py` - Import corpus data

### Phase 2: Validation
5. `validate_newsapi_flexible.py` - NewsAPI validation
6. `validate_newsapi_comprehensive_flexible.py` - Comprehensive validation
7. `validate_newsapi_ce_ai_intersection.py` - Intersection check
8. `create_newsapi_valid_from_validation.py` - Create valid articles

### Phase 2.5: Text Preprocessing (Task 2) ✅ NEW
9. `generate_preprocessing_report.py` - Top 20 words and bi-grams reports
10. `create_cleaned_dataset.py` - Create cleaned dataset

### Phase 3: Classification
11. `classify_ce_ai_llm.py` - Classification with LLM
12. `retag_untagged_articles.py` - Complete missing tags

### Phase 4: Database Merging
13. `import_newsapi_csv_to_db.py` - Import NewsAPI to database
14. `merge_all_valid_to_db.py` - Merge all valid articles
15. `remove_duplicates_from_unified_table.py` - Remove duplicates
16. `complete_missing_abstracts_and_renumber_ids.py` - Abstract + ID editing

### Phase 5: Analysis and Visualization
17. `create_dual_ce_ai_heatmaps.py` - Heatmaps
18. `time_series_analysis.py` - Time series
19. `create_bump_chart_combinations.py` - Bump chart
20. `create_emergence_scatter.py` - Emergence analysis
21. `analyze_longtail_distribution.py` - Long-tail analysis
22. `create_source_combination_heatmap.py` - Source analysis
23. `create_wordclouds_by_ce_area.py` - Word clouds
24. `create_ai_wordclouds_and_contrast.py` - AI word clouds
25. `create_keyword_network_graphs.py` - Network graphs
26. `analyze_ai_specialization_lq.py` - LQ analysis
27. `rank_ce_areas_by_ai_maturity.py` - Final ranking

### Phase 6: Cleanup
28. `remove_columns_from_unified_table.py` - Remove unnecessary columns
29. `reorder_columns_id_first.py` - Move ID to beginning

---

## 📊 Current Status

**Total Script Count:** ~32+ scripts
**Active Scripts:** ~17 scripts
**Deleted/Merged Scripts:** ~15 scripts
**Final Database:** `all_valid_articles` (1155 articles)
**Final Table Structure:** 15 columns

**Newly Added Scripts (Task 2):**
- `generate_preprocessing_report.py` - Preprocessing reports
- `create_cleaned_dataset.py` - Cleaned dataset creation

---

## 📌 Important Note: About "Deleted" Status

In this documentation, **"❌ Deleted"** means:

- ✅ **Script was used** - Executed during conversation and fulfilled its function
- ✅ **Function completed** - Required analysis/data processing was done, outputs were created
- ✅ **Later deleted** - File was removed from filesystem after function completion during cleanup

**Examples:**
- `classify_ce_ai_llm.py` → All articles classified, results transferred to database, script deleted
- `create_wordclouds_by_ce_area.py` → 5 word clouds created, images saved, script deleted
- `rank_ce_areas_by_ai_maturity.py` → Final ranking analysis performed, visualization created, script deleted

**These are NOT unused scripts!** All scripts were actively used during the conversation and contributed to project results.

---

**Note:** Some scripts may have been deleted or merged during the conversation. This list is based on conversation history.

