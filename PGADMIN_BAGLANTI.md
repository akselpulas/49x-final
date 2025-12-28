# pgAdmin Bağlantı Rehberi

## Adım Adım

### 1. pgAdmin'i Açın
- Tarayıcıda: http://localhost:5050
- Email: `admin@ce49x.com`
- Şifre: `admin`

### 2. Server Ekleme
1. Sol tarafta "Servers" üzerine **sağ tıklayın**
2. "Register" → "Server..." seçin

### 3. General Sekmesi
- **Name:** `CE49X Database` (istediğiniz isim)

### 4. Connection Sekmesi (ÖNEMLİ!)
- **Host name/address:** `postgres` (VEYA `localhost`)
- **Port:** `5432`
- **Maintenance database:** `ce49x_db`
- **Username:** `ce49x_user`
- **Password:** `ce49x_password`
- ✅ **"Save password"** işaretleyin

### 5. Save
- "Save" butonuna tıklayın

### 6. Verileri Görme
- Sol menüden: `Servers` → `CE49X Database` → `Databases` → `ce49x_db` → `Schemas` → `public` → `Tables` → `articles`
- `articles` üzerine **sağ tıklayın**
- "View/Edit Data" → "All Rows"

---

## Sorun Giderme

### "Unable to connect to server" hatası
- Host name'i `postgres` yerine `localhost` deneyin
- Docker container'ların çalıştığından emin olun: `docker-compose ps`

### "Password authentication failed" hatası
- Username: `ce49x_user`
- Password: `ce49x_password`
- (docker-compose.yml'deki değerler)

---

## Alternatif: Python ile Görme

pgAdmin kurmak istemiyorsanız:

```powershell
python view_data.py
```

Bu script tüm verileri gösterir.


