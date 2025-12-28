# 🔑 API Anahtarı Ekleme Rehberi

GPT API anahtarınız varsa, şu adımları takip edin:

## 📝 Adım 1: .env Dosyasını Açın

`.env` dosyası proje klasöründe. Notepad veya herhangi bir editörle açın.

## 🔑 Adım 2: API Anahtarınızı Ekleyin

`.env` dosyasında şu satırı bulun:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

`your_openai_api_key_here` yerine gerçek API anahtarınızı yazın:

```env
OPENAI_API_KEY=sk-proj-abc123xyz789...
```

**Örnek:**
```env
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz
```

## ✅ Adım 3: Provider'ı Ayarlayın

Aynı dosyada şu satırın `openai` olduğundan emin olun:

```env
LLM_PROVIDER=openai
```

## 💾 Adım 4: Dosyayı Kaydedin

Dosyayı kaydedin ve kapatın.

## 🧪 Adım 5: Test Edin

API anahtarınızın çalıştığını test etmek için:

```powershell
python -c "from scripts.llm_api import get_classifier; c = get_classifier(); print('✅ API anahtarı çalışıyor!')"
```

Veya direkt sınıflandırma scriptini çalıştırın:

```powershell
python scripts/classify_with_llm.py
```

## ⚠️ Önemli Notlar

1. **API anahtarı formatı:** `sk-` ile başlamalı
2. **Güvenlik:** `.env` dosyasını asla GitHub'a yüklemeyin
3. **Dosya yolu:** `.env` dosyası proje klasörünün kökünde olmalı

## 🎯 Sonraki Adımlar

API anahtarını ekledikten sonra:

1. ✅ Docker container'larını başlatın: `docker-compose up -d`
2. ✅ Veritabanını kontrol edin: `python setup_database.py`
3. ✅ Makaleleri sınıflandırın: `python scripts/classify_with_llm.py`
4. ✅ Analiz yapın: `python scripts/analyze_from_db.py`

## 💡 İpuçları

- **İlk test:** Sadece 5-10 makale ile test edin
- **Maliyet kontrolü:** OpenAI dashboard'dan kullanımı takip edin
- **Hata durumu:** API anahtarı yanlışsa hata mesajı alırsınız


