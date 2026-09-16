# YourBrowser: Modern Privacy Browser with Brave Shields & Tab Password Protection

## Ringkasan Proyek
**YourBrowser** adalah peramban web (*web browser*) native generasi baru dengan antarmuka **Brave Obsidian Dark**, ditenagai oleh mesin peramban Chromium modern (*QtWebEngine Core*). Seluruh kode sumber aplikasi berada di repositori ini dan dirancang untuk dapat dikustomisasi (*full customizable*) oleh pengembang secara fleksibel, clean, dan modular.

Browser ini memiliki dua fitur unggulan yang dirancang khusus:
1. **Brave Shields Native Panel & Aggressive Ad-Blocker**: Memblokir iklan, pelacak (*trackers*), dan skrip popunder secara instan di level peramban, dilengkapi tombol dropdown interaktif bertema Brave Lion dengan penghitung (*counter*) iklan yang diblokir secara *real-time*.
2. **Tab Password Protection (Lock Tab)**: Kemampuan mengunci (*lock*) tab individual mana pun dengan kata sandi/PIN. Ketika tab dikunci, konten web disembunyikan sepenuhnya oleh layar kunci terenkripsi (*Obsidian Lock Screen*), dan hanya dapat dibuka dengan memasukkan kata sandi yang valid.

---

## Arsitektur & Struktur Kode Sumber

Seluruh logika UI, manajemen tab, proteksi password, dan mesin peramban berada dalam folder `src/` sehingga Anda memiliki kontrol 100% untuk memodifikasi tampilan, menambahkan fitur profil, mengubah tema, maupun menyesuaikan perilaku web.

```text
yourbrowser/
├── bin/
│   └── yourbrowser                     # Executable launcher utama YourBrowser
├── src/
│   ├── app.py                          # Titik masuk utama aplikasi (Main Entry Point)
│   ├── core/
│   │   ├── adblock_engine.py           # Mesin penyaring request, anti-popup & anti-clickjacking
│   │   └── security.py                 # Manajemen kriptografi password tab & profil (SHA-256 + Salt)
│   ├── ui/
│   │   ├── browser_window.py           # Jendela peramban utama (Tabs, Omnibox, Toolbar, WebViews)
│   │   ├── shields_panel.py            # Dropdown popup panel interaktif Brave Shields
│   │   └── lock_modal.py               # Dialog set password & overlay pengunci tab
│   └── resources/
│       ├── style.py                    # Tema Brave Obsidian Pro (QSS / CSS)
│       └── icons.py                    # Modul ikon vektor SVG resolusi tinggi
├── tests/
│   ├── test_security.py                # Unit test verifikasi enkripsi password tab & profil
│   ├── test_browser_integration.py     # Integration test UI, tabs, dan lock/unlock lifecycle
│   └── test_stream_native.py           # Verifikasi pemutaran stream & pemblokiran popup di LK21
├── desktop/
│   └── yourbrowser.desktop             # Integrasi shortcut sistem desktop Linux
├── assets/
│   └── icons/                          # Ikon vektor resolusi tinggi YourBrowser
│       └── yourbrowser.svg
└── scripts/
    └── install_desktop.sh              # Skrip instalasi shortcut desktop ke sistem
```

---

## Fitur Utama

### 1. Kustomisasi Bebas & Kode Bersih (Full Extensibility)
- Seluruh komponen UI ditulis menggunakan arsitektur modular PyQt6 + Chromium Content Engine.
- Sangat mudah menambahkan tombol baru, menu konteks, sidebar, sistem vault multi-profil, atau ekstensi kustom langsung di folder `src/ui/`.
- Styling tampilan didefinisikan dalam `src/resources/style.py` dengan format CSS standar (*Qt Style Sheets*).

### 2. Fitur Kunci Tab dengan Password (Tab Lock)
- Klik tombol **🔒 Lock Tab** pada toolbar di sebelah address bar.
- Masukkan kata sandi atau PIN untuk tab yang sedang aktif.
- Tab akan langsung terkunci, judul tab diberi penanda `🔒`, dan konten halaman web digantikan oleh layar enkripsi modern.
- Konten web baru dapat dilihat kembali setelah kata sandi diverifikasi dengan benar.

### 3. Brave Shields & Pemblokir Iklan Agresif
- Tombol **🛡️ Shields** menampilkan jumlah iklan/pelacak yang berhasil diblokir secara langsung.
- Mengklik tombol Shields membuka panel dropdown interaktif untuk mengaktifkan (*Shields UP*) atau menonaktifkan (*Shields DOWN*) proteksi.
- Secara otomatis menetralkan jebakan `window.open` dan iklan klik (*popunder*) pada situs-situs film streaming.

---

## Panduan Penggunaan & Pengembangan

### 1. Menjalankan Peramban
```bash
# Meluncurkan YourBrowser langsung dari terminal
./bin/yourbrowser

# Atau membuka langsung URL spesifik
./bin/yourbrowser https://mamamas.xyz/this-party-dead-2026
```

### 2. Menginstal Shortcut ke Menu Desktop Linux
```bash
./scripts/install_desktop.sh
```
Aplikasi akan langsung muncul di menu aplikasi Linux Mint / Ubuntu Anda dengan nama **YourBrowser**.

### 3. Menjalankan Seluruh Pengujian (Test Suite)
```bash
# Menjalankan pengujian keamanan & integrasi browser
python3 -m unittest discover tests/

# Menjalankan verifikasi streaming video pada situs target (LK21)
python3 tests/test_stream_native.py
```
