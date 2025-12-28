# pgAdmin'de Veri Görme - Adım Adım

## 1. Server'a Bağlanın
- Sol menüde `CE49X Database` (veya server adınız) görünüyor olmalı
- Üzerine tıklayarak genişletin

## 2. Database'e Gidin
- `CE49X Database` → `Databases` → `ce49x_db`
- `ce49x_db` üzerine tıklayın

## 3. Schema'ya Gidin
- `ce49x_db` → `Schemas` → `public`
- `public` üzerine tıklayın

## 4. Tables'a Gidin
- `public` → `Tables`
- `Tables` üzerine tıklayın

## 5. articles Tablosunu Bulun
- `Tables` altında `articles` tablosunu göreceksiniz
- `articles` üzerine **SAĞ TIKLAYIN**

## 6. Verileri Görüntüleyin
- Açılan menüden: **"View/Edit Data"** → **"All Rows"** seçin
- VEYA `articles` üzerine **ÇİFT TIKLAYIN**

## Alternatif: Query Tool
1. `articles` üzerine sağ tıklayın
2. **"Query Tool"** seçin
3. Şu sorguyu yazın:
```sql
SELECT * FROM articles LIMIT 100;
```
4. F5'e basın veya "Execute" butonuna tıklayın

## Hangi Tablolar Var?
- `articles` - Tüm makaleler (2420 adet)
- `classifications` - Sınıflandırmalar (125 adet)
- `cooccurrence_matrix` - Co-occurrence matrisi
- `temporal_trends` - Zaman trendleri
- `sources` - Kaynak bilgileri


