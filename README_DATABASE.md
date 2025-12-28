# CE49X Final Project - Database Setup Guide

Bu proje artık CSV dosyaları yerine PostgreSQL veritabanı kullanmaktadır. LLM API entegrasyonu ile makale sınıflandırması yapılmaktadır.

## 🚀 Hızlı Başlangıç

### 1. Docker ile Veritabanını Başlatma

```bash
# Docker Compose ile PostgreSQL ve pgAdmin'i başlat
docker-compose up -d

# Veritabanının hazır olduğunu kontrol et
docker-compose ps
```

### 2. Ortam Değişkenlerini Ayarlama

`.env.example` dosyasını kopyalayıp `.env` olarak kaydedin:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin ve LLM API anahtarınızı ekleyin:

```env
OPENAI_API_KEY=sk-your-key-here
# veya
ANTHROPIC_API_KEY=your-key-here
```

### 3. Python Bağımlılıklarını Yükleme

```bash
pip install -r requirements.txt
```

### 4. Mevcut Verileri Veritabanına Aktarma

Mevcut CSV ve SQLite dosyalarınızı PostgreSQL'e aktarmak için:

```bash
python scripts/migrate_to_postgres.py
```

Bu script:
- `data/articles.sqlite` dosyasından verileri okur
- `data/articles.csv` ve `data_raw/newsapi_articles.csv` dosyalarından verileri okur
- Tüm verileri PostgreSQL veritabanına aktarır

### 5. LLM ile Makale Sınıflandırma

```bash
python scripts/classify_with_llm.py
```

Bu script:
- Veritabanındaki sınıflandırılmamış makaleleri bulur
- LLM API kullanarak her makaleyi sınıflandırır
- Sonuçları veritabanına kaydeder

### 6. Analiz ve Görselleştirme

```bash
python scripts/analyze_from_db.py
```

Bu script:
- Veritabanından sınıflandırılmış makaleleri okur
- Co-occurrence matrix oluşturur
- Görselleştirmeleri (`results/` klasörüne) kaydeder
- Verileri veritabanına kaydeder

## 📊 Veritabanı Yapısı

### Tablolar

1. **articles**: Toplanan makaleler
   - `id`, `title`, `published_at`, `source`, `url`, `content`, vb.

2. **classifications**: LLM ile yapılan sınıflandırmalar
   - `article_id`, `ce_areas[]`, `ai_technologies[]`, `confidence_score`, vb.

3. **cooccurrence_matrix**: CE alanları ve AI teknolojileri eşleşme matrisi

4. **temporal_trends**: Zaman içindeki trendler

5. **sources**: Kaynak metadata

### Views (Görünümler)

- `articles_with_classifications`: Makaleler ve sınıflandırmaları birleştirilmiş görünüm
- `classification_statistics`: İstatistiksel özet görünümü

## 🔧 Veritabanı Yönetimi

### pgAdmin ile Bağlanma

1. Tarayıcıda `http://localhost:5050` adresine gidin
2. Email: `admin@ce49x.com`
3. Şifre: `admin`
4. Yeni server ekleyin:
   - Host: `postgres` (Docker network içinden) veya `localhost` (dışarıdan)
   - Port: `5432`
   - Database: `ce49x_db`
   - Username: `ce49x_user`
   - Password: `ce49x_password`

### Python ile Bağlanma

```python
from database.db_config import get_db_cursor

with get_db_cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM articles")
    count = cur.fetchone()['count']
    print(f"Total articles: {count}")
```

## 📝 Script Açıklamaları

### `migrate_to_postgres.py`
- CSV ve SQLite dosyalarından verileri PostgreSQL'e aktarır
- Duplicate URL'leri atlar
- Sınıflandırma verilerini de aktarır (varsa)

### `classify_with_llm.py`
- LLM API kullanarak makaleleri sınıflandırır
- OpenAI GPT veya Anthropic Claude kullanabilir
- Sonuçları `classifications` tablosuna kaydeder

### `analyze_from_db.py`
- Veritabanından verileri okur
- Co-occurrence matrix ve görselleştirmeler oluşturur
- Sonuçları hem CSV hem de veritabanına kaydeder

### `collect_articles_advanced.py` (Güncellenmiş)
- Artık PostgreSQL kullanıyor (SQLite yerine)
- RSS feed'lerden makale toplar
- Veritabanına direkt kaydeder

## 🔍 Veritabanı Sorguları

### Sınıflandırılmış Makale Sayısı

```sql
SELECT COUNT(*) FROM classifications;
```

### Hem CE hem AI içeren makaleler

```sql
SELECT COUNT(*) 
FROM classifications 
WHERE array_length(ce_areas, 1) > 0 
  AND array_length(ai_technologies, 1) > 0;
```

### En çok kullanılan CE alanları

```sql
SELECT 
    ce_area,
    COUNT(*) as count
FROM classifications,
LATERAL unnest(ce_areas) AS ce_area
GROUP BY ce_area
ORDER BY count DESC;
```

### Co-occurrence matrix'i görüntüleme

```sql
SELECT * FROM cooccurrence_matrix
ORDER BY count DESC;
```

## 🐳 Docker Komutları

```bash
# Container'ları başlat
docker-compose up -d

# Container'ları durdur
docker-compose down

# Logları görüntüle
docker-compose logs -f postgres

# Veritabanını sıfırla (DİKKAT: Tüm veriler silinir!)
docker-compose down -v
docker-compose up -d
```

## ⚠️ Önemli Notlar

1. **API Anahtarları**: LLM API anahtarlarınızı `.env` dosyasına eklemeyi unutmayın
2. **Docker**: Veritabanı Docker container'ında çalışıyor, container'ı kapatırsanız veriler kaybolmaz (volume'de saklanır)
3. **Migration**: Mevcut CSV verilerinizi kaybetmemek için önce `migrate_to_postgres.py` çalıştırın
4. **Backup**: Önemli veriler için düzenli backup alın:

```bash
docker exec ce49x_postgres pg_dump -U ce49x_user ce49x_db > backup.sql
```

## 🆘 Sorun Giderme

### Veritabanına bağlanamıyorum

```bash
# Container'ların çalıştığını kontrol et
docker-compose ps

# Container'ı yeniden başlat
docker-compose restart postgres
```

### LLM API hatası

- API anahtarınızın doğru olduğundan emin olun
- API quota'nızı kontrol edin
- `.env` dosyasının doğru yüklendiğinden emin olun

### Migration hatası

- CSV dosyalarının doğru yolda olduğundan emin olun
- Veritabanı bağlantısını test edin: `python -c "from database.db_config import test_connection; print(test_connection())"`

## 📚 Ek Kaynaklar

- PostgreSQL Dokümantasyonu: https://www.postgresql.org/docs/
- OpenAI API: https://platform.openai.com/docs
- Anthropic API: https://docs.anthropic.com/

