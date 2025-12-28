# 🎯 CE49X Final Proje - Veritabanı ve LLM API Yöntemleri

Bu dokümantasyon, projenizde kullanabileceğiniz farklı yöntemleri ve yaklaşımları açıklar.

## 📊 Veritabanı Seçenekleri

### 1. PostgreSQL (Önerilen - Docker ile)

**Avantajlar:**
- ✅ Profesyonel, endüstri standardı veritabanı
- ✅ Docker ile kolay kurulum
- ✅ pgAdmin ile görsel yönetim
- ✅ Array ve JSONB desteği (sınıflandırmalar için ideal)
- ✅ Full-text search özellikleri
- ✅ İlişkisel veri yapısı
- ✅ Transaction desteği

**Kurulum:**
```bash
docker-compose up -d
```

**Kullanım:**
- `database/db_config.py` ile bağlantı yönetimi
- `scripts/migrate_to_postgres.py` ile veri aktarımı
- Tüm scriptler PostgreSQL kullanacak şekilde güncellendi

**Dosyalar:**
- `docker-compose.yml` - Docker yapılandırması
- `database/init.sql` - Veritabanı şeması
- `database/db_config.py` - Bağlantı yönetimi

---

### 2. MySQL/MariaDB (Alternatif)

PostgreSQL yerine MySQL kullanmak isterseniz:

**Değişiklikler:**
1. `docker-compose.yml` dosyasında PostgreSQL yerine MySQL image kullanın
2. `database/db_config.py` dosyasında `psycopg2` yerine `mysql-connector-python` kullanın
3. `database/init.sql` dosyasını MySQL syntax'ına çevirin (array yerine JSON kullanın)

**Avantajlar:**
- ✅ Yaygın kullanılan veritabanı
- ✅ Kolay kurulum

**Dezavantajlar:**
- ❌ Array desteği yok (JSON kullanmak gerekir)
- ❌ Full-text search PostgreSQL kadar güçlü değil

---

### 3. MongoDB (NoSQL Alternatifi)

Eğer NoSQL tercih ederseniz:

**Avantajlar:**
- ✅ Esnek şema yapısı
- ✅ JSON dokümanları doğrudan saklama
- ✅ Array'ler için doğal destek

**Dezavantajlar:**
- ❌ İlişkisel sorgular zor
- ❌ Transaction desteği sınırlı

**Kurulum:**
```yaml
# docker-compose.yml'e ekleyin
mongodb:
  image: mongo:latest
  ports:
    - "27017:27017"
```

---

## 🤖 LLM API Seçenekleri

### 1. OpenAI GPT (Önerilen)

**Modeller:**
- `gpt-3.5-turbo` - Hızlı ve ucuz (önerilen)
- `gpt-4` - Daha doğru ama pahalı
- `gpt-4-turbo` - GPT-4'ün hızlı versiyonu

**Avantajlar:**
- ✅ Kolay entegrasyon
- ✅ İyi dokümantasyon
- ✅ Hızlı yanıt süreleri
- ✅ Uygun fiyat (GPT-3.5 için)

**Kurulum:**
```bash
pip install openai
export OPENAI_API_KEY=sk-your-key-here
```

**Kullanım:**
```python
from scripts.llm_api import get_classifier

classifier = get_classifier(provider='openai')
result = classifier.classify_article(title, content)
```

**Maliyet (yaklaşık):**
- GPT-3.5-turbo: ~$0.0015 per 1K tokens
- GPT-4: ~$0.03 per 1K tokens

---

### 2. Anthropic Claude

**Modeller:**
- `claude-3-sonnet-20240229` - Dengeli (önerilen)
- `claude-3-opus-20240229` - En güçlü ama pahalı
- `claude-3-haiku-20240307` - En hızlı ve ucuz

**Avantajlar:**
- ✅ Uzun context window (200K tokens)
- ✅ İyi sınıflandırma performansı
- ✅ Güvenlik odaklı

**Kurulum:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY=your-key-here
```

**Kullanım:**
```python
classifier = get_classifier(provider='anthropic')
result = classifier.classify_article(title, content)
```

**Maliyet (yaklaşık):**
- Claude-3 Haiku: ~$0.25 per 1M tokens
- Claude-3 Sonnet: ~$3 per 1M tokens
- Claude-3 Opus: ~$15 per 1M tokens

---

### 3. Google Gemini (Alternatif)

**Kurulum:**
```bash
pip install google-generativeai
```

**Kullanım:**
`scripts/llm_api.py` dosyasına Gemini desteği eklenebilir.

**Avantajlar:**
- ✅ Ücretsiz tier mevcut
- ✅ İyi performans

---

### 4. Yerel LLM (Ollama, LM Studio)

Eğer API maliyetinden kaçınmak isterseniz:

**Avantajlar:**
- ✅ Ücretsiz
- ✅ Veri gizliliği
- ✅ Sınırsız kullanım

**Dezavantajlar:**
- ❌ Kurulum karmaşık
- ❌ GPU gereksinimi
- ❌ Daha yavaş

**Kurulum:**
```bash
# Ollama kurulumu
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2

