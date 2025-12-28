# 🚀 Hızlı Başlangıç - API Anahtarı Eklendi!

✅ **API anahtarınız `.env` dosyasına eklendi!**

Artık projeyi çalıştırmaya hazırsınız. Şu adımları takip edin:

## 📋 Adım Adım Çalıştırma

### 1️⃣ Docker Container'larını Başlat

```powershell
cd "C:\Users\Asus\Desktop\49X Final"
docker-compose up -d
```

**Kontrol:**
```powershell
docker-compose ps
```

Her iki container (postgres ve pgadmin) "Up" durumunda olmalı.

---

### 2️⃣ Python Paketlerini Yükle

```powershell
pip install -r requirements.txt
```

Bu işlem birkaç dakika sürebilir.

---

### 3️⃣ Veritabanını Test Et

```powershell
python setup_database.py
```

**Beklenen çıktı:**
```
✅ Database connection successful!
✅ All required tables exist
```

---

### 4️⃣ (Opsiyonel) Mevcut Verileri Aktar

Eğer `data/` klasöründe CSV veya SQLite dosyalarınız varsa:

```powershell
python scripts/migrate_to_postgres.py
```

---

### 5️⃣ Makaleleri LLM ile Sınıflandır

```powershell
python scripts/classify_with_llm.py
```

**İlk çalıştırmada:**
- Kaç makale sınıflandırmak istediğiniz sorulacak
- Test için önce **5-10 makale** ile deneyin (maliyet kontrolü)
- Veya tüm makaleleri sınıflandırmak için Enter'a basın

**Beklenen çıktı:**
```
Using LLM provider: openai, model: gpt-3.5-turbo
Found X unclassified articles
How many articles to classify? (Enter for all X): 
```

---

### 6️⃣ Analiz ve Görselleştirme

```powershell
python scripts/analyze_from_db.py
```

Bu script:
- Co-occurrence matrix oluşturur
- Grafikler oluşturur (`results/` klasörüne kaydedilir)
- İstatistikleri gösterir

---

## 🎯 Tüm Komutları Tek Seferde

```powershell
# 1. Docker'ı başlat
cd "C:\Users\Asus\Desktop\49X Final"
docker-compose up -d

# 2. Paketleri yükle (sadece ilk sefer)
pip install -r requirements.txt

# 3. Veritabanını test et
python setup_database.py

# 4. (Opsiyonel) Mevcut verileri aktar
python scripts/migrate_to_postgres.py

# 5. Makaleleri sınıflandır (test için 5-10 makale)
python scripts/classify_with_llm.py

# 6. Analiz yap
python scripts/analyze_from_db.py
```

---

## 💡 İpuçları

1. **İlk test:** Sadece 5-10 makale ile başlayın (~$0.05-0.20 maliyet)
2. **Sonuçlar iyiyse:** Tüm makaleleri sınıflandırın (~$0.50-2.00)
3. **pgAdmin:** `http://localhost:5050` adresinden veritabanını görsel olarak inceleyebilirsiniz
4. **Maliyet takibi:** OpenAI dashboard'dan kullanımı takip edin

---

## ⚠️ Sorun Giderme

### Docker çalışmıyor
```powershell
# Docker Desktop'ın çalıştığından emin olun
# Container'ları yeniden başlatın
docker-compose restart
```

### API anahtarı hatası
```powershell
# .env dosyasını kontrol edin
Get-Content .env | Select-String "OPENAI_API_KEY"
```

### Veritabanı bağlantı hatası
```powershell
# Container'ların durumunu kontrol edin
docker-compose ps

# Logları kontrol edin
docker-compose logs postgres
```

---

## ✅ Başarı Kontrolü

Her şey çalışıyorsa:

1. ✅ `docker-compose ps` → Her iki container "Up"
2. ✅ `python setup_database.py` → "Database connection successful!"
3. ✅ `python scripts/classify_with_llm.py` → Makaleler sınıflandırılıyor
4. ✅ `results/` klasöründe grafikler oluşuyor

---

## 🎉 Hazırsınız!

API anahtarınız eklendi, artık LLM ile makale sınıflandırmaya başlayabilirsiniz!

**Sonraki adım:** Docker'ı başlatın ve `python setup_database.py` ile test edin.

