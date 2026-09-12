# YourBrowser: Advanced Media Sniffer & Multi-Vault Incognito Android Browser

## Ringkasan Proyek
**YourBrowser** adalah peramban web (*web browser*) Android tingkat lanjut yang dirancang khusus untuk kebutuhan kontrol penuh pengguna tanpa batasan kebijakan pihak ketiga. Dua pilar utama dari peramban ini adalah:
1. **Universal Video Sniffer & Downloader**: Kemampuan mendeteksi, menangkap (*sniffing*), dan mengunduh berbagai format media video yang diputar (Direct MP4, HLS `.m3u8`, MPEG-DASH `.mpd`, dan Blob/MSE stream), dilengkapi engine *parallel chunk downloader* dan *local muxing*.
2. **Multi-Vault Incognito (Zero-Knowledge Multi-Sesi)**: Sistem penjelajahan privat multi-identitas di mana setiap kata sandi (*password*) yang berbeda membuka partisi sesi (*vault*) yang sepenuhnya terisolasi dan terenkripsi. Tidak ada *master key* global; setiap sesi memiliki basis data, cookie, cache, dan penyimpanan lokal yang terpisah secara kriptografis.

---

## Arsitektur & Teknologi

* **Platform & Bahasa**: Android Native, Kotlin
* **Min SDK**: 26 (Android 8.0 Oreo) | **Target SDK**: 34/35 (Android 14/15)
* **Browser Engine**:
  * Opsi Rekomendasi: **Mozilla GeckoView** (Menyediakan isolasi partisi browser context/container murni dan hooks jaringan menyeluruh).
  * Opsi Alternatif: **Android System WebView** dengan isolasi arsitektur multi-proses (`setDataDirectorySuffix`).
* **Security & Kriptografi**:
  * **Argon2id** untuk Key Derivation Function (KDF) dari input kata sandi pengguna.
  * **AES-256-GCM** untuk enkripsi file dan state vault.
  * **SQLCipher** untuk enkripsi database lokal (riwayat, bookmark, download queue).
  * `FLAG_SECURE` dan *in-memory zeroization* (`ByteArray.fill(0)`) untuk mencegah *memory inspection* dan *leakage*.
* **Media & Networking Engine**:
  * **OkHttp** untuk network request inspection dan multi-threaded segmented downloading.
  * **FFmpeg-Kit** / **Android MediaMuxer** untuk muxing segmen video HLS/DASH ke container tunggal `.mp4`.
  * **ExoPlayer / Media3** untuk parser manifest (HLS/DASH).

---

## Fitur Utama

### 1. Universal Video Sniffer & Downloader
* **Network & DOM Interception**: Mendeteksi URL video secara real-time dari header respons HTTP/HTTPS maupun inspeksi tag `<video>` via JavaScript injection bridge.
* **Support Adaptive Streaming**:
  * Direct file: `.mp4`, `.webm`, `.mkv`.
  * Adaptive bitrate streaming: HLS (`.m3u8` manifest parsing, TS / fMP4 segment downloading) & MPEG-DASH (`.mpd`).
* **Resumable & Parallel Downloader**: Pengunduhan segmen paralel dengan mekanisme *chunk retry* dan *resumable session*.
* **Local Muxing Engine**: Penggabungan audio dan video stream menjadi file `.mp4` standar yang siap diputar di galeri atau pemutar media eksternal.

### 2. Multi-Vault Incognito Mode
* **Multi-Password Partitioning**: Pengguna dapat mendefinisikan N password berbeda. Setiap password menghasilkan derivasi kunci unik yang membuka sesi (*vault*) spesifik.
* **Plausible Deniability**: Tidak ada daftar akun/vault yang terekspos. Jika pengguna dipaksa membuka browser, mereka cukup memasukkan password "vault dummy/decoy".
* **Total Storage Isolation**: Cookie, cache, IndexedDB, LocalStorage, dan riwayat download disimpan di partisi terpisah per vault.
* **Ephemeral Mode**: Mode pembersihan total saat sesi ditutup (*secure wiping* memory dan temporary cache).

---

## Struktur Repositori

```text
yourbrowser/
├── README.md               # Dokumentasi utama proyek
├── PRD.md                  # Product Requirements Document
├── app/                    # Entry point aplikasi & UI (Jetpack Compose / Material3)
├── core/
│   ├── browser/            # Abstraksi Browser Engine (GeckoView / WebView)
│   ├── crypto/             # Argon2id KDF, AES-256-GCM, SQLCipher helper
│   ├── network/            # OkHttp client, request sniffer, proxy config
│   └── common/             # Utilities, extensions, dispatchers
├── feature/
│   ├── downloader/         # Video sniffer, manifest parser, chunk downloader, FFmpeg muxer
│   ├── vault/              # Session switcher, vault isolation, password auth
│   └── tab-management/     # Tab manager, history, bookmark
└── gradle/                 # Build scripts & version catalog
```

---

## Panduan Build & Setup

### Prasyarat
* Android Studio Iguana / Ladybug atau versi yang lebih baru
* JDK 17
* Android SDK (API Level 34/35)
* NDK (jika mengompilasi custom C/C++ muxer)

### Langkah Kompilasi
```bash
# Build debug APK
./gradlew assembleDebug

# Jalankan Unit Tests
./gradlew testDebugUnitTest
```
