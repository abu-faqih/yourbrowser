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
│   │   ├── security.py                 # Manajemen kriptografi password tab & profil (SHA-256 + Salt)
│   │   ├── browser_data.py             # Pengelola persistensi Bookmarks, History, & Pengaturan
│   │   └── download_manager.py         # Pengelola antrean unduhan file Chromium
│   ├── ui/
│   │   ├── browser_window.py           # Jendela peramban utama (Tabs, Omnibox, Toolbar, WebViews)
│   │   ├── bookmarks_bar.py            # Quick-access toolbar bookmark di bawah Omnibox
│   │   ├── bookmarks_dialog.py         # Dialog pengelola Bookmark
│   │   ├── history_dialog.py           # Dialog riwayat penjelajahan & pembersih data
│   │   ├── downloads_dialog.py         # Dialog daftar unduhan file
│   │   ├── find_in_page.py             # Floating search bar cari teks di halaman (Ctrl+F)
│   │   ├── settings_dialog.py          # Dialog pengaturan mesin pencari & browser
│   │   ├── shields_panel.py            # Dropdown popup panel interaktif Brave Shields
│   │   └── lock_modal.py               # Dialog set password & overlay pengunci tab
│   └── resources/
│       ├── style.py                    # Tema Brave Obsidian Pro (QSS / CSS)
│       └── icons.py                    # Modul ikon vektor SVG resolusi tinggi
├── tests/
│   ├── test_security.py                # Unit test verifikasi enkripsi password tab & profil
│   ├── test_browser_integration.py     # Integration test UI, tabs, dan lock/unlock lifecycle
│   ├── test_browser_features.py        # Test Bookmarks, History, Downloads, Zoom, & Incognito
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
- Styling tampilan didefinisikan dalam `src/resources/style.py` dengan format CSS standar (*Qt Style Sheets*) bertema Brave Obsidian Dark.

### 2. Brave Shields & Pemblokir Iklan Agresif
- Tombol **🛡️ Shields** menampilkan jumlah iklan/pelacak yang berhasil diblokir secara langsung.
- Mengklik tombol Shields membuka panel dropdown interaktif untuk mengaktifkan (*Shields UP*) atau menonaktifkan (*Shields DOWN*) proteksi.
- Secara otomatis menetralkan jebakan `window.open` dan iklan klik (*popunder*) pada situs-situs film streaming.

### 3. Fitur Kunci Tab dengan Password (Tab Lock via Klik-Kanan & Toolbar)
- **Klik Kanan pada Tab Mana Saja**: Pilih **🔒 Lock Tab with Password...** untuk mengunci tab tertentu dengan password/PIN.
- Tab akan langsung terkunci dengan ikon gembok `🔒`, dan konten halaman web digantikan oleh layar enkripsi *Cyber Obsidian*.
- Masukkan password langsung di tab untuk membuka kembali kunci.

### 4. Bookmarks Bar & Bookmarks Manager
- Tombol bintang bintang di Omnibox (`Ctrl+D`): klik untuk bookmark/unbookmark halaman seketika (bintang menyala emas `#F59E0B`).
- **Bookmarks Bar**: Akses cepat situs favorit tepat di bawah Omnibox, dapat di-toggle via `Ctrl+Shift+B` atau menu.
- **Bookmarks Manager** (`Ctrl+Shift+O`): Dialog pencarian, pembukaan, dan penghapusan bookmark.

### 5. Riwayat Penjelajahan (Browsing History Manager)
- Riwayat penjelajahan tersimpan rapi secara lokal dan terurut waktu (`Ctrl+H`).
- Fitur pencarian real-time pada riwayat, pembukaan di tab baru, serta tombol pembersihan riwayat (*Clear All History*).

### 6. Pengelola Unduhan (Download Manager)
- Integrasi otomatis dengan request download berkas Chromium (`Ctrl+J`).
- Menampilkan nama file, persentase download, ukuran yang telah diunduh, status, tombol batalkan, buka file, dan buka folder unduhan.

### 7. Find in Page (Pencarian Teks di Halaman)
- Tekan `Ctrl+F` untuk memunculkan floating bar pencarian teks.
- Mendukung navigasi *Next match* (Enter), *Previous match* (Shift+Enter), dan tutup pencarian (Esc).

### 8. Kontrol Zoom & Tampilan
- Perbesar halaman (`Ctrl++` / `Ctrl+=`), perkecil (`Ctrl+-`), dan reset zoom ke 100% (`Ctrl+0`).
- Indikator badge zoom persentase di Omnibox jika zoom tidak 100%, klik badge untuk langsung reset ke 100%.
- Mode layar penuh / Fullscreen (`F11`).

### 9. Mode Privat / Incognito Window
- Buka jendela privat terpisah (`Ctrl+Shift+N`) dengan profil *off-the-record* memori terisolasi tanpa jejak riwayat atau cookies disk.
- Dilengkapi badge visual khusus `🕶️ Private Window`.

### 10. Pintasan Keyboard Standar (Keyboard Shortcuts)
| Shortcut | Aksi |
| :--- | :--- |
| `Ctrl+T` / `Ctrl+W` | Buka tab baru / Tutup tab aktif |
| `Ctrl+Shift+T` | Buka kembali tab yang baru ditutup (*Reopen closed tab*) |
| `Ctrl+N` / `Ctrl+Shift+N` | Jendela baru / Jendela privat (Incognito) baru |
| `Ctrl+R` / `F5` | Muat ulang halaman (*Reload*) |
| `Ctrl+L` / `Alt+D` | Sorot & fokus ke Omnibox |
| `Ctrl+D` / `Ctrl+Shift+B` | Bookmark tab ini / Tampilkan atau sembunyikan Bookmarks Bar |
| `Ctrl+H` / `Ctrl+J` / `Ctrl+Shift+O` | Riwayat / Unduhan / Manajer Bookmark |
| `Ctrl+F` | Cari teks di halaman (*Find in page*) |
| `Ctrl++` / `Ctrl+-` / `Ctrl+0` | Zoom in / Zoom out / Reset zoom |
| `Ctrl+1` s/d `Ctrl+9` | Berpindah ke tab 1 s/d tab terakhir |
| `Alt+Left` / `Alt+Right` | Mundur / Maju halaman |

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
