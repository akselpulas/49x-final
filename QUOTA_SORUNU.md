# OpenAI API Quota Sorunu Açıklaması

## Quota Nedir?

**Quota** = Kullanım limiti / Bütçe limiti

OpenAI API kullanırken:
- Her API çağrısı ücretlidir
- Hesabınızda belirli bir kredi/bütçe vardır
- Bu bütçe bittiğinde API çalışmaz

## Hata Mesajı

```
Error code: 429 - insufficient_quota
You exceeded your current quota, please check your plan and billing details.
```

Bu hata = **"Quota'nız doldu, daha fazla kullanamazsınız"** demektir.

## Neden Olur?

1. **Ücretsiz kredi bitti**
   - Yeni hesaplarda $5 ücretsiz kredi var
   - Bu kredi bittiğinde quota hatası alırsınız

2. **Aylık limit doldu**
   - Bazı planlarda aylık kullanım limiti vardır
   - Limit dolduğunda hata alırsınız

3. **Ödeme yapılmadı**
   - Kredi kartı eklenmemiş olabilir
   - Ödeme başarısız olmuş olabilir

## Çözümler

### 1. OpenAI Hesabınızı Kontrol Edin

1. https://platform.openai.com/account/billing adresine gidin
2. Giriş yapın
3. "Usage" sekmesine bakın
4. Kalan krediyi kontrol edin

### 2. Kredi Ekleyin

1. https://platform.openai.com/account/billing
2. "Add payment method" veya "Add credits"
3. Kredi kartı ekleyin
4. Kredi satın alın

### 3. Yeni API Anahtarı

- Yeni bir OpenAI hesabı açın
- Yeni $5 ücretsiz kredi alın
- Yeni API anahtarını `.env` dosyasına ekleyin

### 4. Ücretsiz Alternatif (LLM Olmadan)

Eğer quota sorunu devam ederse, basit bir keyword-based abstract oluşturabiliriz (ücretsiz ama daha az kaliteli).

## Maliyet Tahmini

10 makale için abstract oluşturma:
- GPT-3.5-turbo: ~$0.01 - $0.05
- Çok düşük maliyet

130 makale için:
- GPT-3.5-turbo: ~$0.10 - $0.50

## Kontrol Komutu

API anahtarınızın çalışıp çalışmadığını test edin:

```powershell
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('API OK' if client else 'API HATA')"
```

## Özet

- **Quota** = Kullanım limiti
- **Sorun** = Limit dolmuş
- **Çözüm** = Kredi ekle veya yeni hesap aç

