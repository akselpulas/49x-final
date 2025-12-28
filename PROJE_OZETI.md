# CE49X Final Project - Proje Özeti ve Kullanılan Kodlar

## Proje: Civil Engineering & AI Integration - Industry Trends Analysis

Bu dokümantasyon, CE49X Final Project kapsamında yapılan tüm işlemleri ve kullanılan scriptleri kronolojik olarak özetlemektedir.

---

## 📋 İçindekiler

1. [Veritabanı Kurulumu (Database Setup)](#veritabani-kurulumu)
2. [Task 1: Data Collection (Veri Toplama)](#task-1-data-collection)
3. [Task 2: Text Preprocessing & NLP](#task-2-text-preprocessing--nlp)
   - [📍 NLP Kısmının Konumu ve Detayları](#-nlp-kısmının-konumu-ve-detayları)
   - [🔍 NLP KISMI HIZLI REFERANS](#-nlp-kismi-hizli-referans)
4. [Task 3: Categorization & Trend Analysis](#task-3-categorization--trend-analysis)
5. [Task 4: Visualization & Insights](#task-4-visualization--insights)
6. [Database Management](#database-management)
7. [Final Data Preparation](#final-data-preparation)

---

## Veritabanı Kurulumu

Bu projede verileri saklamak için **PostgreSQL** adında bir veritabanı sistemi kullanıldı. Veritabanı kurulumu için **Docker** adında bir teknoloji kullanıldı. İşte hiç bilmeyen biri için adım adım açıklama:

### 🐳 Docker Nedir?

**Docker**, bilgisayarınızda sanal bir ortam oluşturmanızı sağlayan bir araçtır. Tıpkı bir oyun konsolu gibi düşünebilirsiniz - oyun konsolunda oyunlar çalışır, Docker'da ise uygulamalar (veritabanı gibi) çalışır.

**Neden Docker kullandık?**
- Veritabanını bilgisayarınıza doğrudan kurmak yerine, Docker içinde çalıştırdık
- Böylece bilgisayarınızın temiz kalmasını sağladık
- İstediğimiz zaman açıp kapatabiliriz
- Başka bilgisayarlarda da aynı şekilde çalışır

### 📦 Kurulum Adımları

#### Adım 1: Docker Desktop'ı İndirme ve Kurma

1. **Docker Desktop'ı indirin:** [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Kurulumu yapın:** İndirdiğiniz dosyayı çalıştırın ve kurulum sihirbazını takip edin
3. **Docker'ı başlatın:** Bilgisayarınızı yeniden başlattıktan sonra Docker Desktop uygulamasını açın
4. **Hazır olduğunu kontrol edin:** Docker Desktop açıldığında, sol üst köşede "Docker Desktop is running" yazısını görmelisiniz

#### Adım 2: Proje Klasörüne Gitme

Terminal (komut satırı) açın ve proje klasörüne gidin:

```bash
cd "C:\Users\Asus\Desktop\49X Final"
```

#### Adım 3: Docker Compose ile Veritabanını Başlatma

**Docker Compose nedir?** Birden fazla uygulamayı (PostgreSQL + pgAdmin) birlikte çalıştırmamızı sağlayan bir araçtır.

Proje klasöründe `docker-compose.yml` adında bir dosya var. Bu dosya, Docker'a şunu söyler:
- PostgreSQL veritabanını başlat
- pgAdmin (veritabanı yönetim arayüzü) uygulamasını başlat
- İkisini birbirine bağla

**Komut:**
```bash
docker-compose up -d
```

**Ne yapar?**
- `up`: Uygulamaları başlat
- `-d`: Arka planda çalıştır (detached mode)

**Beklenen çıktı:**
```
Creating network "49x-final_ce49x_network" ... done
Creating volume "49x-final_postgres_data" ... done
Creating ce49x_postgres ... done
Creating ce49x_pgadmin ... done
```

#### Adım 4: Veritabanının Hazır Olduğunu Kontrol Etme

```bash
docker-compose ps
```

**Beklenen çıktı:**
```
NAME                STATUS          PORTS
ce49x_postgres      Up (healthy)    0.0.0.0:5432->5432/tcp
ce49x_pgadmin       Up               0.0.0.0:5050->80/tcp
```

Her iki servis de "Up" durumunda olmalı.

### 🗄️ PostgreSQL Nedir?

**PostgreSQL**, verileri saklamak için kullanılan bir veritabanı sistemidir. Excel tablosu gibi düşünebilirsiniz, ama çok daha güçlü:

- **Excel:** Bir tabloda veri saklarsınız
- **PostgreSQL:** Birden fazla tabloda veri saklar, tablolar arası ilişkiler kurar, hızlı arama yapar

**Projemizde ne için kullandık?**
- Toplanan makaleleri sakladık
- Makalelerin sınıflandırma sonuçlarını sakladık
- Analiz sonuçlarını sakladık

### 🎛️ pgAdmin4 Nedir?

**pgAdmin4**, PostgreSQL veritabanını görsel olarak yönetmek için kullanılan bir web arayüzüdür. Excel'i açıp tabloları görmek gibi düşünebilirsiniz.

**Nasıl kullanılır?**

1. **Tarayıcıda açın:** `http://localhost:5050`
2. **Giriş yapın:**
   - Email: `admin@ce49x.com`
   - Şifre: `admin`
3. **Veritabanına bağlanın:**
   - Sol tarafta "Servers" üzerine sağ tıklayın
   - "Register" > "Server" seçin
   - **General** sekmesi:
     - Name: `CE49X Database`
   - **Connection** sekmesi:
     - Host: `postgres` (Docker içindeki servis adı)
     - Port: `5432`
     - Database: `ce49x_db`
     - Username: `ce49x_user`
     - Password: `ce49x_password`
   - "Save" butonuna tıklayın

4. **Tabloları görüntüleyin:**
   - Sol tarafta `CE49X Database` > `Databases` > `ce49x_db` > `Schemas` > `public` > `Tables`
   - Burada tüm tabloları görebilirsiniz

### 📊 Veritabanı Yapısı

Proje başladığında, `database/init.sql` dosyası otomatik olarak çalıştırıldı ve şu tablolar oluşturuldu:

1. **articles** - Toplanan makaleler
   - `id`: Makale numarası
   - `title`: Başlık
   - `url`: Makale linki
   - `content`: İçerik
   - vb.

2. **classifications** - LLM ile yapılan sınıflandırmalar
   - `article_id`: Hangi makale
   - `ce_areas[]`: CE alanları (ör: Structural, Transportation)
   - `ai_technologies[]`: AI teknolojileri (ör: Computer Vision, Predictive Analytics)
   - `confidence_score`: Güven skoru

3. **all_valid_articles** - Tüm valid makalelerin birleştirilmiş hali
   - NewsAPI, Guardian, Corpus kaynaklarından gelen valid makaleler
   - Final analiz için kullanılan tablo

### 🔧 Veritabanı Bağlantı Ayarları

Python scriptlerinin veritabanına bağlanabilmesi için `.env` dosyası oluşturuldu:

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

**Neden `.env` dosyası?**
- Hassas bilgileri (şifreler, API anahtarları) kod içinde saklamamak için
- Herkes kendi bilgilerini ekleyebilir
- Git'e yüklenmez (`.gitignore` içinde)

### ✅ Kurulum Kontrolü

Veritabanının düzgün çalıştığını kontrol etmek için:

```bash
python -c "from database.db_config import test_connection; print('✓ Bağlantı başarılı!' if test_connection() else '✗ Bağlantı hatası!')"
```

**Başarılı çıktı:** `✓ Bağlantı başarılı!`

### 🛑 Veritabanını Durdurma

İşiniz bittiğinde veritabanını durdurmak için:

```bash
docker-compose down
```

**Verileri de silmek isterseniz:**
```bash
docker-compose down -v
```

⚠️ **Dikkat:** `-v` parametresi tüm verileri siler!

### 📝 Özet

1. **Docker Desktop** kuruldu
2. **docker-compose up -d** komutuyla PostgreSQL ve pgAdmin başlatıldı
3. **pgAdmin4** ile veritabanı görsel olarak yönetildi
4. **Python scriptleri** `.env` dosyasındaki ayarlarla veritabanına bağlandı
5. **Tüm veriler** PostgreSQL'de saklandı ve analiz edildi

**Sonuç:** 1155 valid makale `all_valid_articles` tablosunda saklandı ve tüm analizler bu tablo üzerinden yapıldı.

---

## Task 1: Data Collection (Veri Toplama)

### 1.1 NewsAPI Veri Toplama
**Script:** `scripts/collect_newsapi.py`
- **Amaç:** NewsAPI kullanarak CE ve AI konulu haber makalelerini toplama
- **Özellikler:**
  - NewsAPI "everything" endpoint kullanımı
  - CE ve AI keyword kombinasyonları ile arama
  - Metadata toplama (title, publication_date, source, url, description)
  - CSV formatında kayıt
- **Çıktı:** `data/newsapi_articles_*.csv`

### 1.2 Guardian API Veri Toplama
**Script:** `scripts/collect_guardian.py`
- **Amaç:** Guardian Open Platform API ile makale toplama
- **Özellikler:**
  - Guardian API kullanımı
  - Full text extraction (trafilatura)
  - Strict filtreleme (minimum 1 CE + 1 AI keyword)
  - API limit koruması
- **Çıktı:** `data/guardian_articles_*.csv`

### 1.3 RSS Feed Toplama
**Script:** `scripts/collect_rss.py`
- **Amaç:** RSS feed'lerden makale toplama
- **Özellikler:**
  - RSS feed parsing
  - Multiple source support
- **Çıktı:** `data/rss_articles_*.csv`

### 1.4 Corpus Veri İçe Aktarma
**Script:** `scripts/import_corpus_to_db.py`
- **Amaç:** Mevcut corpus verilerini veritabanına aktarma
- **Çıktı:** `data/corpus.csv` → Database

---

## Task 2: Text Preprocessing & NLP

### 📍 NLP Kısmının Konumu ve Detayları

**Ana NLP Scriptleri:**
- `scripts/preprocess_newsapi.py` - Ana preprocessing script
- `scripts/generate_preprocessing_report.py` - Rapor oluşturma
- `scripts/create_cleaned_dataset.py` - Cleaned dataset oluşturma

**NLP Çıktı Dosyaları:**
- `data/top20_most_frequent_words.csv` - Top 20 kelime listesi
- `data/top20_bigrams.csv` - Top 20 bi-gram listesi
- `data/preprocessing_report.md` - Detaylı preprocessing raporu
- `data/cleaned_dataset.csv` - Temizlenmiş dataset (1155 makale)

---

### 2.1 NewsAPI Veri Ön İşleme
**Script:** `scripts/preprocess_newsapi.py`
- **Dosya Yolu:** `49X Final/scripts/preprocess_newsapi.py`
- **Amaç:** NewsAPI verilerini temizleme ve ön işleme
- **Kullanılan NLP Kütüphaneleri:**
  - `nltk` - Tokenization, stopword removal, lemmatization
  - `scikit-learn` - TF-IDF calculation
- **NLP İşlemleri (Sırayla):**
  1. **Tokenization** - `nltk.word_tokenize()` ve `nltk.sent_tokenize()` kullanılarak
  2. **Normalization** - Lowercasing, punctuation removal, URL/email removal
  3. **Stopword Removal** - NLTK English stopwords + domain-specific stopwords (article, read, more, click, etc.)
  4. **Lemmatization** - `nltk.WordNetLemmatizer()` ile kelimeleri kök formuna indirgeme
  5. **N-grams Extraction** - `nltk.ngrams()` ile bigrams ve trigrams çıkarımı
  6. **TF-IDF Calculation** - `sklearn.TfidfVectorizer()` ile term frequency-inverse document frequency hesaplama
- **Fonksiyonlar:**
  - `normalize_text()` - Text normalizasyonu
  - `remove_stopwords()` - Stopword kaldırma
  - `lemmatize_text()` - Lemmatization
  - `extract_ngrams()` - N-gram çıkarımı
  - `calculate_tfidf()` - TF-IDF hesaplama
- **Çıktı:** Processed data with `processed_text`, `bigrams`, `trigrams`, `top_tfidf_terms` kolonları

### 2.2 Preprocessing Raporları Oluşturma
**Script:** `scripts/generate_preprocessing_report.py` ✅ YENİ
- **Dosya Yolu:** `49X Final/scripts/generate_preprocessing_report.py`
- **Amaç:** Task 2 gereksinimleri için preprocessing raporları oluşturma
- **Veri Kaynağı:** `all_valid_articles` tablosundan 1155 makale
- **NLP İşlemleri:**
  - Text birleştirme (title + description + abstract)
  - Normalization (lowercasing, URL/email removal)
  - Stopword removal (NLTK + domain-specific)
  - Word frequency counting (Counter kullanarak)
  - Bigram extraction ve frequency counting
- **Özellikler:**
  - Top 20 most frequent words hesaplama (stopwords hariç)
  - Top 20 bi-grams hesaplama
  - Markdown formatında detaylı rapor
- **Çıktılar:**
  - `data/top20_most_frequent_words.csv` - Rank, Word, Frequency kolonları ile
  - `data/top20_bigrams.csv` - Rank, Bigram, Frequency kolonları ile
  - `data/preprocessing_report.md` - Detaylı preprocessing raporu (markdown formatında)
- **Durum:** ✅ KULLANILDI - 1155 makale üzerinden raporlar oluşturuldu
- **Sonuçlar:**
  - Top Word: "market" (598 kez)
  - Top Bigram: "artificial intelligence" (203 kez)

### 2.3 Cleaned Dataset Oluşturma
**Script:** `scripts/create_cleaned_dataset.py` ✅ YENİ
- **Dosya Yolu:** `49X Final/scripts/create_cleaned_dataset.py`
- **Amaç:** Temizlenmiş dataset oluşturma (Task 2 gereksinimi)
- **Veri Kaynağı:** `all_valid_articles` tablosundan
- **NLP İşlemleri:**
  1. Text birleştirme (title + description + abstract)
  2. Normalization:
     - Lowercasing
     - Punctuation removal
     - URL removal (regex: `r'http\S+|www\.\S+'`)
     - Email removal (regex: `r'\S+@\S+'`)
     - Special characters removal (sadece alphanumeric ve spaces)
  3. Stopword removal:
     - Common English stopwords (the, a, an, and, or, etc.)
     - Domain-specific stopwords (article, read, more, click, subscribe, etc.)
     - Words with length <= 2 characters excluded
- **Çıktı:** `data/cleaned_dataset.csv` - 1155 makale, temizlenmiş text ile
- **Kolonlar:**
  - `id`, `title`, `description`, `url`, `source`, `publication_date`
  - `abstract`, `ce_areas`, `ai_technologies`, `cleaned_text`
- **Durum:** ✅ KULLANILDI - Cleaned dataset oluşturuldu
- **İstatistikler:**
  - Toplam makale: 1155
  - Ortalama cleaned text uzunluğu: ~560 karakter

### 2.4 AI/CE Filtreleme
**Script:** `scripts/filter_ai_ce_articles.py`
- **Amaç:** Sadece AI ve CE kesişimini içeren makaleleri filtreleme
- **Çıktı:** `data/filtered_ai_ce_articles.csv`

### 2.5 Common Usage Filtreleme
**Script:** `scripts/filter_common_usage.py`
- **Amaç:** Genel kullanım içeren makaleleri filtreleme
- **Çıktı:** `data/common_usage_articles.csv`

---

## Task 3: Categorization & Trend Analysis

### 3.1 Guardian Makale Validasyonu
**Script:** `scripts/validate_guardian_ce_keywords.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Guardian makalelerinde CE keyword'lerinin geçerliliğini LLM ile kontrol etme
- **Yöntem:** OpenAI GPT-3.5-turbo API
- **Durum:** Kullanıldı, validasyon yapıldı, sonra daha esnek versiyonla değiştirildi
- **Çıktı:** `data/guardian_ce_keyword_validation.csv`

**Script:** `scripts/revalidate_guardian_flexible.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Daha esnek kriterlerle Guardian makalelerini yeniden validasyon
- **Değişiklik:** Daha düşük confidence threshold, daha geniş CE yorumu
- **Durum:** Kullanıldı, daha fazla valid makale bulundu, işlevi tamamlandı
- **Çıktı:** `data/guardian_ce_keyword_validation_flexible.csv`

**Script:** `scripts/save_guardian_valid.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Valid Guardian makalelerini ayrı CSV'ye kaydetme
- **Durum:** Kullanıldı, valid makaleler kaydedildi, işlevi tamamlandı
- **Çıktı:** `data/guardian_valid.csv`

### 3.2 Corpus Makale Validasyonu
**Script:** `scripts/validate_corpus_ce.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Corpus makalelerini LLM ile validasyon
- **Durum:** Kullanıldı, corpus makaleleri validate edildi, işlevi tamamlandı
- **Çıktı:** `data/corpus_valid.csv`

### 3.3 NewsAPI Makale Validasyonu
**Script:** `scripts/validate_newsapi_flexible.py`
- **Amaç:** NewsAPI makalelerini esnek kriterlerle validasyon
- **Yöntem:** LLM-based validation
- **Çıktı:** `data/newsapi_validation_flexible.csv`

**Script:** `scripts/validate_newsapi_comprehensive_flexible.py`
- **Amaç:** Kapsamlı ve esnek NewsAPI validasyonu
- **Çıktı:** `data/newsapi_validation_comprehensive.csv`

**Script:** `scripts/validate_newsapi_ce_ai_intersection.py`
- **Amaç:** NewsAPI makalelerinde CE ve AI kesişimini kontrol etme
- **Çıktı:** `data/newsapi_ce_ai_validation.csv`

**Script:** `scripts/validate_newsapi_ai_ce_intersection.py`
- **Amaç:** AI ve CE kesişimini ters yönden kontrol
- **Çıktı:** `data/newsapi_ai_ce_validation.csv`

**Script:** `scripts/create_newsapi_valid_from_validation.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Validasyon sonuçlarından valid NewsAPI makalelerini oluşturma
- **Durum:** Kullanıldı, valid NewsAPI makaleleri oluşturuldu, işlevi tamamlandı
- **Çıktı:** `data/newsapi_valid.csv`

### 3.4 Dictionary-Based Classification
**Script:** `scripts/classify_ce_ai.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Dictionary-based CE ve AI sınıflandırması
- **Yöntem:** Keyword matching
- **Durum:** Kullanıldı, test edildi, sonra LLM-based versiyonla değiştirildi
- **CE Areas:** Structural, Geotechnical, Transportation, Construction Management, Environmental Engineering
- **AI Technologies:** Computer Vision, Predictive Analytics, Generative Design, Robotics/Automation
- **Çıktı:** `data/articles_tagged.csv`

### 3.5 LLM-Based Classification
**Script:** `scripts/classify_ce_ai_llm.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** LLM API kullanarak daha doğru sınıflandırma
- **Yöntem:** OpenAI GPT-3.5-turbo
- **Durum:** Kullanıldı, tüm makaleler (NewsAPI, Guardian, Corpus) sınıflandırıldı, işlevi tamamlandı
- **Özellikler:**
  - Her makale için CE areas ve AI technologies tagleme
  - Confidence scoring
  - NewsAPI, Guardian, Corpus verilerini işleme
- **Çıktı:** `data/articles_tagged_llm.csv`, `data/articles_tagged_llm_complete.csv`
- **Not:** Tüm makaleler başarıyla sınıflandırıldı ve sonuçlar veritabanına aktarıldı. İşlevi tamamlandıktan sonra temizlik sırasında silindi.

**Script:** `scripts/retag_untagged_articles.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Taglenmemiş makaleleri yeniden tagleme
- **Durum:** Kullanıldı, eksik tag'ler tamamlandı, tüm valid makalelerin en az 1 CE ve 1 AI tag'i olduğu garanti edildi
- **Özellik:** Tüm valid makalelerin en az 1 CE ve 1 AI tag'i olmasını sağlama

### 3.6 Classification Analysis
**Script:** `scripts/classify_and_analyze.py`
- **Amaç:** Sınıflandırma sonuçlarını analiz etme
- **Çıktılar:**
  - `data/classification_analysis.csv`
  - `data/heatmap_ce_ai.png`
  - `data/bar_chart_*.png`

**Script:** `scripts/generate_classification_report.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Sınıflandırma raporu oluşturma
- **Durum:** Kullanıldı, rapor oluşturuldu, işlevi tamamlandı
- **Çıktı:** `data/classification_report.md`

---

## Task 4: Visualization & Insights

### 4.1 Co-occurrence Heatmaps
**Script:** `scripts/create_normalized_ce_ai_heatmap.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Normalize edilmiş CE × AI co-occurrence heatmap
- **Durum:** Kullanıldı, heatmap oluşturuldu, işlevi tamamlandı
- **Özellikler:**
  - Row-wise normalization
  - Percentage annotations
- **Çıktı:** `data/heatmap_ce_ai_specialization_LQ.png`, `data/ce_ai_cooccurrence_normalized.csv`

**Script:** `scripts/create_dual_ce_ai_heatmaps.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Hem raw counts hem normalized percentages için dual heatmaps
- **Durum:** Kullanıldı, her iki heatmap oluşturuldu, işlevi tamamlandı
- **Çıktılar:**
  - `data/heatmap_ce_ai_raw_counts.png`
  - `data/heatmap_ce_ai_normalized.png`
  - `data/ce_ai_cooccurrence_raw_counts.csv`
  - `data/ce_ai_cooccurrence_normalized.csv`

### 4.2 Temporal Analysis
**Script:** `scripts/time_series_analysis.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Makale hacminin zaman serisi analizi
- **Durum:** Kullanıldı, zaman serisi analizi yapıldı, görselleştirme oluşturuldu
- **Özellikler:**
  - Günlük/haftalık aggregasyon
  - Rolling average (7-day/14-day)
  - Otomatik spike detection (z-score based)
- **Çıktılar:**
  - `data/time_series_total_articles_with_rolling_avg.png`
  - `data/time_series_article_counts.csv`

**Script:** `scripts/temporal_trends_analysis.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Belirli CE×AI kombinasyonlarının temporal trendleri
- **Durum:** Kullanıldı, temporal trendler analiz edildi, işlevi tamamlandı
- **Çıktı:** `data/temporal_trends.csv`, `data/temporal_trends.png`

### 4.3 Bump Chart
**Script:** `scripts/create_bump_chart_combinations.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Top 10 CE×AI kombinasyonlarının rank evrimi
- **Durum:** Kullanıldı, bump chart oluşturuldu, işlevi tamamlandı
- **Özellikler:**
  - Aylık rank hesaplama
  - Bump chart visualization
- **Çıktılar:**
  - `data/bump_chart_top10_combinations.png`
  - `data/combination_rank_over_time.csv`

### 4.4 Emergence Analysis
**Script:** `scripts/create_emergence_scatter.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Yükselen CE×AI kombinasyonlarını belirleme
- **Durum:** Kullanıldı, emergence analizi yapıldı, scatter plot oluşturuldu
- **Özellikler:**
  - x-axis: Recency (ilk görünümden bu yana geçen gün)
  - y-axis: Growth rate (son dönem vs önceki dönem)
  - Point size: Total article count
- **Çıktılar:**
  - `data/emergence_scatter_recency_vs_growth.png`
  - `data/emergence_metrics_combinations.csv`

### 4.5 Long-tail Distribution Analysis
**Script:** `scripts/analyze_longtail_distribution.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** CE×AI kombinasyonlarının long-tail dağılımını analiz etme
- **Durum:** Kullanıldı, long-tail analizi yapıldı, log-log plot oluşturuldu
- **Özellikler:**
  - Log-log plot
  - Power-law reference line
  - Pareto analysis
- **Çıktılar:**
  - `data/loglog_pareto_combination_frequency.png`
  - `data/combination_frequency_ranked.csv`

### 4.6 Source Analysis
**Script:** `scripts/create_source_combination_heatmap.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Hangi kaynakların hangi CE×AI kombinasyonlarını kapsadığını gösterme
- **Durum:** Kullanıldı, source analysis heatmap oluşturuldu, işlevi tamamlandı
- **Çıktılar:**
  - `data/heatmap_source_by_combination.png`
  - `data/source_combination_matrix.csv`

### 4.7 Word Clouds
**Script:** `scripts/create_wordclouds_by_ce_area.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Her CE alanı için AI-filtreli word cloud'lar
- **Durum:** Kullanıldı, 5 CE area için word cloud'lar oluşturuldu, işlevi tamamlandı
- **Özellikler:**
  - Her CE area için ayrı word cloud
  - AI keyword'leri içeren makalelerden oluşturuldu
  - Minimum article count kontrolü
  - High resolution (dpi >= 200)
- **Çıktılar:**
  - `data/wc_structural_ai.png`
  - `data/wc_geotechnical_ai.png`
  - `data/wc_transportation_ai.png`
  - `data/wc_construction_mgmt_ai.png`
  - `data/wc_environmental_ai.png`
  - `data/top_terms_*.csv` (her CE area için)

**Script:** `scripts/create_ai_wordclouds_and_contrast.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Her AI teknolojisi için CE-filtreli word cloud'lar ve contrastive word clouds
- **Durum:** Kullanıldı, 4 AI tech + 2 contrastive word cloud oluşturuldu, işlevi tamamlandı
- **Özellikler:**
  - Her AI tech için ayrı word cloud
  - CE keyword'leri içeren makalelerden oluşturuldu
  - Contrastive word clouds (Transportation+AI vs Structural+AI, Construction Mgmt+AI vs Environmental+AI)
  - TF-IDF difference kullanarak distinctive terms
- **Çıktılar:**
  - `data/wc_cv_in_ce.png`
  - `data/wc_predictive_in_ce.png`
  - `data/wc_genai_in_ce.png`
  - `data/wc_robotics_in_ce.png`
  - `data/wc_contrast_transport_vs_structural.png`
  - `data/wc_contrast_conmgmt_vs_env.png`
  - `data/top_terms_*.csv` (her AI tech için)
  - `data/contrast_*.csv` (contrastive terms)

**Script:** `scripts/create_ce_area_top_terms_csv.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** CE area word cloud'ları için top terms CSV'leri oluşturma
- **Durum:** Kullanıldı, CSV'ler oluşturuldu, işlevi tamamlandı
- **Çıktı:** `data/top_terms_*.csv`

### 4.8 Network Graphs
**Script:** `scripts/create_keyword_network_graphs.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Keyword co-occurrence network grafikleri
- **Durum:** Kullanıldı, 3 network graph oluşturuldu (full, CE-only, bipartite), işlevi tamamlandı
- **Özellikler:**
  - Full keyword network (CE + AI together)
  - CE-only keyword network
  - Bipartite network (CE keywords ↔ AI keywords only)
  - Community detection (Louvain algorithm)
  - Centrality measures (degree, betweenness)
  - Hub ve bridge node identification
- **Çıktılar:**
  - `data/network_full_keywords.png`
  - `data/network_ce_only.png`
  - `data/network_bipartite_ce_to_ai.png`
  - `data/network_metrics_full.csv`
  - `data/network_metrics_ce.csv`
  - `data/network_metrics_bipartite.csv`
  - `data/network_top_bridges.csv`
  - `data/network_insights.txt`

### 4.9 Specialization Analysis
**Script:** `scripts/analyze_ai_specialization_lq.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Location Quotient (LQ) kullanarak AI teknolojilerinin CE alanlarına özelleşmesini analiz etme
- **Durum:** Kullanıldı, LQ analizi yapıldı, heatmap oluşturuldu, işlevi tamamlandı
- **Formül:** LQ = (share of AI within CE) / (overall share of AI)
- **Yorum:** LQ > 1 = CE domain is over-represented for that AI tech
- **Çıktılar:**
  - `data/heatmap_ce_ai_specialization_LQ.png`
  - `data/ce_ai_location_quotient.csv`

### 4.10 AI Maturity Ranking
**Script:** `scripts/rank_ce_areas_by_ai_maturity.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** CE alanlarını AI olgunluğu/ilgi düzeyine göre sıralama
- **Durum:** Kullanıldı, final ranking analizi yapıldı, görselleştirme oluşturuldu, işlevi tamamlandı
- **Metrikler:**
  - Article Volume (30%)
  - AI Diversity (25%)
  - Specialization/LQ (25%)
  - Growth Trend (20%)
- **Çıktılar:**
  - `data/ce_ai_maturity_ranking.csv`
  - `data/ce_ai_maturity_ranking.png`

---

## Database Management

### 5.1 Database Migration
**Script:** `scripts/migrate_to_postgres.py`
- **Amaç:** SQLite'den PostgreSQL'e veri migrasyonu
- **Özellikler:**
  - Connection pooling
  - Batch processing

### 5.2 NewsAPI Database Import
**Script:** `scripts/import_newsapi_csv_to_db.py`
- **Amaç:** NewsAPI CSV dosyalarını veritabanına aktarma
- **Tablo:** `newsapi_articles`

### 5.3 Valid Articles Database Operations
**Script:** `scripts/save_valid_newsapi_to_db.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Valid NewsAPI makalelerini ayrı tabloya kaydetme
- **Durum:** Kullanıldı, valid NewsAPI makaleleri kaydedildi, işlevi tamamlandı
- **Tablo:** `newsapi_valid`

**Script:** `scripts/merge_all_valid_to_db.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Tüm valid makaleleri (NewsAPI, Guardian, Corpus) birleştirme
- **Durum:** Kullanıldı, tüm kaynaklar birleştirildi, unified table oluşturuldu
- **Tablo:** `all_valid_articles`
- **Özellikler:**
  - Column standardization
  - Date format conversion

**Script:** `scripts/add_abstracts_to_unified_table.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Önceki tablolardan abstract'leri birleştirilmiş tabloya ekleme
- **Durum:** Kullanıldı, abstract'ler eklendi, işlevi tamamlandı

**Script:** `scripts/remove_duplicates_from_unified_table.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** URL ve title'a göre duplicate'leri kaldırma
- **Durum:** Kullanıldı, duplicate'ler temizlendi, işlevi tamamlandı
- **Yöntem:** URL ve title kombinasyonuna göre, sonra URL'e göre, sonra title'a göre

**Script:** `scripts/generate_abstracts_for_unified_table.py` ✅ KULLANILDI (sonra silindi)
- **Amaç:** Abstract'i olmayan makaleler için LLM ile abstract oluşturma
- **Durum:** Kullanıldı, eksik abstract'ler LLM ile oluşturuldu, işlevi tamamlandı
- **Yöntem:** OpenAI GPT-3.5-turbo

### 5.4 Database Cleanup
**Script:** `scripts/remove_columns_from_unified_table.py`
- **Amaç:** Gereksiz kolonları kaldırma
- **Kaldırılan kolonlar:**
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
- **Amaç:** ID kolonunu tablonun başına alma
- **Yöntem:** Tablo yeniden oluşturma

**Script:** `scripts/complete_missing_abstracts_and_renumber_ids.py`
- **Amaç:** 
  1. Eksik abstract'leri tamamlama (LLM ile)
  2. ID'leri 1'den başlayarak yeniden numaralandırma
- **Sonuç:** 1155 makale, ID'ler 1-1155 arası

---

## Final Data Preparation

### 6.1 Duplicate Detection
**Script:** `scripts/detect_duplicates_by_summary.py`
- **Amaç:** Summary-based duplicate detection
- **Çıktı:** `data/duplicate_articles_by_summary.csv`

### 6.2 Abstract Generation
**Script:** `scripts/add_abstracts.py`
- **Amaç:** Makaleler için abstract oluşturma
- **Yöntem:** LLM API

**Script:** `scripts/add_abstracts_filtered.py`
- **Amaç:** Filtrelenmiş makaleler için abstract oluşturma

**Script:** `scripts/add_summaries_newsapi.py`
- **Amaç:** NewsAPI makaleleri için summary ekleme

---

## 📊 Final Database Structure

### `all_valid_articles` Tablosu

**Kolonlar (15 adet):**
1. `id` (integer, PRIMARY KEY) - 1'den başlayarak sıralı
2. `title` (text)
3. `description` (text)
4. `url` (text)
5. `source` (text)
6. `publication_date` (timestamp)
7. `ce_keywords_found` (text)
8. `ai_keywords_found` (text)
9. `ce_areas` (ARRAY) - CE alanları listesi
10. `ce_confidence` (double precision)
11. `ce_reason` (text)
12. `ai_technologies` (ARRAY) - AI teknolojileri listesi
13. `ai_confidence` (double precision)
14. `ai_reason` (text)
15. `abstract` (text)

**Toplam Kayıt:** 1155 makale

### Task 2: Preprocessing Çıktıları ✅

**Cleaned Dataset:**
- `data/cleaned_dataset.csv` - 1155 makale, temizlenmiş text ile
- Her makale için: id, title, description, url, source, publication_date, abstract, ce_areas, ai_technologies, cleaned_text

**Preprocessing Raporları:**
- Top 20 most frequent words: market (598), data (451), technology (395), intelligence (280), infrastructure (226)
- Top 20 bi-grams: artificial intelligence (203), data center (97), machine learning (60), deep learning (45)

---

## 🎯 Proje Sonuçları Özeti

### CE Areas - AI Maturity Ranking (Final)
1. **Construction Management** - 97.4/100
2. **Transportation** - 80.8/100
3. **Structural** - 79.7/100
4. **Environmental Engineering** - 73.7/100
5. **Geotechnical** - 65.7/100

### Key Insights
- **En Yüksek AI Olgunluğu:** Construction Management (686 makale, 4/4 AI teknolojisi)
- **En Yüksek Özelleşme:** Structural (Avg LQ: 1.095)
- **En Dengeli:** Transportation (yüksek hacim + özelleşme dengesi)
- **En Düşük Hacim:** Geotechnical (10 makale)

---

## 📁 Önemli Çıktı Dosyaları

### Task 2: Preprocessing Sonuçları ✅ YENİ
- `data/top20_most_frequent_words.csv` - Top 20 en sık kullanılan kelimeler
- `data/top20_bigrams.csv` - Top 20 en sık kullanılan bi-gramlar
- `data/preprocessing_report.md` - Detaylı preprocessing raporu
- `data/cleaned_dataset.csv` - Temizlenmiş dataset (1155 makale)

### Analiz Sonuçları
- `data/ce_ai_maturity_ranking.csv` - AI maturity ranking
- `data/ce_ai_location_quotient.csv` - Location Quotient matrix
- `data/ce_ai_cooccurrence_raw_counts.csv` - Raw co-occurrence counts
- `data/ce_ai_cooccurrence_normalized.csv` - Normalized co-occurrence percentages

### Görselleştirmeler
- `data/heatmap_ce_ai_specialization_LQ.png` - LQ heatmap
- `data/heatmap_ce_ai_raw_counts.png` - Raw counts heatmap
- `data/heatmap_ce_ai_normalized.png` - Normalized heatmap
- `data/ce_ai_maturity_ranking.png` - Ranking bar chart
- `data/time_series_total_articles_with_rolling_avg.png` - Time series
- `data/bump_chart_top10_combinations.png` - Bump chart
- `data/emergence_scatter_recency_vs_growth.png` - Emergence scatter
- `data/loglog_pareto_combination_frequency.png` - Long-tail distribution
- `data/heatmap_source_by_combination.png` - Source analysis
- `data/network_*.png` - Network graphs (3 adet)
- `data/wc_*.png` - Word clouds (9 adet)

---

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler
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

## 📝 Notlar

- Bazı scriptler silinmiş veya birleştirilmiş olabilir (conversation history'de bahsedilen scriptler)
- Tüm analizler `all_valid_articles` tablosu üzerinden yapılmıştır
- LLM API kullanımı için rate limiting uygulanmıştır
- Database connection pooling kullanılmıştır

---

## 🔍 NLP KISMI HIZLI REFERANS

### 📂 NLP Scriptleri Nerede?
- **Ana Preprocessing:** `scripts/preprocess_newsapi.py`
- **Rapor Oluşturma:** `scripts/generate_preprocessing_report.py`
- **Cleaned Dataset:** `scripts/create_cleaned_dataset.py`

### 📁 NLP Çıktı Dosyaları Nerede?
- **Top 20 Words:** `data/top20_most_frequent_words.csv`
- **Top 20 Bi-grams:** `data/top20_bigrams.csv`
- **Preprocessing Raporu:** `data/preprocessing_report.md`
- **Cleaned Dataset:** `data/cleaned_dataset.csv`

### 📚 NLP Kütüphaneleri
- **NLTK:** Tokenization, stopword removal, lemmatization, n-grams
  - `nltk.word_tokenize()` - Kelime tokenization
  - `nltk.sent_tokenize()` - Cümle tokenization
  - `nltk.corpus.stopwords` - Stopword listesi
  - `nltk.stem.WordNetLemmatizer()` - Lemmatization
  - `nltk.util.ngrams()` - N-gram çıkarımı
- **scikit-learn:** TF-IDF calculation
  - `sklearn.feature_extraction.text.TfidfVectorizer()` - TF-IDF hesaplama

### 🔄 NLP İşlem Adımları (Sıralı)
1. **Tokenization** - Metni kelimelere/cümlelere ayırma (NLTK word_tokenize)
2. **Normalization** - Küçük harfe çevirme, noktalama kaldırma, URL/email temizleme
3. **Stopword Removal** - Yaygın kelimeleri kaldırma (NLTK + domain-specific)
4. **Lemmatization** - Kelimeleri kök formuna indirgeme (NLTK WordNetLemmatizer)
5. **N-grams Extraction** - Bigram ve trigram çıkarımı (NLTK ngrams)
6. **TF-IDF Calculation** - Term frequency-inverse document frequency hesaplama (scikit-learn)

### 📊 NLP Sonuçları
- **Top Word:** market (598 kez)
- **Top Bigram:** artificial intelligence (203 kez)
- **Toplam İşlenen Makale:** 1155
- **Ortalama Cleaned Text Uzunluğu:** ~560 karakter

### 🎯 NLP Kullanım Senaryoları
- **Preprocessing:** `preprocess_newsapi.py` - Ham metinleri temizleme
- **Rapor Oluşturma:** `generate_preprocessing_report.py` - Top 20 words/bi-grams
- **Dataset Hazırlama:** `create_cleaned_dataset.py` - Analiz için temiz dataset

---

## 📌 Önemli Not: "Silindi" İfadesi Hakkında

Bu dokümantasyonda **"✅ KULLANILDI (sonra silindi)"** ifadesi şu anlama gelir:

- ✅ **Script kullanıldı** - Conversation sırasında çalıştırıldı ve işlevini yerine getirdi
- ✅ **İşlevi tamamlandı** - Gerekli analiz/veri işleme yapıldı, çıktılar oluşturuldu
- ✅ **Sonra silindi** - İşlevi tamamlandıktan sonra temizlik sırasında dosya sisteminden kaldırıldı

**Örnekler:**
- `classify_ce_ai_llm.py` → Tüm makaleler sınıflandırıldı, sonuçlar veritabanına aktarıldı, script silindi
- `create_wordclouds_by_ce_area.py` → 5 word cloud oluşturuldu, görseller kaydedildi, script silindi
- `rank_ce_areas_by_ai_maturity.py` → Final ranking analizi yapıldı, görselleştirme oluşturuldu, script silindi

**Hiç kullanılmayan scriptler değildir!** Tüm scriptler conversation sırasında aktif olarak kullanıldı ve proje sonuçlarına katkı sağladı.

---

**Son Güncelleme:** 2025-01-XX
**Proje Durumu:** ✅ Tamamlandı

