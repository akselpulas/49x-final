# 🚀 CE49X Final Proje - Kurulum Rehberi

Bu rehber, projeyi veritabanı ve LLM API entegrasyonu ile çalıştırmak için adım adım talimatlar içerir.

## 📋 Gereksinimler

- Docker ve Docker Compose
- Python 3.8+
- LLM API anahtarı (OpenAI veya Anthropic)

## 🔧 Adım 1: Docker ile Veritabanını Başlatma

```bash
# Proje klasörüne gidin
cd "49X Final"

# Docker container'ları başlatın
docker-compose up -d

# Container'ların çalıştığını kontrol edin
docker-compose ps
```

PostgreSQL şu adreste çalışacak: `localhost:5432`
pgAdmin şu adreste çalışacak: `http://localhost:5050`

## 🔑 Adım 2: Ortam Değişkenlerini Ayarlama

1. `env_template.txt` dosyasını `.env` olarak kopyalayın:

```bash
# Windows PowerShell
Copy-Item env_template.txt .env

# Linux/Mac
cp env_template.txt .env
```

2. `.env` dosyasını düzenleyin ve LLM API anahtarınızı ekleyin:

```env
# OpenAI kullanıyorsanız:
OPENAI_API_KEY=sk-your-actual-key-here
LLM_PROVIDER=openai

# VEYA Anthropic kullanıyorsanız:
ANTHROPIC_API_KEY=your-actual-key-here
LLM_PROVIDER=anthropic
```

## 📦 Adım 3: Python Bağımlılıklarını Yükleme

```bash
pip install -r requirements.txt
```

## ✅ Adım 4: Veritabanını Kontrol Etme

```bash
python setup_database.py
```

Bu script veritabanı bağlantısını test eder ve şemayı kontrol eder.

## 📥 Adım 5: Mevcut Verileri Aktarma (Opsiyonel)

Eğer mevcut CSV veya SQLite dosyalarınız varsa:

```bash
python scripts/migrate_to_postgres.py
```

Bu script:
- `data/articles.sqlite` dosyasından verileri okur
- `data/articles.csv` ve `data_raw/newsapi_articles.csv` dosyalarından verileri okur
- Tüm verileri PostgreSQL veritabanına aktarır

## 🤖 Adım 6: LLM ile Makale Sınıflandırma

```bash
python scripts/classify_with_llm.py
```

Bu script:
- Veritabanındaki sınıflandırılmamış makaleleri bulur
- LLM API kullanarak her makaleyi sınıflandırır
- Sonuçları veritabanına kaydeder

**Not:** İlk çalıştırmada kaç makale sınıflandırmak istediğiniz sorulacak. Tüm makaleleri sınıflandırmak için Enter'a basın.

## 📊 Adım 7: Analiz ve Görselleştirme

```bash
python scripts/analyze_from_db.py
```

Bu script:
- Veritabanından sınıflandırılmış makaleleri okur
- Co-occurrence matrix oluşturur
- Görselleştirmeleri `results/` klasörüne kaydeder
- Verileri veritabanına kaydeder

## 📝 Yeni Makale Toplama

Yeni makaleler toplamak için:

```bash
python scripts/collect_articles_db.py --max-articles 130
```

## 🔍 Veritabanını Görüntüleme

### pgAdmin ile

1. Tarayıcıda `http://localhost:5050` adresine gidin
2. Email: `admin@ce49x.com`
3. Şifre: `admin`
4. Yeni server ekleyin:
   - **Name:** CE49X Database
   - **Host:** `postgres` (veya `localhost`)
   - **Port:** `5432`
   - **Database:** `ce49x_db`
   - **Username:** `ce49x_user`
   - **Password:** `ce49x_password`

### Python ile

```python
from database.db_config import get_db_cursor

with get_db_cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM articles")
    count = cur.fetchone()['count']
    print(f"Toplam makale: {count}")
```

## 📊 Önemli SQL Sorguları

### Sınıflandırılmış makale sayısı

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

## ⚠️ Sorun Giderme

### Veritabanına bağlanamıyorum

```bash
# Container'ların çalıştığını kontrol et
docker-compose ps

# Container'ı yeniden başlat
docker-compose restart postgres

# Logları kontrol et
docker-compose logs postgres
```

### LLM API hatası

- API anahtarınızın `.env` dosyasında doğru olduğundan emin olun
- API quota'nızı kontrol edin
- Python'da `.env` dosyasının yüklendiğinden emin olun:

```python
from dotenv import load_dotenv
load_dotenv()
```

### Migration hatası

- CSV dosyalarının doğru yolda olduğundan emin olun
- Veritabanı bağlantısını test edin: `python setup_database.py`

## 📚 Dosya Yapısı

```
49X Final/
├── docker-compose.yml          # Docker yapılandırması
├── database/
│   ├── init.sql                # Veritabanı şeması
│   └── db_config.py            # Veritabanı bağlantı yönetimi
├── scripts/
│   ├── migrate_to_postgres.py  # CSV/SQLite → PostgreSQL migration
│   ├── classify_with_llm.py   # LLM ile sınıflandırma
│   ├── analyze_from_db.py     # Veritabanından analiz
│   ├── collect_articles_db.py # Makale toplama (PostgreSQL)
│   └── llm_api.py             # LLM API entegrasyonu
├── data/                       # Eski CSV/SQLite dosyaları (opsiyonel)
├── results/                    # Görselleştirmeler
├── requirements.txt            # Python bağımlılıkları
└── README_DATABASE.md         # Detaylı dokümantasyon
```

## 🎯 Hızlı Başlangıç Özeti

```bash
# 1. Docker'ı başlat
docker-compose up -d

# 2. .env dosyasını oluştur ve API anahtarını ekle
cp env_template.txt .env
# .env dosyasını düzenle

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Veritabanını kontrol et
python setup_database.py

# 5. (Opsiyonel) Mevcut verileri aktar
python scripts/migrate_to_postgres.py

# 6. Makaleleri sınıflandır
python scripts/classify_with_llm.py

# 7. Analiz yap
python scripts/analyze_from_db.py
```

## 💡 İpuçları

1. **130 makale hedefi:** `collect_articles_db.py` scriptini `--max-articles 130` ile çalıştırın
2. **LLM maliyeti:** OpenAI GPT-3.5-turbo daha ucuz, GPT-4 daha doğru
3. **Backup:** Önemli veriler için düzenli backup alın
4. **pgAdmin:** Veritabanını görsel olarak incelemek için pgAdmin kullanın

## 📞 Yardım

Sorun yaşarsanız:
1. `README_DATABASE.md` dosyasına bakın
2. Docker loglarını kontrol edin: `docker-compose logs`
3. Veritabanı bağlantısını test edin: `python setup_database.py`

