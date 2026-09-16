# YourBrowser: Next-Gen Privacy Browser (Brave Engine Distribution)

## Ringkasan Proyek
**YourBrowser** adalah peramban web (*web browser*) multi-platform generasi baru berbasis arsitektur **Brave Browser (Chromium Core)**. Browser ini dirancang dengan fokus privasi tingkat tinggi, proteksi pelacak agresif (*Brave Shields*), serta netralisasi total terhadap popup, popunder, dan penipuan klik (*click-hijacking*) pada situs-situs streaming modern.

Proyek ini dirancang untuk multi-platform (**Linux**, **Windows**, dan **Android**), dengan fokus implementasi tahap pertama pada lingkungan **Linux**.

---

## Fitur Utama

1. **Brave Shields Native Integration**:
   - Pemblokiran iklan agresif (*aggressive adblocking*) dan pemfilteran kosmetik elemen manipulatif.
   - Proteksi sidik jari peramban (*strict fingerprinting protection*).
   - Pemblokiran pelacak lintas-situs (*cross-site tracker blocking*).

2. **YourBrowser Shield Booster (Anti-Popunder & Anti-Clickjacking)**:
   - Injeksi otomatis di tingkat kernel peramban (*Manifest V3 Content Script & Service Worker*).
   - Menetralkan jebakan `window.open`, *invisible banner overlays*, dan manipulasi event `click`/`mousedown` pada situs streaming.
   - Pembersihan otomatis (*auto-purge*) terhadap iframe jaringan iklan liar.
   - Deteksi dan penutupan instan tab popunder liar dari situs streaming.

3. **Seamless Media Streaming**:
   - Menjamin video streaming (HLS, DASH, Direct MP4 via Cloud Storage) dapat langsung diputar dengan suara (*unmuted* & audio jernih) tanpa tertahan oleh dialog atau popunder iklan.
   - Teruji dan terverifikasi secara sempurna pada situs streaming agresif: `https://mamamas.xyz/this-party-dead-2026`.

4. **Isolasi Data Profil Pengguna**:
   - Menyimpan seluruh cache, riwayat, cookie, dan preferensi terpisah pada folder terdedikasi `~/.config/yourbrowser`.

---

## Struktur Repositori

```text
yourbrowser/
├── README.md                           # Dokumentasi peramban & panduan
├── PRD.md                              # Product Requirements Document
├── DESIGN_SYSTEM.md                    # Panduan visual dan design tokens
├── bin/
│   └── yourbrowser                     # Executable launcher utama YourBrowser
├── config/
│   └── policies.json                   # Kebijakan peramban terkelola (Anti-Popup, Anti-Metrics)
├── extensions/
│   └── shield-booster/                 # Ekstensi internal Shield Booster (Anti-popunder & clickjacking)
│       ├── manifest.json
│       ├── content.js                  # Main world interception
│       ├── isolated_content.js         # Isolated world DOM cleaner
│       └── background.js               # Service worker tab governor
├── desktop/
│   └── yourbrowser.desktop             # Integrasi desktop Linux (FreeDesktop standard)
├── assets/
│   └── icons/                          # Aset visual & logo vektor YourBrowser
│       └── yourbrowser.svg
└── scripts/
    ├── install_desktop.sh              # Skrip instalasi shortcut desktop ke sistem
    └── verify_stream.py                # Otomasi pengujian streaming & audit anti-popup
```

---

## Panduan Menjalankan (Linux)

### 1. Menjalankan Langsung via Terminal
```bash
# Meluncurkan browser dengan profil default YourBrowser
./bin/yourbrowser

# Membuka langsung URL spesifik
./bin/yourbrowser https://mamamas.xyz/this-party-dead-2026

# Mode Incognito / Private
./bin/yourbrowser --incognito
```

### 2. Memasang ke Menu Aplikasi Desktop Linux
```bash
./scripts/install_desktop.sh
```
Setelah dijalankan, aplikasi akan terdaftar di menu sistem Anda (misal Linux Mint Menu / GNOME / KDE) dengan nama **YourBrowser**.

### 3. Otomasi Pengujian Streaming & Anti-Popup
Untuk memverifikasi bahwa browser memutar video streaming tanpa ada satupun popup iklan:
```bash
python3 ./scripts/verify_stream.py
```
Skrip ini akan memvalidasi secara otomatis:
- Pemutaran stream berjalan lancar (`currentTime` bertambah).
- Durasi media terdeteksi (~98 menit).
- Audio bersuara aktif (`muted: false`, `volume: 1`).
- Jumlah tab/window popup iklan yang terbuka adalah **0** (bersih total).

---

## Roadmap Multi-Platform

* **Tahap 1 (Selesai)**: Linux Desktop (Mint/Ubuntu/Debian) - Distribusi Brave Engine mandiri, Shield Booster, integrasi desktop, dan verifikasi streaming sempurna.
* **Tahap 2**: Windows Desktop - Pengemasan executable wrapper (`yourbrowser.exe`), installer InnoSetup/MSI, dan integrasi Registry browser default.
* **Tahap 3**: Android Mobile - Arsitektur Brave-core / GeckoView Android wrapper dengan porting modul Shield Booster ke WebView / WebExtension API mobile.
