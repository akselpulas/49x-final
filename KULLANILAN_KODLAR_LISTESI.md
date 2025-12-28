# CE49X Final Project - Kullanılan Kodlar Listesi

Bu dokümantasyon, proje süresince kullanılan tüm scriptleri kronolojik sırayla listeler.

---

## 📂 Script Kategorileri

### 1. Veri Toplama Scriptleri (Data Collection)

| Script Adı | Dosya Yolu | Amaç | Çıktı |
|------------|------------|------|-------|
| `collect_newsapi.py` | `scripts/collect_newsapi.py` | NewsAPI'den makale toplama | `data/newsapi_articles_*.csv` |
| `collect_guardian.py` | `scripts/collect_guardian.py` | Guardian API'den makale toplama | `data/guardian_articles_*.csv` |
| `collect_rss.py` | `scripts/collect_rss.py` | RSS feed'lerden makale toplama | `data/rss_articles_*.csv` |
| `collect_nytimes.py` | `scripts/collect_nytimes.py` | New York Times API'den makale toplama | `data/nytimes_articles_*.csv` |
| `import_corpus_to_db.py` | `scripts/import_corpus_to_db.py` | Corpus verilerini DB'ye aktarma | Database |

---

### 2. Veri Ön İşleme Scriptleri (Preprocessing)

| Script Adı | Dosya Yolu | Amaç | Çıktı |
|------------|------------|------|-------|
| `preprocess_newsapi.py` | `scripts/preprocess_newsapi.py` | NewsAPI verilerini temizleme | Processed data |
| `generate_preprocessing_report.py` | `scripts/generate_preprocessing_report.py` | ✅ YENİ - Task 2 raporları oluşturma | `data/top20_most_frequent_words.csv`, `data/top20_bigrams.csv`, `data/preprocessing_report.md` |
| `create_cleaned_dataset.py` | `scripts/create_cleaned_dataset.py` | ✅ YENİ - Cleaned dataset oluşturma | `data/cleaned_dataset.csv` |
| `filter_ai_ce_articles.py` | `scripts/filter_ai_ce_articles.py` | AI/CE kesişimini filtreleme | `data/filtered_ai_ce_articles.csv` |
| `filter_common_usage.py` | `scripts/filter_common_usage.py` | Genel kullanım filtreleme | `data/common_usage_articles.csv` |

---

### 3. Validasyon Scriptleri (Validation)

| Script Adı | Durum | Amaç | Çıktı |
|------------|-------|------|-------|
| `validate_guardian_ce_keywords.py` | ❌ Silindi | Guardian makalelerini LLM ile validasyon | `data/guardian_ce_keyword_validation.csv` |
| `revalidate_guardian_flexible.py` | ❌ Silindi | Esnek Guardian validasyonu | `data/guardian_ce_keyword_validation_flexible.csv` |
| `save_guardian_valid.py` | ❌ Silindi | Valid Guardian makalelerini kaydetme | `data/guardian_valid.csv` |
| `validate_corpus_ce.py` | ❌ Silindi | Corpus makalelerini validasyon | `data/corpus_valid.csv` |
| `validate_newsapi_flexible.py` | ✅ Mevcut | NewsAPI esnek validasyon | `data/newsapi_validation_flexible.csv` |
| `validate_newsapi_comprehensive_flexible.py` | ✅ Mevcut | NewsAPI kapsamlı validasyon | `data/newsapi_validation_comprehensive.csv` |
| `validate_newsapi_ce_ai_intersection.py` | ✅ Mevcut | CE-AI kesişim kontrolü | `data/newsapi_ce_ai_validation.csv` |
| `validate_newsapi_ai_ce_intersection.py` | ✅ Mevcut | AI-CE kesişim kontrolü | `data/newsapi_ai_ce_validation.csv` |
| `create_newsapi_valid_from_validation.py` | ❌ Silindi | Valid NewsAPI makalelerini oluşturma | `data/newsapi_valid.csv` |

---

### 4. Sınıflandırma Scriptleri (Classification)

