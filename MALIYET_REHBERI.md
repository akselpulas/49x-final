# 💰 LLM API Maliyet Rehberi

## 📊 Maliyet Özeti

### OpenAI GPT Modelleri

| Model | Giriş (1K token) | Çıkış (1K token) | 130 Makale Tahmini Maliyet |
|-------|------------------|------------------|----------------------------|
| **GPT-3.5-turbo** | $0.0005 | $0.0015 | **~$0.50 - $2.00** |
| **GPT-4** | $0.03 | $0.06 | **~$15 - $40** |
| **GPT-4-turbo** | $0.01 | $0.03 | **~$5 - $15** |

**Önerilen:** GPT-3.5-turbo (en ucuz ve yeterli)

### Anthropic Claude Modelleri

| Model | Giriş (1M token) | Çıkış (1M token) | 130 Makale Tahmini Maliyet |
|-------|-------------------|-------------------|----------------------------|
| **Claude-3 Haiku** | $0.25 | $1.25 | **~$0.10 - $0.50** |
| **Claude-3 Sonnet** | $3.00 | $15.00 | **~$1.00 - $3.00** |
| **Claude-3 Opus** | $15.00 | $75.00 | **~$5.00 - $15.00** |

**Önerilen:** Claude-3 Haiku (en ucuz)

---

## 💡 Maliyet Hesaplama

### Bir Makale İçin Tahmini Token Kullanımı

- **Makale başlığı:** ~20-50 token
- **Makale içeriği (ilk 2000 karakter):** ~500-800 token
- **Prompt (sistem mesajı):** ~200-300 token
- **Yanıt (JSON):** ~100-200 token

**Toplam:** ~800-1,350 token per makale

### 130 Makale İçin

- **GPT-3.5-turbo:** 
  - 130 makale × 1,000 token = 130,000 token
  - Maliyet: ~130,000 × $0.0015/1K = **~$0.20 - $0.50**
  
- **GPT-4:**
  - Maliyet: ~130,000 × $0.06/1K = **~$8 - $15**

**Not:** Bu tahminlerdir. Gerçek maliyet makale uzunluğuna göre değişir.

---

## 🆓 Ücretsiz Alternatifler

### 1. Keyword-Based Classification (Mevcut)

Zaten projenizde var! `classify_and_analyze.py` scripti keyword matching kullanıyor.

**Avantajlar:**
- ✅ Tamamen ücretsiz
- ✅ Hızlı
- ✅ Öngörülebilir sonuçlar

**Dezavantajlar:**
- ❌ LLM kadar akıllı değil
- ❌ Bağlam anlayışı yok

**Kullanım:**
```bash
python scripts/classify_and_analyze.py
```

### 2. Yerel LLM (Ollama)

Bilgisayarınızda çalışan ücretsiz LLM.

**Kurulum:**
```bash
# Ollama'yı indirin: https://ollama.ai
# Model indirin
ollama pull llama2
ollama pull mistral
```

**Avantajlar:**
- ✅ Tamamen ücretsiz
- ✅ Veri gizliliği
- ✅ Sınırsız kullanım

**Dezavantajlar:**
- ❌ GPU gereksinimi (hızlı çalışması için)
- ❌ Kurulum karmaşık
- ❌ API'den daha yavaş

### 3. Hugging Face Inference API (Ücretsiz Tier)

Bazı modeller ücretsiz tier sunuyor.

**Avantajlar:**
- ✅ Ücretsiz tier mevcut
- ✅ Kolay entegrasyon

**Dezavantajlar:**
- ❌ Rate limiting (sınırlı istek)
- ❌ Daha az güçlü modeller

---

## 💰 Maliyet Optimizasyonu İpuçları

### 1. Önce Keyword Matching Kullan

```bash
# Önce keyword-based classification yap
python scripts/classify_and_analyze.py

# Sadece sınıflandırılamayanları LLM ile sınıflandır
python scripts/classify_with_llm.py --only-unclassified
```

### 2. Batch Processing

Birden fazla makaleyi tek seferde göndererek maliyeti düşürün.

