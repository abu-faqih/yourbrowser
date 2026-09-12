# Direktori Rilis Build YourBrowser - v0.0.1

Folder ini berisi paket installer APK aplikasi **YourBrowser v0.0.1** yang telah disiapkan untuk pengujian (*testing phase*) di berbagai tipe smartphone Android:

---

## 📱 Panduan Pemilihan APK Sesuai Tipe HP

| File APK | Target Perangkat | Rekomendasi Penggunaan |
| :--- | :--- | :--- |
| **`yourbrowser-v0.0.1-arm64-v8a.apk`** | **Semua HP Android Modern (64-bit)** | **Sangat Direkomendasikan**. Cocok untuk 90%+ HP keluaran tahun 2018 ke atas (Samsung Galaxy, Xiaomi/Redmi/Poco, OPPO, Vivo, Realme, Google Pixel, Infinix, Tecno). |
| **`yourbrowser-v0.0.1-armeabi-v7a.apk`** | **HP Android Lawas / Entry-Level (32-bit)** | Untuk HP Android generasi lama atau prosesor low-end 32-bit. |
| **`yourbrowser-v0.0.1-universal.apk`** | **Semua Tipe Arsitektur** | Mengandung binary lengkap untuk seluruh arsitektur hardware. |
| **`yourbrowser-v0.0.1-x86_64.apk`** | **Emulator PC / Tablet Intel** | Untuk testing di Android Studio Emulator / PC x86_64. |

---

## 🛠️ Cara Instalasi & Testing di HP Fisik

### Metode 1: Lewat ADB (Android Debug Bridge)
Jika HP terhubung via kabel USB dengan opsi *USB Debugging* aktif:
```bash
# Untuk HP Android modern pada umumnya:
adb install -r output/yourbrowser-v0.0.1-arm64-v8a.apk
```

### Metode 2: Pasang Langsung di HP
1. Salin file `yourbrowser-v0.0.1-arm64-v8a.apk` ke HP via WhatsApp / Telegram / File Manager / Google Drive.
2. Buka file APK tersebut di HP.
3. Izinkan *Install unknown apps* jika diminta oleh Android.
4. Buka aplikasi **YourBrowser**.

---

## 🧪 Skenario Pengujian yang Siap Diuji (Testing Checklist)

1. **Inisialisasi & Multi-Vault Password**:
   * Saat pertama kali dibuka, masukkan password tertentu (misal: `kucing123`).
   * Buka beberapa tab atau streaming video.
   * Tekan tombol status `🔒 Vault` di pojok kiri atas -> masukkan password berbeda (misal: `rahasia888`).
   * Verifikasi bahwa sesi penjelajahan langsung berganti ke partisi baru yang bersih tanpa riwayat sebelumnya.
2. **Video Sniffer & Downloader**:
   * Buka situs streaming web apa saja.
   * Putar video -> Perhatikan Floating Action Button `⚡ Unduh (N)` yang akan muncul secara otomatis di pojok kanan bawah.
   * Ketuk tombol tersebut untuk memilih stream/resolusi dan mulai unduhan.
3. **Download Latar Belakang (Foreground Service)**:
   * Saat download berjalan, minimize aplikasi ke Home screen atau kunci layar.
   * Tarik status bar HP -> Verifikasi adanya notifikasi progres unduhan dengan persentase dan kecepatan real-time.
4. **Ekspor Video ke Galeri**:
   * Setelah unduhan selesai, ketuk opsi **"📥 Ekspor ke Galeri Publik"**.
   * Buka Galeri HP atau pemutar video (VLC / MX Player) -> pastikan video muncul di folder *Download/YourBrowser*.
5. **Navigasi Tombol Back Fisik**:
   * Jelajahi beberapa tautan web lalu tekan tombol Back fisik pada HP -> pastikan halaman mundur satu per satu sesuai riwayat web.