| Script Adı | Durum | Amaç | Çıktı |
|------------|-------|------|-------|
| `classify_ce_ai.py` | ❌ Silindi | Dictionary-based classification | `data/articles_tagged.csv` |
| `classify_ce_ai_llm.py` | ❌ Silindi | LLM-based classification | `data/articles_tagged_llm.csv` |
| `retag_untagged_articles.py` | ❌ Silindi | Taglenmemiş makaleleri yeniden tagleme | Updated database |
| `classify_and_analyze.py` | ✅ Mevcut | Classification analizi | `data/classification_analysis.csv` |
| `classify_with_llm.py` | ✅ Mevcut | LLM ile sınıflandırma | Classification results |
| `generate_classification_report.py` | ❌ Silindi | Classification raporu | `data/classification_report.md` |

---

### 5. Veritabanı Yönetim Scriptleri (Database Management)

| Script Adı | Durum | Amaç | Çıktı |
|------------|-------|------|-------|
| `migrate_to_postgres.py` | ✅ Mevcut | SQLite'den PostgreSQL'e migrasyon | PostgreSQL database |
| `import_newsapi_csv_to_db.py` | ✅ Mevcut | NewsAPI CSV'lerini DB'ye aktarma | `newsapi_articles` table |
| `save_valid_newsapi_to_db.py` | ❌ Silindi | Valid NewsAPI makalelerini kaydetme | `newsapi_valid` table |
| `merge_all_valid_to_db.py` | ❌ Silindi | Tüm valid makaleleri birleştirme | `all_valid_articles` table |
| `add_abstracts_to_unified_table.py` | ❌ Silindi | Abstract'leri birleştirme | Updated `all_valid_articles` |
| `remove_duplicates_from_unified_table.py` | ❌ Silindi | Duplicate'leri kaldırma | Cleaned `all_valid_articles` |
| `generate_abstracts_for_unified_table.py` | ❌ Silindi | LLM ile abstract oluşturma | Updated `all_valid_articles` |
| `complete_missing_abstracts_and_renumber_ids.py` | ✅ Mevcut | Abstract tamamlama + ID renumbering | Final `all_valid_articles` |
| `remove_columns_from_unified_table.py` | ✅ Mevcut | Gereksiz kolonları kaldırma | Cleaned table structure |
| `reorder_columns_id_first.py` | ✅ Mevcut | ID kolonunu başa alma | Reordered table |

---

### 6. Görselleştirme Scriptleri (Visualization)

| Script Adı | Durum | Amaç | Çıktı |
|------------|-------|------|-------|
| `create_normalized_ce_ai_heatmap.py` | ❌ Silindi | Normalize heatmap | `data/heatmap_ce_ai_specialization_LQ.png` |
| `create_dual_ce_ai_heatmaps.py` | ❌ Silindi | Dual heatmaps (raw + normalized) | `data/heatmap_ce_ai_*.png` |
| `time_series_analysis.py` | ❌ Silindi | Zaman serisi analizi | `data/time_series_*.png` |
| `temporal_trends_analysis.py` | ❌ Silindi | Temporal trend analizi | `data/temporal_trends.png` |
| `create_bump_chart_combinations.py` | ❌ Silindi | Bump chart | `data/bump_chart_top10_combinations.png` |
| `create_emergence_scatter.py` | ❌ Silindi | Emergence scatter plot | `data/emergence_scatter_*.png` |
| `analyze_longtail_distribution.py` | ❌ Silindi | Long-tail analizi | `data/loglog_pareto_*.png` |
| `create_source_combination_heatmap.py` | ❌ Silindi | Source combination heatmap | `data/heatmap_source_by_combination.png` |
| `create_wordclouds_by_ce_area.py` | ❌ Silindi | CE area word clouds | `data/wc_*_ai.png` |
| `create_ai_wordclouds_and_contrast.py` | ❌ Silindi | AI word clouds + contrast | `data/wc_*.png` |
| `create_ce_area_top_terms_csv.py` | ❌ Silindi | Top terms CSV'leri | `data/top_terms_*.csv` |
| `create_keyword_network_graphs.py` | ❌ Silindi | Network graphs | `data/network_*.png` |
| `analyze_ai_specialization_lq.py` | ❌ Silindi | Location Quotient analizi | `data/heatmap_ce_ai_specialization_LQ.png` |
| `rank_ce_areas_by_ai_maturity.py` | ❌ Silindi | AI maturity ranking | `data/ce_ai_maturity_ranking.png` |
| `analyze_from_db.py` | ✅ Mevcut | Database'den analiz | Various outputs |

---