### 3. İçerik Kısaltma

Makale içeriğini 2000 karakterle sınırlayın (zaten yapıyoruz).

### 4. Cache Kullanımı

Aynı makaleyi tekrar sınıflandırmayın.

### 5. Test İçin Az Makale

İlk test için sadece 5-10 makale ile başlayın.

---

## 🎯 Önerilen Yaklaşım

### Seçenek 1: Düşük Maliyet (Önerilen)

1. **GPT-3.5-turbo kullanın**
   - 130 makale için ~$0.50 - $2.00
   - Yeterince iyi sonuçlar

2. **Önce keyword matching deneyin**
   - Ücretsiz
   - Hızlı
   - Sonuçlar yeterliyse LLM'e gerek yok

### Seçenek 2: Ücretsiz

1. **Sadece keyword matching kullanın**
   - `classify_and_analyze.py` scripti
   - Tamamen ücretsiz
   - Hoca için yeterli olabilir

2. **Manuel kontrol ekleyin**
   - Keyword matching sonuçlarını gözden geçirin
   - Yanlış sınıflandırmaları düzeltin

### Seçenek 3: Hibrit Yaklaşım

1. Keyword matching ile başla
2. Sadece belirsiz makaleleri LLM ile sınıflandır
3. Maliyet: ~$0.10 - $0.50 (sadece 20-30 makale için)

---

## 📝 Hoca İçin Açıklama

**Öğrenci perspektifi:**
- "LLM API kullanımı için küçük bir maliyet var (~$1-2)"
- "Alternatif olarak tamamen ücretsiz keyword-based classification da mevcut"
- "Her iki yöntem de projede implement edildi"

**Hoca için:**
- LLM API entegrasyonu gösterildi ✅
- Ücretsiz alternatif de mevcut ✅
- Veritabanı kullanımı gösterildi ✅
- Docker kullanımı gösterildi ✅

---

## 🔧 Ücretsiz Çalıştırma

Eğer hiç maliyet istemiyorsanız:

### Yöntem 1: Sadece Keyword Matching

```bash
# Mevcut script'i kullan (LLM yok)
python scripts/classify_and_analyze.py
```

Bu script:
- Keyword matching kullanır
- Tamamen ücretsiz
- Hızlı
- Sonuçlar CSV'ye kaydedilir

**Not:** Bu script hala CSV kullanıyor. Veritabanı versiyonu için `analyze_from_db.py` kullanabilirsiniz ama önce keyword-based classification'ı veritabanına eklemeniz gerekir.

### Yöntem 2: Keyword + Veritabanı

Keyword-based classification'ı veritabanına kaydetmek için script oluşturabilirim. İsterseniz söyleyin!

---

## 💡 Sonuç

**En Ucuz Seçenek:**
- GPT-3.5-turbo: ~$0.50 - $2.00 (130 makale)
- Claude-3 Haiku: ~$0.10 - $0.50 (130 makale)

**Ücretsiz Seçenek:**
- Keyword-based classification (mevcut script)
- Yerel LLM (Ollama - kurulum gerekir)

**Öneri:**
- Test için: 5-10 makale ile başla (~$0.05 - $0.20)
- Sonuçlar iyiyse: Tüm makaleleri sınıflandır
- Veya: Sadece keyword matching kullan (ücretsiz)

---

## ❓ Sık Sorulan Sorular

**S: 130 makale için gerçekten $1-2 mi?**
C: Evet, GPT-3.5-turbo kullanırsanız yaklaşık bu kadar.

**S: Ücretsiz çalıştırabilir miyim?**
C: Evet, keyword-based classification tamamen ücretsiz.

**S: API anahtarı almak zor mu?**
C: Hayır, OpenAI'da hesap açıp kredi kartı eklemeniz yeterli. İlk $5 ücretsiz kredi veriyorlar.

**S: Hoca maliyetten bahsederse ne diyeyim?**
C: "LLM API kullanımı için küçük bir maliyet var ama ücretsiz keyword-based alternatif de mevcut. Her iki yöntem de implement edildi."


