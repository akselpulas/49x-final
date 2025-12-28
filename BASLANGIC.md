# 🚀 Hızlı Başlangıç - Adım Adım

Projeyi çalıştırmak için şu adımları takip edin:

## ✅ Adım 1: Docker Container'larını Başlat

PowerShell'de proje klasörüne gidin ve Docker'ı başlatın:

```powershell
cd "C:\Users\Asus\Desktop\49X Final"
docker-compose up -d
```

**Kontrol:** Container'ların çalıştığını kontrol edin:
```powershell
docker-compose ps
```

Her iki container da (postgres ve pgadmin) "Up" durumunda olmalı.

---

## ✅ Adım 2: .env Dosyası Oluştur

`.env` dosyası yoksa oluşturun:

```powershell
Copy-Item env_template.txt .env
```

Sonra `.env` dosyasını açın ve LLM API anahtarınızı ekleyin:

**OpenAI kullanıyorsanız:**
```env
OPENAI_API_KEY=sk-your-actual-key-here
LLM_PROVIDER=openai
```

**VEYA Anthropic kullanıyorsanız:**
```env
ANTHROPIC_API_KEY=your-actual-key-here
LLM_PROVIDER=anthropic
```

**ÖNEMLİ:** `your-actual-key-here` yerine gerçek API anahtarınızı yazın!

---

## ✅ Adım 3: Python Paketlerini Yükle

```powershell
pip install -r requirements.txt
```

Bu işlem birkaç dakika sürebilir.

---

## ✅ Adım 4: Veritabanını Kontrol Et

```powershell
python setup_database.py
```

Bu script:
- Veritabanı bağlantısını test eder
- Tabloların oluşturulduğunu kontrol eder
- İstatistikleri gösterir

**Başarılı olursa:** "✅ Database connection successful!" mesajını görmelisiniz.

---

## ✅ Adım 5: Mevcut Verileri Aktar (Opsiyonel)

Eğer `data/` klasöründe CSV veya SQLite dosyalarınız varsa:

```powershell
python scripts/migrate_to_postgres.py
```

Bu script mevcut verilerinizi PostgreSQL'e aktarır.

---

## ✅ Adım 6: Makaleleri Sınıflandır

LLM API kullanarak makaleleri sınıflandırın:

```powershell
python scripts/classify_with_llm.py
```

**İlk çalıştırmada:**
- Kaç makale sınıflandırmak istediğiniz sorulacak
- Tüm makaleleri sınıflandırmak için Enter'a basın
- Veya belirli bir sayı girin (örn: 10)

**Not:** Bu işlem API kullanım ücreti gerektirir. OpenAI GPT-3.5-turbo kullanıyorsanız maliyet düşüktür.

---

## ✅ Adım 7: Analiz ve Görselleştirme

Sınıflandırılmış makaleleri analiz edin:

```powershell
python scripts/analyze_from_db.py
```

Bu script:
- Co-occurrence matrix oluşturur
- Grafikler oluşturur (`results/` klasörüne kaydedilir)
- İstatistikleri gösterir

---

## 🎯 Tüm Adımları Tek Seferde

Eğer her şey hazırsa, şu komutları sırayla çalıştırın:

```powershell
# 1. Docker'ı başlat
cd "C:\Users\Asus\Desktop\49X Final"
docker-compose up -d

# 2. .env dosyasını oluştur (sadece ilk sefer)
Copy-Item env_template.txt .env
# .env dosyasını düzenleyip API anahtarınızı ekleyin!

# 3. Paketleri yükle
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

---

## ⚠️ Sorun Giderme

### Docker çalışmıyor
```powershell
# Docker Desktop'ın çalıştığından emin olun
# Container'ları yeniden başlatın
docker-compose restart
```

### Veritabanına bağlanamıyorum
```powershell
# Container'ların durumunu kontrol edin
docker-compose ps

# Logları kontrol edin
docker-compose logs postgres
```

### API anahtarı hatası
- `.env` dosyasının doğru yolda olduğundan emin olun
- API anahtarının doğru olduğundan emin olun
- API quota'nızı kontrol edin

### Python paket hatası
```powershell
# Python sürümünü kontrol edin (3.8+ olmalı)
python --version

# Paketleri tekrar yükleyin
pip install --upgrade -r requirements.txt
```

---

## 📊 Başarı Kontrolü

Her şey çalışıyorsa:

1. ✅ `docker-compose ps` → Her iki container "Up"
2. ✅ `python setup_database.py` → "Database connection successful!"
3. ✅ `python scripts/classify_with_llm.py` → Makaleler sınıflandırılıyor
4. ✅ `results/` klasöründe grafikler oluşuyor

---

## 💡 İpuçları

- **İlk çalıştırma:** Sadece birkaç makale ile test edin (maliyet için)
- **pgAdmin:** `http://localhost:5050` adresinden veritabanını görsel olarak inceleyebilirsiniz
- **Backup:** Önemli veriler için düzenli backup alın
- **API maliyeti:** GPT-3.5-turbo kullanırsanız 130 makale için yaklaşık $1-2 maliyet olur

---

## 🆘 Yardım

Sorun yaşarsanız:
1. `KURULUM.md` dosyasına bakın (detaylı rehber)
2. `README_DATABASE.md` dosyasına bakın (teknik detaylar)
3. Docker loglarını kontrol edin: `docker-compose logs`

