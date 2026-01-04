# CE49X Final Project - Project Summary and Code Usage

## Project: Civil Engineering & AI Integration - Industry Trends Analysis

This documentation summarizes all processes and scripts used in the CE49X Final Project in chronological order.

---

## 📋 Table of Contents

1. [Database Setup](#database-setup)
2. [Task 1: Data Collection](#task-1-data-collection)
3. [Task 2: Text Preprocessing & NLP](#task-2-text-preprocessing--nlp)
   - [📍 NLP Section Location and Details](#-nlp-section-location-and-details)
   - [🔍 NLP QUICK REFERENCE](#-nlp-quick-reference)
4. [Task 3: Categorization & Trend Analysis](#task-3-categorization--trend-analysis)
5. [Task 4: Visualization & Insights](#task-4-visualization--insights)
6. [Database Management](#database-management)
7. [Final Data Preparation](#final-data-preparation)

---

## Database Setup

This project uses **PostgreSQL** database system to store data. Docker technology was used for database setup. Here's a step-by-step explanation for beginners:

### 🐳 What is Docker?

**Docker** is a tool that creates a virtual environment on your computer. Think of it like a game console - games run on a game console, applications (like databases) run in Docker.

**Why did we use Docker?**
- Instead of installing the database directly on your computer, we ran it inside Docker
- This keeps your computer clean
- We can start and stop it anytime
- It works the same way on other computers

### 📦 Setup Steps

#### Step 1: Download and Install Docker Desktop

1. **Download Docker Desktop:** [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Run the installation:** Run the downloaded file and follow the installation wizard
3. **Start Docker:** After restarting your computer, open the Docker Desktop application
4. **Check if ready:** When Docker Desktop opens, you should see "Docker Desktop is running" in the top left corner

#### Step 2: Navigate to Project Folder

Open Terminal (command line) and go to the project folder:

```bash
cd "C:\Users\Asus\Desktop\49X Final"
```

#### Step 3: Start Database with Docker Compose

**What is Docker Compose?** A tool that allows us to run multiple applications (PostgreSQL + pgAdmin) together.

There is a file called `docker-compose.yml` in the project folder. This file tells Docker:
- Start PostgreSQL database
- Start pgAdmin (database management interface) application
- Connect them together

**Command:**
```bash
docker-compose up -d
```

**What it does:**
- `up`: Start applications
- `-d`: Run in background (detached mode)

**Expected output:**
```
Creating network "49x-final_ce49x_network" ... done
Creating volume "49x-final_postgres_data" ... done
Creating ce49x_postgres ... done
Creating ce49x_pgadmin ... done
```

#### Step 4: Check if Database is Ready

```bash
docker-compose ps
```

**Expected output:**
```
NAME                STATUS          PORTS
ce49x_postgres      Up (healthy)    0.0.0.0:5432->5432/tcp
ce49x_pgadmin       Up               0.0.0.0:5050->80/tcp
```

Both services should be in "Up" status.

### 🗄️ What is PostgreSQL?

**PostgreSQL** is a database system used to store data. You can think of it like an Excel spreadsheet, but much more powerful:

- **Excel:** You store data in one table
- **PostgreSQL:** Stores data in multiple tables, creates relationships between tables, performs fast searches

**What did we use it for in our project?**
- Stored collected articles
- Stored article classification results
- Stored analysis results

### 🎛️ What is pgAdmin4?

**pgAdmin4** is a web interface used to manage PostgreSQL database visually. Think of it like opening Excel and viewing tables.

**How to use it?**

1. **Open in browser:** `http://localhost:5050`
2. **Login:**
   - Email: `admin@ce49x.com`
   - Password: `admin`
3. **Connect to database:**
   - Right-click on "Servers" on the left
   - Select "Register" > "Server"
   - **General** tab:
     - Name: `CE49X Database`
   - **Connection** tab:
     - Host: `postgres` (service name inside Docker)
     - Port: `5432`
     - Database: `ce49x_db`
     - Username: `ce49x_user`
     - Password: `ce49x_password`
   - Click "Save" button

4. **View tables:**
   - On the left: `CE49X Database` > `Databases` > `ce49x_db` > `Schemas` > `public` > `Tables`
   - You can see all tables here

### 📊 Database Structure

When the project started, the `database/init.sql` file was automatically executed and the following tables were created:

1. **articles** - Collected articles
   - `id`: Article number
   - `title`: Title
   - `url`: Article link
   - `content`: Content
   - etc.

2. **classifications** - Classifications made with LLM
   - `article_id`: Which article
   - `ce_areas[]`: CE areas (e.g., Structural, Transportation)
   - `ai_technologies[]`: AI technologies (e.g., Computer Vision, Predictive Analytics)
   - `confidence_score`: Confidence score

3. **all_valid_articles** - Combined valid articles from all sources
   - Valid articles from NewsAPI, Guardian, Corpus sources
   - Table used for final analysis

### 🔧 Database Connection Settings

For Python scripts to connect to the database, a `.env` file was created:

```env
# Database Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ce49x_db
DB_USER=ce49x_user
DB_PASSWORD=ce49x_password

# LLM API Keys
OPENAI_API_KEY=sk-your-key-here
```

**Why `.env` file?**
- To avoid storing sensitive information (passwords, API keys) in code
- Everyone can add their own information
- Not uploaded to Git (in `.gitignore`)

### ✅ Setup Verification

To check if the database is working properly:

```bash
python -c "from database.db_config import test_connection; print('✓ Connection successful!' if test_connection() else '✗ Connection error!')"
```

**Successful output:** `✓ Connection successful!`

### 🛑 Stopping the Database

When you're done, to stop the database:

```bash
docker-compose down
```

**To also delete data:**
```bash
docker-compose down -v
```

⚠️ **Warning:** The `-v` parameter deletes all data!

### 📝 Summary

1. **Docker Desktop** was installed
2. **docker-compose up -d** command started PostgreSQL and pgAdmin
3. **pgAdmin4** was used to manage the database visually
4. **Python scripts** connected to the database using settings in `.env` file
5. **All data** was stored and analyzed in PostgreSQL

**Result:** 1155 valid articles were stored in the `all_valid_articles` table and all analyses were performed on this table.

---

## Task 1: Data Collection

### 1.1 NewsAPI Data Collection
**Script:** `scripts/collect_newsapi.py`
- **Purpose:** Collect news articles related to CE and AI using NewsAPI
- **Features:**
  - NewsAPI "everything" endpoint usage
  - Search with CE and AI keyword combinations
  - Metadata collection (title, publication_date, source, url, description)
  - CSV format storage
- **Output:** `data/newsapi_articles_*.csv`

### 1.2 Guardian API Data Collection
**Script:** `scripts/collect_guardian.py`
- **Purpose:** Collect articles using Guardian Open Platform API
- **Features:**
  - Guardian API usage
  - Full text extraction (trafilatura)
  - Strict filtering (minimum 1 CE + 1 AI keyword)
  - API limit protection
- **Output:** `data/guardian_articles_*.csv`

### 1.3 RSS Feed Collection
**Script:** `scripts/collect_rss.py`
- **Purpose:** Collect articles from RSS feeds
- **Features:**
  - RSS feed parsing
  - Multiple source support
- **Output:** `data/rss_articles_*.csv`

### 1.4 Corpus Data Import
**Script:** `scripts/import_corpus_to_db.py`
- **Purpose:** Import existing corpus data to database
- **Output:** `data/corpus.csv` → Database

---

## Task 2: Text Preprocessing & NLP

### 📍 NLP Section Location and Details

**Main NLP Scripts:**
- `scripts/preprocess_newsapi.py` - Main preprocessing script
- `scripts/generate_preprocessing_report.py` - Report generation
- `scripts/create_cleaned_dataset.py` - Cleaned dataset creation

**NLP Output Files:**
- `data/top20_most_frequent_words.csv` - Top 20 word list
- `data/top20_bigrams.csv` - Top 20 bi-gram list
- `data/preprocessing_report.md` - Detailed preprocessing report
- `data/cleaned_dataset.csv` - Cleaned dataset (1155 articles)

---

### 2.1 NewsAPI Data Preprocessing
**Script:** `scripts/preprocess_newsapi.py`
- **File Path:** `49X Final/scripts/preprocess_newsapi.py`
- **Purpose:** Clean and preprocess NewsAPI data
- **NLP Libraries Used:**
  - `nltk` - Tokenization, stopword removal, lemmatization
  - `scikit-learn` - TF-IDF calculation
- **NLP Processes (In Order):**
  1. **Tokenization** - Using `nltk.word_tokenize()` and `nltk.sent_tokenize()`
  2. **Normalization** - Lowercasing, punctuation removal, URL/email removal
  3. **Stopword Removal** - NLTK English stopwords + domain-specific stopwords (article, read, more, click, etc.)
  4. **Lemmatization** - Reducing words to root form using `nltk.WordNetLemmatizer()`
  5. **N-grams Extraction** - Extracting bigrams and trigrams using `nltk.ngrams()`
  6. **TF-IDF Calculation** - Calculating term frequency-inverse document frequency using `sklearn.TfidfVectorizer()`
- **Functions:**
  - `normalize_text()` - Text normalization
  - `remove_stopwords()` - Stopword removal
  - `lemmatize_text()` - Lemmatization
  - `extract_ngrams()` - N-gram extraction
  - `calculate_tfidf()` - TF-IDF calculation
- **Output:** Processed data with `processed_text`, `bigrams`, `trigrams`, `top_tfidf_terms` columns

### 2.2 Preprocessing Report Generation
**Script:** `scripts/generate_preprocessing_report.py` ✅ NEW
- **File Path:** `49X Final/scripts/generate_preprocessing_report.py`
- **Purpose:** Generate preprocessing reports for Task 2 requirements
- **Data Source:** 1155 articles from `all_valid_articles` table
- **NLP Processes:**
  - Text combination (title + description + abstract)
  - Normalization (lowercasing, URL/email removal)
  - Stopword removal (NLTK + domain-specific)
  - Word frequency counting (using Counter)
  - Bigram extraction and frequency counting
- **Features:**
  - Calculate top 20 most frequent words (excluding stopwords)
  - Calculate top 20 bi-grams
  - Detailed report in Markdown format
- **Outputs:**
  - `data/top20_most_frequent_words.csv` - With Rank, Word, Frequency columns
  - `data/top20_bigrams.csv` - With Rank, Bigram, Frequency columns
  - `data/preprocessing_report.md` - Detailed preprocessing report (Markdown format)
- **Status:** ✅ USED - Reports generated from 1155 articles
- **Results:**
  - Top Word: "market" (598 times)
  - Top Bigram: "artificial intelligence" (203 times)

### 2.3 Cleaned Dataset Creation
**Script:** `scripts/create_cleaned_dataset.py` ✅ NEW
- **File Path:** `49X Final/scripts/create_cleaned_dataset.py`
- **Purpose:** Create cleaned dataset (Task 2 requirement)
- **Data Source:** From `all_valid_articles` table
- **NLP Processes:**
  1. Text combination (title + description + abstract)
  2. Normalization:
     - Lowercasing
     - Punctuation removal
     - URL removal (regex: `r'http\S+|www\.\S+'`)
     - Email removal (regex: `r'\S+@\S+'`)
     - Special characters removal (only alphanumeric and spaces)
  3. Stopword removal:
     - Common English stopwords (the, a, an, and, or, etc.)
     - Domain-specific stopwords (article, read, more, click, subscribe, etc.)
     - Words with length <= 2 characters excluded
- **Output:** `data/cleaned_dataset.csv` - 1155 articles with cleaned text
- **Columns:**
  - `id`, `title`, `description`, `url`, `source`, `publication_date`
  - `abstract`, `ce_areas`, `ai_technologies`, `cleaned_text`
- **Status:** ✅ USED - Cleaned dataset created
- **Statistics:**
  - Total articles: 1155
  - Average cleaned text length: ~560 characters

---

## Task 3: Categorization & Trend Analysis

### 3.1 Guardian Article Validation
**Script:** `scripts/validate_guardian_ce_keywords.py` ✅ USED (later deleted)
- **Purpose:** Validate CE keywords in Guardian articles using LLM
- **Method:** OpenAI GPT-3.5-turbo API
- **Status:** Used, validation performed, then replaced with more flexible version
- **Output:** `data/guardian_ce_keyword_validation.csv`

**Script:** `scripts/revalidate_guardian_flexible.py` ✅ USED (later deleted)
- **Purpose:** Re-validate Guardian articles with more flexible criteria
- **Change:** Lower confidence threshold, broader CE interpretation
- **Status:** Used, more valid articles found, function completed
- **Output:** `data/guardian_ce_keyword_validation_flexible.csv`

**Script:** `scripts/save_guardian_valid.py` ✅ USED (later deleted)
- **Purpose:** Save valid Guardian articles to separate CSV
- **Status:** Used, valid articles saved, function completed
- **Output:** `data/guardian_valid.csv`

### 3.2 Corpus Article Validation
**Script:** `scripts/validate_corpus_ce.py` ✅ USED (later deleted)
- **Purpose:** Validate corpus articles using LLM
- **Status:** Used, corpus articles validated, function completed
- **Output:** `data/corpus_valid.csv`

### 3.3 NewsAPI Article Validation
**Script:** `scripts/validate_newsapi_flexible.py`
- **Purpose:** Validate NewsAPI articles with flexible criteria
- **Method:** LLM-based validation
- **Output:** `data/newsapi_validation_flexible.csv`

**Script:** `scripts/validate_newsapi_comprehensive_flexible.py`
- **Purpose:** Comprehensive and flexible NewsAPI validation
- **Output:** `data/newsapi_validation_comprehensive.csv`

**Script:** `scripts/validate_newsapi_ce_ai_intersection.py`
- **Purpose:** Check CE and AI intersection in NewsAPI articles
- **Output:** `data/newsapi_ce_ai_validation.csv`

**Script:** `scripts/validate_newsapi_ai_ce_intersection.py`
- **Purpose:** Check AI and CE intersection in reverse direction
- **Output:** `data/newsapi_ai_ce_validation.csv`

**Script:** `scripts/create_newsapi_valid_from_validation.py` ✅ USED (later deleted)
- **Purpose:** Create valid NewsAPI articles from validation results
- **Status:** Used, valid NewsAPI articles created, function completed
- **Output:** `data/newsapi_valid.csv`

### 3.4 Dictionary-Based Classification
**Script:** `scripts/classify_ce_ai.py` ✅ USED (later deleted)
- **Purpose:** Dictionary-based CE and AI classification
- **Method:** Keyword matching
- **Status:** Used, tested, then replaced with LLM-based version
- **CE Areas:** Structural, Geotechnical, Transportation, Construction Management, Environmental Engineering
- **AI Technologies:** Computer Vision, Predictive Analytics, Generative Design, Robotics/Automation
- **Output:** `data/articles_tagged.csv`

### 3.5 LLM-Based Classification
**Script:** `scripts/classify_ce_ai_llm.py` ✅ USED (later deleted)
- **Purpose:** More accurate classification using LLM API
- **Method:** OpenAI GPT-3.5-turbo
- **Status:** Used, all articles (NewsAPI, Guardian, Corpus) classified, function completed
- **Features:**
  - Tagging each article with CE areas and AI technologies
  - Confidence scoring
  - Processing NewsAPI, Guardian, Corpus data
- **Output:** `data/articles_tagged_llm.csv`, `data/articles_tagged_llm_complete.csv`
- **Note:** All articles were successfully classified and results were transferred to the database. Script was deleted after function completion.

**Script:** `scripts/retag_untagged_articles.py` ✅ USED (later deleted)
- **Purpose:** Re-tag untagged articles
- **Status:** Used, missing tags completed, ensured all valid articles have at least 1 CE and 1 AI tag
- **Feature:** Ensures all valid articles have at least 1 CE and 1 AI tag

### 3.6 Classification Analysis
**Script:** `scripts/classify_and_analyze.py`
- **Purpose:** Analyze classification results
- **Outputs:**
  - `data/classification_analysis.csv`
  - `data/heatmap_ce_ai.png`
  - `data/bar_chart_*.png`

**Script:** `scripts/generate_classification_report.py` ✅ USED (later deleted)
- **Purpose:** Generate classification report
- **Status:** Used, report generated, function completed
- **Output:** `data/classification_report.md`

---

## Task 4: Visualization & Insights

### 4.1 Co-occurrence Heatmaps
**Script:** `scripts/create_normalized_ce_ai_heatmap.py` ✅ USED (later deleted)
- **Purpose:** Normalized CE × AI co-occurrence heatmap
- **Status:** Used, heatmap created, function completed
- **Features:**
  - Row-wise normalization
  - Percentage annotations
- **Output:** `data/heatmap_ce_ai_specialization_LQ.png`, `data/ce_ai_cooccurrence_normalized.csv`

**Script:** `scripts/create_dual_ce_ai_heatmaps.py` ✅ USED (later deleted)
- **Purpose:** Dual heatmaps for both raw counts and normalized percentages
- **Status:** Used, both heatmaps created, function completed
- **Outputs:**
  - `data/heatmap_ce_ai_raw_counts.png`
  - `data/heatmap_ce_ai_normalized.png`
  - `data/ce_ai_cooccurrence_raw_counts.csv`
  - `data/ce_ai_cooccurrence_normalized.csv`

### 4.2 Temporal Analysis
**Script:** `scripts/time_series_analysis.py` ✅ USED (later deleted)
- **Purpose:** Time series analysis of article volume
- **Status:** Used, time series analysis performed, visualization created
- **Features:**
  - Daily/weekly aggregation
  - Rolling average (7-day/14-day)
  - Automatic spike detection (z-score based)
- **Outputs:**
  - `data/time_series_total_articles_with_rolling_avg.png`
  - `data/time_series_article_counts.csv`

**Script:** `scripts/temporal_trends_analysis.py` ✅ USED (later deleted)
- **Purpose:** Temporal trends of specific CE×AI combinations
- **Status:** Used, temporal trends analyzed, function completed
- **Output:** `data/temporal_trends.csv`, `data/temporal_trends.png`

### 4.3 Bump Chart
**Script:** `scripts/create_bump_chart_combinations.py` ✅ USED (later deleted)
- **Purpose:** Rank evolution of top 10 CE×AI combinations
- **Status:** Used, bump chart created, function completed
- **Features:**
  - Monthly rank calculation
  - Bump chart visualization
- **Outputs:**
  - `data/bump_chart_top10_combinations.png`
  - `data/combination_rank_over_time.csv`

### 4.4 Emergence Analysis
**Script:** `scripts/create_emergence_scatter.py` ✅ USED (later deleted)
- **Purpose:** Identify emerging CE×AI combinations
- **Status:** Used, emergence analysis performed, scatter plot created
- **Features:**
  - x-axis: Recency (days since first appearance)
  - y-axis: Growth rate (last period vs previous period)
  - Point size: Total article count
- **Outputs:**
  - `data/emergence_scatter_recency_vs_growth.png`
  - `data/emergence_metrics_combinations.csv`

### 4.5 Long-tail Distribution Analysis
**Script:** `scripts/analyze_longtail_distribution.py` ✅ USED (later deleted)
- **Purpose:** Analyze long-tail distribution of CE×AI combinations
- **Status:** Used, long-tail analysis performed, log-log plot created
- **Features:**
  - Log-log plot
  - Power-law reference line
  - Pareto analysis
- **Outputs:**
  - `data/loglog_pareto_combination_frequency.png`
  - `data/combination_frequency_ranked.csv`

### 4.6 Source Analysis
**Script:** `scripts/create_source_combination_heatmap.py` ✅ USED (later deleted)
- **Purpose:** Show which sources cover which CE×AI combinations
- **Status:** Used, source analysis heatmap created, function completed
- **Outputs:**
  - `data/heatmap_source_by_combination.png`
  - `data/source_combination_matrix.csv`

### 4.7 Word Clouds
**Script:** `scripts/create_wordclouds_by_ce_area.py` ✅ USED (later deleted)
- **Purpose:** AI-filtered word clouds for each CE area
- **Status:** Used, 5 word clouds created for CE areas, function completed
- **Features:**
  - Separate word cloud for each CE area
  - Created from articles containing AI keywords
  - Minimum article count check
  - High resolution (dpi >= 200)
- **Outputs:**
  - `data/wc_structural_ai.png`
  - `data/wc_geotechnical_ai.png`
  - `data/wc_transportation_ai.png`
  - `data/wc_construction_mgmt_ai.png`
  - `data/wc_environmental_ai.png`
  - `data/top_terms_*.csv` (for each CE area)

**Script:** `scripts/create_ai_wordclouds_and_contrast.py` ✅ USED (later deleted)
- **Purpose:** CE-filtered word clouds for each AI technology and contrastive word clouds
- **Status:** Used, 4 AI tech + 2 contrastive word clouds created, function completed
- **Features:**
  - Separate word cloud for each AI tech
  - Created from articles containing CE keywords
  - Contrastive word clouds (Transportation+AI vs Structural+AI, Construction Mgmt+AI vs Environmental+AI)
  - Distinctive terms using TF-IDF difference
- **Outputs:**
  - `data/wc_cv_in_ce.png`
  - `data/wc_predictive_in_ce.png`
  - `data/wc_genai_in_ce.png`
  - `data/wc_robotics_in_ce.png`
  - `data/wc_contrast_transport_vs_structural.png`
  - `data/wc_contrast_conmgmt_vs_env.png`
  - `data/top_terms_*.csv` (for each AI tech)
  - `data/contrast_*.csv` (contrastive terms)

**Script:** `scripts/create_ce_area_top_terms_csv.py` ✅ USED (later deleted)
- **Purpose:** Create top terms CSVs for CE area word clouds
- **Status:** Used, CSVs created, function completed
- **Output:** `data/top_terms_*.csv`

### 4.8 Network Graphs
**Script:** `scripts/create_keyword_network_graphs.py` ✅ USED (later deleted)
- **Purpose:** Keyword co-occurrence network graphs
- **Status:** Used, 3 network graphs created (full, CE-only, bipartite), function completed
- **Features:**
  - Full keyword network (CE + AI together)
  - CE-only keyword network
  - Bipartite network (CE keywords ↔ AI keywords only)
  - Community detection (Louvain algorithm)
  - Centrality measures (degree, betweenness)
  - Hub and bridge node identification
- **Outputs:**
  - `data/network_full_keywords.png`
  - `data/network_ce_only.png`
  - `data/network_bipartite_ce_to_ai.png`
  - `data/network_metrics_full.csv`
  - `data/network_metrics_ce.csv`
  - `data/network_metrics_bipartite.csv`
  - `data/network_top_bridges.csv`
  - `data/network_insights.txt`

### 4.9 Specialization Analysis
**Script:** `scripts/analyze_ai_specialization_lq.py` ✅ USED (later deleted)
- **Purpose:** Analyze AI technology specialization in CE areas using Location Quotient (LQ)
- **Status:** Used, LQ analysis performed, heatmap created, function completed
- **Formula:** LQ = (share of AI within CE) / (overall share of AI)
- **Interpretation:** LQ > 1 = CE domain is over-represented for that AI tech
- **Outputs:**
  - `data/heatmap_ce_ai_specialization_LQ.png`
  - `data/ce_ai_location_quotient.csv`

### 4.10 AI Maturity Ranking
**Script:** `scripts/rank_ce_areas_by_ai_maturity.py` ✅ USED (later deleted)
- **Purpose:** Rank CE areas by AI maturity/interest level
- **Status:** Used, final ranking analysis performed, visualization created, function completed
- **Metrics:**
  - Article Volume (30%)
  - AI Diversity (25%)
  - Specialization/LQ (25%)
  - Growth Trend (20%)
- **Outputs:**
  - `data/ce_ai_maturity_ranking.csv`
  - `data/ce_ai_maturity_ranking.png`

---

## Database Management

### 5.1 Database Migration
**Script:** `scripts/migrate_to_postgres.py`
- **Purpose:** Data migration from SQLite to PostgreSQL
- **Features:**
  - Connection pooling
  - Batch processing

### 5.2 NewsAPI Database Import
**Script:** `scripts/import_newsapi_csv_to_db.py`
- **Purpose:** Import NewsAPI CSV files to database
- **Table:** `newsapi_articles`

### 5.3 Valid Articles Database Operations
**Script:** `scripts/save_valid_newsapi_to_db.py` ✅ USED (later deleted)
- **Purpose:** Save valid NewsAPI articles to separate table
- **Status:** Used, valid NewsAPI articles saved, function completed
- **Table:** `newsapi_valid`

**Script:** `scripts/merge_all_valid_to_db.py` ✅ USED (later deleted)
- **Purpose:** Merge all valid articles (NewsAPI, Guardian, Corpus)
- **Status:** Used, all sources merged, unified table created
- **Table:** `all_valid_articles`
- **Features:**
  - Column standardization
  - Date format conversion

**Script:** `scripts/add_abstracts_to_unified_table.py` ✅ USED (later deleted)
- **Purpose:** Add abstracts from previous tables to unified table
- **Status:** Used, abstracts added, function completed

**Script:** `scripts/remove_duplicates_from_unified_table.py` ✅ USED (later deleted)
- **Purpose:** Remove duplicates by URL and title
- **Status:** Used, duplicates cleaned, function completed
- **Method:** By URL and title combination, then by URL, then by title

**Script:** `scripts/generate_abstracts_for_unified_table.py` ✅ USED (later deleted)
- **Purpose:** Generate abstracts using LLM for articles missing abstracts
- **Status:** Used, missing abstracts generated using LLM, function completed
- **Method:** OpenAI GPT-3.5-turbo

### 5.4 Database Cleanup
**Script:** `scripts/remove_columns_from_unified_table.py`
- **Purpose:** Remove unnecessary columns
- **Removed columns:**
  - `text_content`
  - `validation_confidence`
  - `validation_reason`
  - `is_valid`
  - `created_at`
  - `use_case_topic`
  - `topic_confidence`
  - `topic_reason`
  - `source_type`

**Script:** `scripts/reorder_columns_id_first.py`
- **Purpose:** Move ID column to the beginning
- **Method:** Table recreation

**Script:** `scripts/complete_missing_abstracts_and_renumber_ids.py`
- **Purpose:** 
  1. Complete missing abstracts (using LLM)
  2. Renumber IDs starting from 1
- **Result:** 1155 articles, IDs 1-1155

---

## Final Data Preparation

### 6.1 Duplicate Detection
**Script:** `scripts/detect_duplicates_by_summary.py`
- **Purpose:** Summary-based duplicate detection
- **Output:** `data/duplicate_articles_by_summary.csv`

### 6.2 Abstract Generation
**Script:** `scripts/add_abstracts.py`
- **Purpose:** Generate abstracts for articles
- **Method:** LLM API

**Script:** `scripts/add_abstracts_filtered.py`
- **Purpose:** Generate abstracts for filtered articles

**Script:** `scripts/add_summaries_newsapi.py`
- **Purpose:** Add summaries to NewsAPI articles

---

## 📊 Final Database Structure

### `all_valid_articles` Table

**Columns (15 total):**
1. `id` (integer, PRIMARY KEY) - Sequential starting from 1
2. `title` (text)
3. `description` (text)
4. `url` (text)
5. `source` (text)
6. `publication_date` (timestamp)
7. `ce_keywords_found` (text)
8. `ai_keywords_found` (text)
9. `ce_areas` (ARRAY) - CE areas list
10. `ce_confidence` (double precision)
11. `ce_reason` (text)
12. `ai_technologies` (ARRAY) - AI technologies list
13. `ai_confidence` (double precision)
14. `ai_reason` (text)
15. `abstract` (text)

**Total Records:** 1155 articles

### Task 2: Preprocessing Outputs ✅

**Cleaned Dataset:**
- `data/cleaned_dataset.csv` - 1155 articles with cleaned text
- For each article: id, title, description, url, source, publication_date, abstract, ce_areas, ai_technologies, cleaned_text

**Preprocessing Reports:**
- Top 20 most frequent words: market (598), data (451), technology (395), intelligence (280), infrastructure (226)
- Top 20 bi-grams: artificial intelligence (203), data center (97), machine learning (60), deep learning (45)

---

## 🎯 Project Results Summary

### CE Areas - AI Maturity Ranking (Final)
1. **Construction Management** - 97.4/100
2. **Transportation** - 80.8/100
3. **Structural** - 79.7/100
4. **Environmental Engineering** - 73.7/100
5. **Geotechnical** - 65.7/100

### Key Insights
- **Highest AI Maturity:** Construction Management (686 articles, 4/4 AI technologies)
- **Highest Specialization:** Structural (Avg LQ: 1.095)
- **Most Balanced:** Transportation (high volume + specialization balance)
- **Lowest Volume:** Geotechnical (10 articles)

---

## 📁 Important Output Files

### Task 2: Preprocessing Results ✅ NEW
- `data/top20_most_frequent_words.csv` - Top 20 most frequently used words
- `data/top20_bigrams.csv` - Top 20 most frequently used bi-grams
- `data/preprocessing_report.md` - Detailed preprocessing report
- `data/cleaned_dataset.csv` - Cleaned dataset (1155 articles)

### Analysis Results
- `data/ce_ai_maturity_ranking.csv` - AI maturity ranking
- `data/ce_ai_location_quotient.csv` - Location Quotient matrix
- `data/ce_ai_cooccurrence_raw_counts.csv` - Raw co-occurrence counts
- `data/ce_ai_cooccurrence_normalized.csv` - Normalized co-occurrence percentages

### Visualizations
- `data/heatmap_ce_ai_specialization_LQ.png` - LQ heatmap
- `data/heatmap_ce_ai_raw_counts.png` - Raw counts heatmap
- `data/heatmap_ce_ai_normalized.png` - Normalized heatmap
- `data/ce_ai_maturity_ranking.png` - Ranking bar chart
- `data/time_series_total_articles_with_rolling_avg.png` - Time series
- `data/bump_chart_top10_combinations.png` - Bump chart
- `data/emergence_scatter_recency_vs_growth.png` - Emergence scatter
- `data/loglog_pareto_combination_frequency.png` - Long-tail distribution
- `data/heatmap_source_by_combination.png` - Source analysis
- `data/network_*.png` - Network graphs (3 files)
- `data/wc_*.png` - Word clouds (9 files)

---

## 🔧 Technical Details

### Technologies Used
- **Python 3.8+**
- **PostgreSQL** (Docker)
- **OpenAI GPT-3.5-turbo API** (LLM classification, validation, abstract generation)
- **Libraries:**
  - `pandas`, `numpy` - Data manipulation
  - `psycopg2` - PostgreSQL connection
  - `openai` - LLM API
  - `matplotlib`, `seaborn` - Visualization
  - `networkx`, `python-louvain` - Network analysis
  - `wordcloud` - Word cloud generation
  - `requests` - API calls
  - `trafilatura` - Web scraping
  - **NLP Libraries:**
    - `nltk` - Tokenization, stopword removal, lemmatization, n-grams
    - `scikit-learn` - TF-IDF calculation (TfidfVectorizer)

### API Keys
- NewsAPI
- Guardian Open Platform API
- OpenAI API

---

## 📝 Notes

- Some scripts may have been deleted or merged (scripts mentioned in conversation history)
- All analyses were performed on the `all_valid_articles` table
- Rate limiting was applied for LLM API usage
- Database connection pooling was used

---

## 🔍 NLP QUICK REFERENCE

### 📂 Where are NLP Scripts?
- **Main Preprocessing:** `scripts/preprocess_newsapi.py`
- **Report Generation:** `scripts/generate_preprocessing_report.py`
- **Cleaned Dataset:** `scripts/create_cleaned_dataset.py`

### 📁 Where are NLP Output Files?
- **Top 20 Words:** `data/top20_most_frequent_words.csv`
- **Top 20 Bi-grams:** `data/top20_bigrams.csv`
- **Preprocessing Report:** `data/preprocessing_report.md`
- **Cleaned Dataset:** `data/cleaned_dataset.csv`

### 📚 NLP Libraries
- **NLTK:** Tokenization, stopword removal, lemmatization, n-grams
  - `nltk.word_tokenize()` - Word tokenization
  - `nltk.sent_tokenize()` - Sentence tokenization
  - `nltk.corpus.stopwords` - Stopword list
  - `nltk.stem.WordNetLemmatizer()` - Lemmatization
  - `nltk.util.ngrams()` - N-gram extraction
- **scikit-learn:** TF-IDF calculation
  - `sklearn.feature_extraction.text.TfidfVectorizer()` - TF-IDF calculation

### 🔄 NLP Process Steps (Sequential)
1. **Tokenization** - Split text into words/sentences (NLTK word_tokenize)
2. **Normalization** - Convert to lowercase, remove punctuation, clean URLs/emails
3. **Stopword Removal** - Remove common words (NLTK + domain-specific)
4. **Lemmatization** - Reduce words to root form (NLTK WordNetLemmatizer)
5. **N-grams Extraction** - Extract bigrams and trigrams (NLTK ngrams)
6. **TF-IDF Calculation** - Calculate term frequency-inverse document frequency (scikit-learn)

### 📊 NLP Results
- **Top Word:** market (598 times)
- **Top Bigram:** artificial intelligence (203 times)
- **Total Processed Articles:** 1155
- **Average Cleaned Text Length:** ~560 characters

### 🎯 NLP Usage Scenarios
- **Preprocessing:** `preprocess_newsapi.py` - Clean raw texts
- **Report Generation:** `generate_preprocessing_report.py` - Top 20 words/bi-grams
- **Dataset Preparation:** `create_cleaned_dataset.py` - Clean dataset for analysis

---

## 📌 Important Note: About "Deleted" Status

In this documentation, **"✅ USED (later deleted)"** means:

- ✅ **Script was used** - Executed during conversation and fulfilled its function
- ✅ **Function completed** - Required analysis/data processing was done, outputs were created
- ✅ **Later deleted** - File was removed from filesystem after function completion during cleanup

**Examples:**
- `classify_ce_ai_llm.py` → All articles classified, results transferred to database, script deleted
- `create_wordclouds_by_ce_area.py` → 5 word clouds created, images saved, script deleted
- `rank_ce_areas_by_ai_maturity.py` → Final ranking analysis performed, visualization created, script deleted

**These are NOT unused scripts!** All scripts were actively used during the conversation and contributed to project results.

---

**Last Update:** 2025-01-XX
**Project Status:** ✅ Completed