### 7. Abstract/Summary Scriptleri

| Script Adı | Durum | Amaç | Çıktı |
|------------|-------|------|-------|
| `add_abstracts.py` | ✅ Mevcut | Abstract ekleme | Updated articles |
| `add_abstracts_filtered.py` | ✅ Mevcut | Filtrelenmiş makalelere abstract | Updated articles |
| `add_summaries_newsapi.py` | ✅ Mevcut | NewsAPI summary ekleme | Updated articles |

---

### 8. Duplicate Detection Scriptleri

| Script Adı | Durum | Amaç | Çıktı |
|------------|-------|------|-------|
| `detect_duplicates_by_summary.py` | ✅ Mevcut | Summary-based duplicate detection | `data/duplicate_articles_*.csv` |

---

### 9. Yardımcı Scriptler

| Script Adı | Durum | Amaç |
|------------|-------|------|
| `llm_api.py` | ✅ Mevcut | LLM API wrapper |
| `collect_articles.py` | ✅ Mevcut | Genel makale toplama |
| `collect_articles_advanced.py` | ✅ Mevcut | Gelişmiş makale toplama |
| `collect_articles_search.py` | ✅ Mevcut | Arama tabanlı toplama |
| `collect_articles_db.py` | ✅ Mevcut | Database'den toplama |

---

## 🔄 Çalıştırma Sırası (Kronolojik)

### Faz 1: Veri Toplama
1. `collect_newsapi.py` - NewsAPI verilerini topla
2. `collect_guardian.py` - Guardian verilerini topla
3. `collect_rss.py` - RSS feed'lerden topla
4. `import_corpus_to_db.py` - Corpus verilerini aktar

### Faz 2: Validasyon
5. `validate_newsapi_flexible.py` - NewsAPI validasyonu
6. `validate_newsapi_comprehensive_flexible.py` - Kapsamlı validasyon
7. `validate_newsapi_ce_ai_intersection.py` - Kesişim kontrolü
8. `create_newsapi_valid_from_validation.py` - Valid makaleleri oluştur

### Faz 3: Sınıflandırma
9. `classify_ce_ai_llm.py` - LLM ile sınıflandırma
10. `retag_untagged_articles.py` - Eksik tag'leri tamamla

### Faz 4: Veritabanı Birleştirme
13. `import_newsapi_csv_to_db.py` - NewsAPI'yi DB'ye aktar
14. `merge_all_valid_to_db.py` - Tüm valid makaleleri birleştir
15. `remove_duplicates_from_unified_table.py` - Duplicate'leri kaldır
16. `complete_missing_abstracts_and_renumber_ids.py` - Abstract + ID düzenleme

### Faz 5: Analiz ve Görselleştirme
17. `create_dual_ce_ai_heatmaps.py` - Heatmap'ler
18. `time_series_analysis.py` - Zaman serisi
19. `create_bump_chart_combinations.py` - Bump chart
20. `create_emergence_scatter.py` - Emergence analizi
21. `analyze_longtail_distribution.py` - Long-tail analizi
22. `create_source_combination_heatmap.py` - Source analizi
23. `create_wordclouds_by_ce_area.py` - Word clouds
24. `create_ai_wordclouds_and_contrast.py` - AI word clouds
25. `create_keyword_network_graphs.py` - Network graphs
26. `analyze_ai_specialization_lq.py` - LQ analizi
27. `rank_ce_areas_by_ai_maturity.py` - Final ranking

### Faz 6: Temizlik
28. `remove_columns_from_unified_table.py` - Gereksiz kolonları kaldır
29. `reorder_columns_id_first.py` - ID'yi başa al

---

## 📊 Son Durum

**Toplam Script Sayısı:** ~32+ script
**Aktif Scriptler:** ~17 script
**Silinen/Birleştirilen Scriptler:** ~15 script
**Final Database:** `all_valid_articles` (1155 makale)
**Final Tablo Yapısı:** 15 kolon

**Yeni Eklenen Scriptler (Task 2):**
- `generate_preprocessing_report.py` - Preprocessing raporları
- `create_cleaned_dataset.py` - Cleaned dataset oluşturma

---

**Not:** Bazı scriptler conversation sırasında silinmiş veya birleştirilmiş olabilir. Bu liste, conversation history'ye dayanarak oluşturulmuştur.