# Python entegrasyonu
pip install ollama
```

---

## 🔄 Veri Akışı Yöntemleri

### Yöntem 1: Tam Otomatik Pipeline

```
1. collect_articles_db.py → PostgreSQL'e makale kaydet
2. classify_with_llm.py → LLM ile sınıflandır
3. analyze_from_db.py → Analiz ve görselleştirme
```

**Avantaj:** Tek komutla tüm süreç

---

### Yöntem 2: Manuel Kontrollü

```
1. collect_articles_db.py → Makaleleri topla
2. pgAdmin ile verileri kontrol et
3. classify_with_llm.py → İstediğin kadarını sınıflandır
4. analyze_from_db.py → Analiz yap
```

**Avantaj:** Her adımda kontrol

---

### Yöntem 3: Batch Processing

```python
# scripts/batch_classify.py (oluşturulabilir)
# Belirli sayıda makaleyi batch'ler halinde işle
for batch in batches:
    classify_batch(batch)
    save_to_db(batch)
```

**Avantaj:** Büyük veri setleri için optimize

---

## 📈 Performans Optimizasyonu

### 1. Paralel İşleme

```python
# classify_with_llm.py'de paralel işleme eklenebilir
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def classify_parallel(articles, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = await asyncio.gather(*[
            executor.submit(classifier.classify_article, a['title'], a['content'])
            for a in articles
        ])
    return results
```

### 2. Caching

```python
# Aynı makaleyi tekrar sınıflandırmamak için
cache = {}
if article_url in cache:
    return cache[article_url]
```

### 3. Batch API Calls

```python
# OpenAI batch API kullanımı (daha ucuz)
# 100 makaleyi tek seferde gönder
```

---

## 💾 Veri Saklama Stratejileri

### Strateji 1: Sadece Veritabanı (Önerilen)

- ✅ Tek kaynak (single source of truth)
- ✅ İlişkisel veri yapısı
- ✅ Transaction güvenliği
- ❌ CSV export gerektiğinde manuel

### Strateji 2: Veritabanı + CSV Sync

```python
# Her güncellemede CSV'ye de yaz
def save_to_db_and_csv(data):
    save_to_db(data)
    export_to_csv()  # Backup için
```

### Strateji 3: Veritabanı + JSON Export

```python
# Analiz için JSON export
def export_for_analysis():
    data = load_from_db()
    json.dump(data, open('analysis_data.json', 'w'))
```

---

## 🔐 Güvenlik ve Best Practices

### 1. API Key Yönetimi

```bash
# .env dosyasını .gitignore'a ekleyin
echo ".env" >> .gitignore

# Production'da environment variables kullanın
export OPENAI_API_KEY=sk-...
```

### 2. Veritabanı Backup

```bash
# Düzenli backup scripti
docker exec ce49x_postgres pg_dump -U ce49x_user ce49x_db > backup_$(date +%Y%m%d).sql
```

### 3. Rate Limiting

```python
# LLM API rate limiting
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
```

---

## 📊 Karşılaştırma Tablosu

| Özellik | PostgreSQL | MySQL | MongoDB | SQLite |
|---------|-----------|-------|---------|--------|
| Docker Kurulum | ✅ Kolay | ✅ Kolay | ✅ Kolay | ❌ Gerekmez |
| Array Desteği | ✅ | ❌ | ✅ | ❌ |
| Full-text Search | ✅ Güçlü | ⚠️ Sınırlı | ⚠️ Sınırlı | ⚠️ Sınırlı |
| İlişkisel | ✅ | ✅ | ❌ | ✅ |
| Ölçeklenebilirlik | ✅ | ✅ | ✅ | ❌ |

| Özellik | OpenAI | Anthropic | Gemini | Yerel LLM |
|---------|--------|-----------|--------|-----------|
| Kurulum | ✅ Kolay | ✅ Kolay | ✅ Kolay | ❌ Zor |
| Maliyet | ⚠️ Orta | ⚠️ Orta | ✅ Düşük | ✅ Ücretsiz |
| Hız | ✅ Hızlı | ✅ Hızlı | ✅ Hızlı | ❌ Yavaş |
| Doğruluk | ✅ Yüksek | ✅ Yüksek | ✅ Yüksek | ⚠️ Değişken |

---

## 🎯 Önerilen Yöntem (Hoca İçin)

**Veritabanı:** PostgreSQL (Docker ile)
- ✅ Profesyonel
- ✅ Kolay kurulum
- ✅ pgAdmin ile görsel yönetim

**LLM API:** OpenAI GPT-3.5-turbo
- ✅ Kolay entegrasyon
- ✅ Uygun maliyet
- ✅ Hızlı yanıt

**Pipeline:**
1. `collect_articles_db.py` - 130 makale topla
2. `classify_with_llm.py` - LLM ile sınıflandır
3. `analyze_from_db.py` - Analiz ve görselleştirme

Bu yöntem profesyonel, ölçeklenebilir ve hoca için uygun bir çözümdür.

---

## 📝 Özet

Projenizde şu yöntemler mevcut:

1. **Veritabanı:** PostgreSQL (Docker) ✅
2. **LLM API:** OpenAI ve Anthropic desteği ✅
3. **Migration:** CSV/SQLite → PostgreSQL ✅
4. **Analiz:** Veritabanı tabanlı analiz ✅
5. **Görselleştirme:** Otomatik grafik oluşturma ✅

Tüm scriptler veritabanı kullanacak şekilde güncellendi ve CSV bağımlılığı kaldırıldı.

