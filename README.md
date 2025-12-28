# CE49X Final Project: Civil Engineering & AI Integration - Industry Trends Analysis

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/akselpulas/49x-final)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

## 📋 Project Overview

This project analyzes the integration of Artificial Intelligence (AI) technologies in Civil Engineering (CE) domains by collecting, processing, and analyzing 1,155+ articles from multiple news sources. The analysis includes:

- **Data Collection**: Guardian API, NewsAPI, RSS feeds
- **Text Preprocessing & NLP**: Tokenization, lemmatization, stopword removal, n-gram extraction
- **Categorization**: Multi-label classification of articles into CE areas and AI technologies
- **Trend Analysis**: Temporal patterns, co-occurrence matrices, emergence analysis
- **Visualization**: 28+ publication-ready visualizations (heatmaps, word clouds, network graphs, time series)

## 🎯 Key Findings

- **1,155 articles** collected (11.5x the minimum requirement of 100)
- **Construction Management** leads in AI maturity (97.4 score, 59.4% of articles)
- **Computer Vision** is the most prevalent AI technology across all CE domains
- **Geotechnical Engineering** shows the lowest representation (0.9%), indicating a research gap

## 📊 Project Structure

```
49X Final/
├── scripts/              # Python scripts for data collection, processing, and analysis
│   ├── collect_*.py      # Data collection scripts
│   ├── preprocess_*.py   # NLP preprocessing
│   ├── classify_*.py     # LLM-based classification
│   └── analyze_*.py      # Analysis and visualization scripts
├── data/                 # All data files and outputs
│   ├── *.csv            # Processed datasets and analysis results
│   ├── *.png            # 28 visualization files
│   └── *.md             # Reports and insights
├── database/            # Database configuration
│   ├── db_config.py     # Database connection settings
│   └── init.sql         # Database initialization script
├── docs/                # Documentation (Turkish and English)
│   ├── PROJE_OZETI.md           # Turkish project summary
│   ├── PROJECT_SUMMARY_EN.md    # English project summary
│   ├── CODE_LIST_EN.md          # English code list
│   └── PROGRESS_PRESENTATION_ANSWERS.md  # Q&A for progress presentation
├── docker-compose.yml   # Docker setup for PostgreSQL and pgAdmin
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker Desktop
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/akselpulas/49x-final.git
   cd 49x-final
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `env_template.txt` to `.env`
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_key
     GUARDIAN_API_KEY=your_guardian_key
     NEWSAPI_KEY=your_newsapi_key
     ```

4. **Start the database:**
   ```bash
   docker-compose up -d
   ```

5. **Initialize the database:**
   ```bash
   python setup_database.py
   ```

### Running Scripts

**Data Collection:**
```bash
python scripts/collect_guardian.py
python scripts/collect_newsapi.py
python scripts/collect_rss.py
```

**Preprocessing:**
```bash
python scripts/generate_preprocessing_report.py
python scripts/create_cleaned_dataset.py
```

**Classification:**
```bash
python scripts/classify_with_llm.py
```

**Analysis & Visualization:**
```bash
python scripts/analyze_from_db.py
```

## 📚 Documentation

- **[PROJECT_SUMMARY_EN.md](PROJECT_SUMMARY_EN.md)**: Comprehensive English project summary
- **[PROGRESS_PRESENTATION_ANSWERS.md](PROGRESS_PRESENTATION_ANSWERS.md)**: Answers to 24 progress presentation questions
- **[README_DATABASE.md](README_DATABASE.md)**: Detailed database setup guide
- **[CODE_LIST_EN.md](CODE_LIST_EN.md)**: Complete list of scripts and their purposes

## 🗄️ Database Setup

The project uses **PostgreSQL** with **Docker** for easy setup. See [README_DATABASE.md](README_DATABASE.md) for detailed instructions.

**Quick Setup:**
1. Start Docker Desktop
2. Run `docker-compose up -d`
3. Access pgAdmin at `http://localhost:5050`
4. Database credentials are in `docker-compose.yml`

## 📈 Key Metrics

- **Articles Collected**: 1,155
- **CE Areas**: 5 (Structural, Geotechnical, Transportation, Construction Management, Environmental)
- **AI Technologies**: 4 (Computer Vision, Predictive Analytics, Generative Design, Robotics/Automation)
- **Visualizations**: 28
- **Date Range**: November 2024 - December 2025

## 🎨 Visualizations

All visualizations are in the `data/` folder:

- **Heatmaps**: CE×AI co-occurrence (raw counts, normalized, specialization LQ)
- **Time Series**: Article volume over time with rolling averages
- **Word Clouds**: 9 word clouds by CE area and AI technology
- **Network Graphs**: Keyword co-occurrence networks (full, CE-only, bipartite)
- **Advanced Analysis**: Bump charts, emergence scatter plots, Pareto analysis

## 🔧 Technologies Used

- **Python**: Data processing, NLP, analysis
- **PostgreSQL**: Data storage
- **Docker**: Containerization
- **OpenAI API**: LLM-based classification
- **NLTK**: Natural language processing
- **Pandas**: Data manipulation
- **Matplotlib/Seaborn**: Visualization
- **NetworkX**: Network analysis
- **WordCloud**: Word cloud generation

## 📝 Tasks Completed

- ✅ **Task 1**: Data Collection (1,155 articles from 3 sources)
- ✅ **Task 2**: Text Preprocessing & NLP (reports and cleaned dataset)
- ✅ **Task 3**: Categorization & Trend Analysis (LLM classification, co-occurrence matrices)
- ✅ **Task 4**: Visualization & Insights (28 visualizations, AI maturity ranking)

## 🤝 Contributing

This is a final project for CE49X - Introduction to Data Science for Civil Engineering. For questions or issues, please open an issue on GitHub.

## 📄 License

This project is for academic purposes as part of the CE49X course.

## 👥 Authors

- **Aksel Pulaş** - [GitHub](https://github.com/akselpulas)

## 🙏 Acknowledgments

- CE49X Course Instructors
- OpenAI for GPT-3.5-turbo API
- Guardian API and NewsAPI for data access

---

**Repository**: [https://github.com/akselpulas/49x-final](https://github.com/akselpulas/49x-final)

**Last Updated**: December 2025

