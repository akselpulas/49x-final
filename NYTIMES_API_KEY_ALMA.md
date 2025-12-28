# NYTimes API Key Nasıl Alınır?

## Adım Adım Rehber

### 1. NYTimes Developer Portal'a Gidin
- URL: https://developer.nytimes.com/
- "Get Started" veya "Sign Up" butonuna tıklayın

### 2. Hesap Oluşturun
- Email adresinizle kayıt olun
- Email doğrulaması yapın

### 3. Yeni Uygulama Oluşturun
- Dashboard'a gidin
- "Apps" sekmesine tıklayın
- "New App" veya "+" butonuna tıklayın

### 4. Uygulama Bilgilerini Doldurun
- **App Name**: Örn: "CE49X Article Collector"
- **Description**: Örn: "Collecting articles about Civil Engineering and AI"
- **Organization**: Örn: "Personal" veya okul adınız
- **What type of app are you building?**: "Personal" seçin

### 5. API Seçin
- **Article Search API** seçeneğini işaretleyin
- Bu API ücretsizdir ve günlük 4000 istek limiti vardır

### 6. API Key'inizi Alın
- Uygulama oluşturulduktan sonra size bir API key verilecek
- Bu key'i kopyalayın

### 7. .env Dosyasına Ekleyin
Proje klasörünüzde `.env` dosyasını açın (yoksa oluşturun) ve şunu ekleyin:

```
NYTIMES_API_KEY=your_api_key_here
```

**Örnek:**
```
NYTIMES_API_KEY=AbCdEf123456GhIjKl789012MnOpQr
```

## Önemli Notlar

### Ücretsiz Limitler
- ✅ **Günlük 4000 istek** (yeterli!)
- ✅ **Son 1 yıl veri** erişimi
- ✅ **Ücretsiz** - kredi kartı gerekmez

### API Key Güvenliği
- ⚠️ API key'inizi **asla** GitHub'a yüklemeyin
- ⚠️ `.env` dosyasını `.gitignore`'a ekleyin
- ✅ Sadece kendi bilgisayarınızda kullanın

### API Key Kontrolü
API key'inizin çalışıp çalışmadığını test etmek için:

```bash
python scripts/collect_nytimes.py --target 10 --no-db
```

Bu komut test modunda çalışır ve database'e kaydetmez.

## Alternatif: NewsAPI Kullanmaya Devam

Eğer NYTimes API key almak istemiyorsanız, mevcut **NewsAPI** scriptini kullanmaya devam edebilirsiniz:

```bash
python scripts/collect_newsapi.py --target 1000
```

NewsAPI key'iniz zaten var ve çalışıyor.

## Sorun Giderme

### "API key not found" hatası
- `.env` dosyasında `NYTIMES_API_KEY` değişkeninin doğru yazıldığından emin olun
- Dosya adının `.env` olduğundan emin olun (`.env.txt` değil)

### "Invalid API key" hatası
- API key'inizi tekrar kopyalayıp yapıştırın
- Boşluk veya fazladan karakter olmadığından emin olun

### Rate limit hatası
- Günlük 4000 istek limitine ulaştınız
- Yarın tekrar deneyin veya NewsAPI kullanın

## Yardım

- NYTimes Developer Docs: https://developer.nytimes.com/docs
- API Status: https://developer.nytimes.com/status

