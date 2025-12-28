# OpenAI API Quota Artırma Rehberi

## Yöntem 1: OpenAI Hesabına Kredi Eklemek (Önerilen)

### Adımlar:

1. **OpenAI Platform'a Gidin**
   - https://platform.openai.com/account/billing
   - Giriş yapın

2. **Billing Sayfasına Gidin**
   - Sol menüden "Billing" veya "Usage" seçin
   - Veya direkt: https://platform.openai.com/account/billing

3. **Payment Method Ekleyin**
   - "Add payment method" butonuna tıklayın
   - Kredi kartı bilgilerinizi girin
   - Kaydedin

4. **Usage Limits Ayarlayın**
   - "Usage limits" veya "Billing limits" bölümüne gidin
   - "Hard limit" veya "Soft limit" ayarlayın
   - Örnek: $10, $25, $50, $100

5. **Otomatik Ödeme Ayarlayın (Opsiyonel)**
   - "Auto-recharge" özelliğini açın
   - Belirli bir miktarın altına düştüğünde otomatik kredi ekler

### Minimum Tutar:
- Genellikle minimum $5 kredi ekleyebilirsiniz
- Bazı bölgelerde minimum tutar farklı olabilir

---

## Yöntem 2: Usage Limits Artırma

### Adımlar:

1. **Settings'e Gidin**
   - https://platform.openai.com/account/limits
   - Veya Billing sayfasından "Usage limits"

2. **Rate Limits Kontrol Edin**
   - RPM (Requests Per Minute)
   - TPM (Tokens Per Minute)
   - Bu limitler varsayılan olarak düşük olabilir

3. **Limit Artırma İsteği**
   - "Request increase" butonuna tıklayın
   - İhtiyacınızı açıklayın
   - OpenAI onaylar (genellikle 24-48 saat)

---

## Yöntem 3: Yeni Hesap Açmak

Eğer mevcut hesabınıza kredi ekleyemiyorsanız:

1. **Yeni OpenAI Hesabı Açın**
   - https://platform.openai.com/signup
   - Farklı email ile kayıt olun

2. **Yeni API Anahtarı Alın**
   - Settings → API keys
   - Yeni key oluşturun

3. **Yeni API Anahtarını Kullanın**
   - `.env` dosyasını açın
   - `OPENAI_API_KEY` değerini yeni key ile değiştirin

**Not:** Her yeni hesap $5 ücretsiz kredi ile başlar.

---

## Yöntem 4: Farklı Plan Seçmek

### Pay-As-You-Go Plan:
- Kullandığınız kadar ödersiniz
- Minimum limit yok
- Esnek kullanım

### Team/Enterprise Plan:
- Daha yüksek limitler
- Öncelikli destek
- Toplu kullanım için uygun

---

## Hızlı Kontrol

### Mevcut Quota'nızı Kontrol Edin:

1. https://platform.openai.com/account/billing
2. "Usage" sekmesine bakın
3. "Current period" altında kullanımı görün
4. "Available credits" kalan krediyi gösterir

### API Anahtarınızı Test Edin:

```powershell
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('OK' if client else 'HATA')"
```

---

## Öneriler

1. **Başlangıç için:** $10-20 kredi ekleyin
2. **130 makale için:** ~$0.50 yeterli, $5 fazlasıyla yeterli
3. **Auto-recharge:** Düzenli kullanım için açın
4. **Usage alerts:** Email bildirimleri açın

---

## Sorun Giderme

### "Payment method declined" hatası:
- Kredi kartı bilgilerini kontrol edin
- Farklı kart deneyin
- Bankanızla iletişime geçin

### "Limit increase request denied":
- Daha detaylı açıklama yazın
- Kullanım amacınızı belirtin
- Birkaç gün sonra tekrar deneyin

### "Account suspended":
- OpenAI support ile iletişime geçin
- support@openai.com

---

## Maliyet Tahmini

- **10 makale abstract:** ~$0.01-0.05
- **130 makale abstract:** ~$0.10-0.50
- **130 makale sınıflandırma:** ~$0.50-2.00
- **Toplam (tüm işlemler):** ~$1-3

**Önerilen başlangıç kredisi:** $5-10

