# YourBrowser: Modern Privacy Browser with Brave Shields, Isolated Profiles & Password Vault

## Ringkasan Proyek
**YourBrowser** adalah peramban web (*web browser*) native generasi baru dengan antarmuka **Brave Obsidian Dark**, ditenagai oleh mesin peramban Chromium modern (*QtWebEngine Core*). Seluruh kode sumber aplikasi berada di repositori ini dan dirancang untuk dapat dikustomisasi (*full customizable*) oleh pengembang secara fleksibel, clean, dan modular.

Browser ini memiliki fitur-fitur unggulan yang dirancang khusus:
1. **Multi-Profile Isolation & Dashboard**: Setiap profil pengguna sepenuhnya terisolasi (cookies, storage, history, bookmark, dan pengaturan terpisah). Saat aplikasi dibuka, user disambut oleh **Dashboard** manajemen profil dengan alur onboarding otomatis jika belum ada profil.
2. **Profile Password Protection & Hidden Profiles (Ctrl+H)**: Setiap profil dapat dilindungi secara kriptografis menggunakan kata sandi/PIN (SHA-256 + Salt). Profil juga dapat disembunyikan (*stealth mode*) dan ditampilkan/disembunyikan kembali seketika dengan menekan shortcut `Ctrl+H` di Dashboard.
3. **Tab Session Persistence**: Seluruh tab yang sedang dibuka dalam profil disimpan secara otomatis saat browser ditutup atau saat kembali ke Dashboard, dan langsung dimuat kembali saat profil tersebut dibuka lagi.
4. **Brave Shields Native Panel & Aggressive Ad-Blocker**: Memblokir iklan, pelacak (*trackers*), dan skrip popunder secara instan di level peramban, dilengkapi tombol dropdown interaktif bertema Brave Lion dengan penghitung (*counter*) iklan yang diblokir secara *real-time*.
5. **Tab Password Protection (Lock Tab via Context Menu)**: Kemampuan mengunci (*lock*) tab individual mana pun dengan kata sandi/PIN melalui klik kanan pada tab. Tombol pada toolbar navigasi telah diselaraskan menjadi tombol **🏠 Dashboard** untuk perpindahan profil instan.

---

## Arsitektur & Struktur Kode Sumber

Seluruh logika UI, manajemen profil, persistensi sesi, proteksi password, dan mesin peramban berada dalam folder `src/` dengan arsitektur modular yang rapi:

```text
yourbrowser/
├── bin/
│   └── yourbrowser                     # Executable launcher utama YourBrowser
├── src/
│   ├── app.py                          # Titik masuk utama aplikasi (Main Entry Point)
│   ├── core/
│   │   ├── profile_manager.py          # Pengelola profil terisolasi, sandi, hidden state, & tab sesi
│   │   ├── adblock_engine.py           # Mesin penyaring request, anti-popup & anti-clickjacking
│   │   ├── security.py                 # Manajemen kriptografi password tab & profil (SHA-256 + Salt)
│   │   ├── browser_data.py             # Pengelola persistensi Bookmarks, History, & Pengaturan
│   │   └── download_manager.py         # Pengelola antrean unduhan file Chromium
│   ├── ui/
│   │   ├── dashboard_window.py         # Jendela Dashboard utama (Profile Picker, Onboarding, Vault Auth)
│   │   ├── browser_window.py           # Jendela peramban utama (Tabs, Omnibox, Toolbar, WebViews)
│   │   ├── bookmarks_bar.py            # Quick-access toolbar bookmark di bawah Omnibox
│   │   ├── bookmarks_dialog.py         # Dialog pengelola Bookmark
│   │   ├── history_dialog.py           # Dialog riwayat penjelajahan & pembersih data
│   │   ├── downloads_dialog.py         # Dialog daftar unduhan file
│   │   ├── find_in_page.py             # Floating search bar cari teks di halaman (Ctrl+F)
│   │   ├── settings_dialog.py          # Dialog pengaturan mesin pencari & browser
│   │   ├── shields_panel.py            # Dropdown popup panel interaktif Brave Shields
│   │   ├── window_controls.py          # Kontrol jendela frameless modern (Min, Max, Close & Draggable header)
│   │   └── lock_modal.py               # Dialog set password & overlay pengunci tab
│   └── resources/
│       ├── design_system.py            # Modul Design System tokens (Colors, Gradients, Radii, Typography)
│       ├── style.py                    # Tema Brave Obsidian Pro (QSS / CSS) berbasis design system
│       └── icons.py                    # Modul ikon vektor SVG resolusi tinggi
├── tests/
│   ├── test_design_system.py           # Unit test token visual, pill helpers, & gradasi design system
│   ├── test_profile_manager.py         # Unit test CRUD profil, direktori isolasi, & persistensi sesi tab
│   ├── test_dashboard_integration.py   # Integration test Dashboard, Ctrl+H toggle, password auth
│   ├── test_security.py                # Unit test verifikasi enkripsi password tab & profil
│   ├── test_browser_integration.py     # Integration test UI, tabs, dan lock/unlock lifecycle
│   ├── test_browser_features.py        # Test Bookmarks, History, Downloads, Zoom, & Incognito
│   └── test_stream_native.py           # Verifikasi pemutaran stream & pemblokiran popup di LK21
├── desktop/
│   └── yourbrowser.desktop             # Integrasi shortcut sistem desktop Linux
├── assets/
│   └── icons/                          # Ikon vektor resolusi tinggi & PNG multi-resolusi YourBrowser
│       ├── yourbrowser.svg
│       ├── yourbrowser.png
│       └── [16x16 ... 512x512]/
└── scripts/
    └── install_desktop.sh              # Skrip instalasi shortcut desktop & cache ikon ke sistem
```

---

## Fitur Utama

### 1. Dashboard Profil & Alur Onboarding Perdana
- Saat pertama kali membuka peramban, aplikasi menampilkan layar **Dashboard** bergaya Brave Obsidian Dark.
- Jika belum ada profil yang dibuat, sistem otomatis menyajikan alur onboarding interaktif untuk membuat profil pertama Anda.
- Setiap kartu profil menampilkan inisial avatar berwarna, nama akun, serta tombol aksi dengan estetika minimalis dan bersih tanpa badge status yang merusak stealth mode.

### 2. Isolasi Penuh Antar Profil (Session & Data Isolation)
- Setiap profil memiliki direktori terpisah di `~/.config/yourbrowser/profiles/<profile_id>/`.
- Cookies, cache, LocalStorage, IndexedDB, riwayat penjelajahan (`history.json`), bookmarks (`bookmarks.json`), serta preferensi (`settings.json`) terisolasi 100% dan tidak bercampur dengan profil lain.

### 3. Proteksi Password Profil & Mode Profil Tersembunyi (Ctrl+H Stealth)
- Profil dapat dikunci dengan kata sandi saat dibuat atau diedit. Pembukaan profil terkunci memerlukan verifikasi kata sandi sebelum browser dibuka.
- Profil dapat ditandai sebagai *Hidden* (tersembunyi).
- **Murni Stealth (Tanpa Petunjuk/Tombol/Badge UI)**: Tidak ada petunjuk teks, tombol, maupun badge pada kartu profil yang membocorkan keberadaan atau status profil tersembunyi.
- Secara *default*, profil tersembunyi tidak pernah muncul di Dashboard saat aplikasi dibuka atau saat kembali dari jendela browser.
- Pada Dashboard, tekan tombol pintasan **`Ctrl+H`** untuk menampilkan (*reveal*) atau menyembunyikan (*hide*) profil-profil rahasia tersebut secara instan.

### 4. Persistensi Sesi Tab Otomatis (Tab Session Persistence)
- Seluruh tab yang sedang aktif di dalam profil tidak akan hilang ketika jendela browser ditutup atau ketika Anda kembali ke Dashboard.
- Saat profil dibuka kembali dari Dashboard di masa mendatang, seluruh tab yang tersimpan akan langsung dimuat ulang ke posisi tab terakhir.

### 5. Tombol Dashboard & Shields Seragam (Pill Rounded Corner)
- Tombol **Shields** dan **Dashboard** pada toolbar navigasi memiliki ukuran tinggi (32px), padding (0 14px), font, serta *rounded corners* (border-radius 16px) yang sepenuhnya seragam dan simetris.
- Menekan tombol Dashboard akan menyimpan sesi tab profil saat ini dan mengembalikan pengguna ke tampilan Dashboard manajemen profil.
- Proteksi kunci tab individual tetap dapat diakses dengan mudah via klik kanan pada tab (Tab Context Menu).

### 6. Brave Shields & Pemblokir Iklan Agresif
- Tombol **Shields** menampilkan jumlah iklan/pelacak yang berhasil diblokir secara langsung.
- Mengklik tombol Shields membuka panel dropdown interaktif untuk mengaktifkan (*Shields UP*) atau menonaktifkan (*Shields DOWN*) proteksi.
- Secara otomatis menetralkan jebakan `window.open` dan iklan klik (*popunder*) pada situs-situs film streaming.

### 7. Bookmarks Bar & Bookmarks Manager
- Tombol bintang di Omnibox (`Ctrl+D`): klik untuk bookmark/unbookmark halaman seketika (bintang menyala emas `#F59E0B`).
- **Bookmarks Bar**: Akses cepat situs favorit tepat di bawah Omnibox, dapat di-toggle via `Ctrl+Shift+B` atau menu.
- **Bookmarks Manager** (`Ctrl+Shift+O`): Dialog pencarian, pembukaan, dan penghapusan bookmark.

### 8. Riwayat Penjelajahan (Browsing History Manager)
- Riwayat penjelajahan tersimpan rapi secara lokal di dalam profil dan terurut waktu (`Ctrl+H` pada jendela browser).
- Fitur pencarian real-time pada riwayat, pembukaan di tab baru, serta tombol pembersihan riwayat (*Clear All History*).

### 9. Pengelola Unduhan (Download Manager)
- Integrasi otomatis dengan request download berkas Chromium (`Ctrl+J`).
- Menampilkan nama file, persentase download, ukuran yang telah diunduh, status, tombol batalkan, buka file, dan buka folder unduhan.

### 10. Mode Privat / Incognito Window
- Buka jendela privat terpisah (`Ctrl+Shift+N`) dengan profil *off-the-record* memori terisolasi tanpa jejak riwayat atau cookies disk.
- Dilengkapi badge visual khusus `Private Window` dengan ikon vektor kacamata penyamaran.

### 11. Unified Design System & Fluid Visual Tokens
- Arsitektur desain konsisten, modern, dan profesional berbasis token (`Colors`, `Gradients`, `Radii`, `Typography`) di `src/resources/design_system.py`.
- Seluruh ikon antarmuka menggunakan **100% SVG Vector Graphics** resolusi tinggi (`src/resources/icons.py`) sehingga tajam di semua DPI layar Linux dan bebas dari distorsi font emoji Unicode.
- Mengusung bentuk **pill / capsule** (`border-radius: 9999px` / `14-18px`) pada Omnibox, tombol aksi utama, dan badge status.
- Dilengkapi gradasi linear dinamis (*Brave Flame Gradient*, *Cyber Cyan Gradient*, *Emerald Glow*, dan *Deep Obsidian Surface Depth*).
- Dokumentasi lengkap tersedia pada [`DESIGN_SYSTEM.md`](file:///mnt/storage/aplikasi/yourbrowser/DESIGN_SYSTEM.md).

### 12. Brave Settings Hub & Kustomisasi Real-Time (`Ctrl+,`)
- Antarmuka pengaturan komprehensif dua panel bergaya Brave Browser dengan sidebar navigasi kategori berikon vektor SVG:
  1. **Shields & Privacy**: Pengaturan agresivitas pemblokir iklan & pelacak (*Aggressive / Standard / Off*), proteksi anti-fingerprinting (Canvas & AudioContext noise), pemblokir pelacak media sosial (Facebook, X, TikTok), opsi upgrade ke HTTPS (*Force HTTPS*), anti-popup, dan kebijakan cookie terisolasi.
  2. **Appearance**: Kustomisasi tema seketika (*Brave Obsidian Dark*, *Cyber Cyan Dark*, *Midnight OLED*, dan *Crisp Light*) serta pemilihan warna aksen (*Brave Flame Orange*, *Cyber Cyan*, *Emerald Glow*, dan *Electric Purple*), toggle tombol Home, tombol Shields, dan Bookmarks Bar.
  3. **Search Engines**: Pemilihan mesin pencari bawaan (*Brave Search*, *DuckDuckGo*, *Google*, *Bing*, *Ecosia*, *Qwant*).
  4. **Extensions**: Panel kelola ekstensi terpasang dan instalasi unpacked extension.
  5. **Clear Data**: Pembersihan selektif riwayat, cache, cookies, dan tab sesi.

### 13. Dukungan Ekstensi Chromium (Manifest V2 & V3) (`Ctrl+Shift+E`)
- Engine loader ekstensi native (`src/core/extension_manager.py`) yang mem-parse `manifest.json` dan menginjeksi `content_scripts` ke profil Chromium secara terisolasi (`MainWorld` / `ApplicationWorld`).
- Dilengkapi ekstensi bawaan **`YourBrowser Shield Booster`** (`extensions/shield-booster`) untuk netralisasi popup dan click-hijacking.
- Mendukung pemasangan ekstensi baru secara langsung dari direktori (*Load Unpacked Extension...*) dan toggle aktivasi per ekstensi.

### 14. Integrasi Native Tema GTK Linux (Cinnamon / GNOME / XFCE)
- Aplikasi secara otomatis mengintegrasikan tema sistem GTK3 (`QT_QPA_PLATFORMTHEME=gtk3`) di lingkungan Linux.
- Dialog sistem native (buka berkas, pilih folder download, simpan halaman) serta scrollbar dan window frame beradaptasi selaras dengan desktop environment pengguna.

### 15. Tampilan Jendela Modern Frameless (Client-Side Decoration / CSD)
- Title bar jadul bawaan OS dihilangkan secara default; deretan tab dinaikkan ke tepi paling atas jendela seperti browser modern (Google Chrome, Brave, Edge).
- Menghemat ruang vertikal 30–40 px dan memperluas area pandang penjelajahan web.
- Dilengkapi **Custom Window Controls** (Minimize `—`, Maximize/Restore `□`/`❐`, Close `✕`) di pojok kanan atas tab bar dengan efek hover modern (hover merah pada tombol close).
- Mendukung *Native Window Dragging & Snapping* serta *Edge Resizing* via API Qt 6 (`startSystemMove()` dan `startSystemResize()`).
- Opsi switchable: Pengguna yang tetap menginginkan title bar sistem bawaan OS dapat mengaktifkannya melalui menu **Settings (`Ctrl+,`) > Appearance > "Use native system title bar and window borders"**.

### 16. Pintasan Keyboard Standar (Keyboard Shortcuts)
| Shortcut | Konteks | Aksi |
| :--- | :--- | :--- |
| `Ctrl+H` | Dashboard | Sembunyikan / Tampilkan profil rahasia (*Toggle Hidden Profiles*) |
| `Ctrl+H` | Browser | Buka Pengelola Riwayat Penjelajahan (*Browsing History*) |
| `Ctrl+,` | Browser | Buka Panel Pengaturan Brave (*Settings Hub*) |
| `Ctrl+Shift+E` | Browser | Buka Manajer Ekstensi (*Extensions Manager*) |
| `Ctrl+T` / `Ctrl+W` | Browser | Buka tab baru / Tutup tab aktif |
| `Ctrl+Shift+T` | Browser | Buka kembali tab yang baru ditutup (*Reopen closed tab*) |
| `Ctrl+N` / `Ctrl+Shift+N` | Browser | Jendela baru / Jendela privat (Incognito) baru |
| `Ctrl+R` / `F5` | Browser | Muat ulang halaman (*Reload*) |
| `Ctrl+L` / `Alt+D` | Browser | Sorot & fokus ke Omnibox |
| `Ctrl+D` / `Ctrl+Shift+B` | Browser | Bookmark tab ini / Tampilkan atau sembunyikan Bookmarks Bar |
| `Ctrl+J` / `Ctrl+Shift+O` | Browser | Unduhan / Manajer Bookmark |
| `Ctrl+F` | Browser | Cari teks di halaman (*Find in page*) |
| `Ctrl++` / `Ctrl+-` / `Ctrl+0` | Browser | Zoom in / Zoom out / Reset zoom |
| `Ctrl+1` s/d `Ctrl+9` | Browser | Berpindah ke tab 1 s/d tab terakhir |
| `Alt+Left` / `Alt+Right` | Browser | Mundur / Maju halaman |

---

## Panduan Penggunaan & Pengembangan

### 1. Menjalankan Peramban
```bash
# Meluncurkan Dashboard YourBrowser langsung dari terminal mana saja (karena telah terinstal di ~/.local/bin)
yourbrowser

# Atau via path direktori proyek
./bin/yourbrowser

# Atau membuka langsung URL spesifik
yourbrowser https://search.brave.com
```

### 2. Menginstal Shortcut ke Menu Desktop Linux & Terminal PATH
```bash
./scripts/install_desktop.sh
```
Perintah di atas secara otomatis:
- Memasang shortcut `.desktop` ke `~/.local/share/applications/yourbrowser.desktop`.
- Memasang seluruh variasi ukuran ikon aplikasi (SVG & PNG 16x16 s/d 512x512) ke `~/.local/share/icons/hicolor/`.
- Memasang symlink binary ke `~/.local/bin/yourbrowser` agar dapat dipanggil langsung dari terminal mana pun.
Aplikasi akan langsung muncul di menu aplikasi Linux Mint / Cinnamon / Ubuntu Anda dengan nama **YourBrowser** dan logo lengkap.

### 3. Menjalankan Seluruh Pengujian (Test Suite)
```bash
# Menjalankan seluruh pengujian unit & integrasi profil/browser
python3 -m unittest discover tests/

# Menjalankan verifikasi streaming video pada situs target (LK21)
python3 tests/test_stream_native.py
```

### 4. Membangun & Menjalankan Portable AppImage (v1.0.0)
Aplikasi mendukung mode portabel murni. Seluruh profil, bookmark, riwayat, sesi tab, dan cache akan disimpan secara otomatis di folder `yourbrowser_data/` yang berada tepat di samping berkas `.AppImage` (atau di `<nama>.AppImage.home/`). Anda dapat memindahkan file AppImage beserta foldernya ke flashdisk atau komputer lain tanpa kehilangan data sedikitpun!

```bash
# Membangun file Standalone Portable AppImage ke folder dist/ (default: kompresi gzip cepat multi-core)
./scripts/build_appimage.sh

# Opsi parameter tambahan:
# --clean : Memaksa compile ulang bundel PyInstaller secara penuh dari awal
# --xz    : Menggunakan kompresi XZ maksimal (ukuran berkas lebih hemat, waktu kompresi lebih lama)
./scripts/build_appimage.sh --clean

# Menjalankan Portable AppImage
./dist/YourBrowser-1.0.0-x86_64.AppImage
```

---

## YourBrowser for Android (v1.0.0)

YourBrowser for Android adalah aplikasi peramban mobile native berperforma tinggi dengan tema **Brave Obsidian Dark**, didesain untuk kenyamanan penjelajahan privat dan bebas iklan di semua perangkat Android.

### Fitur Utama Android
1. **Brave Shields Native Blocker**: Memblokir iklan, trackers, skrip penambang, dan jebakan popup streaming langsung pada request interceptor.
2. **Omnibox Capsule**: Kolom pencarian membulat penuh dengan indikator status SSL & Bookmark cepat.
3. **Multi-Tab Manager**: Pengalih tab sheet responsif dengan counter tab real-time.
4. **Proteksi Sesi & Vault Tab**: Mengunci tab rahasia dengan PIN / kata sandi kriptografis SHA-256.
5. **Universal Device Support**: Mendukung Android 7.0 (Nougat, API 24) hingga Android 14/15 (API 34/35) dengan jangkauan 99.9%+ perangkat global.

### Menjalankan Pengujian & Membangun Signed APK
```bash
# 1. Menjalankan Unit Test Android
./gradlew test

# 2. Membangun Release APK yang telah ditandatangani secara digital (Signed APK)
./gradlew assembleRelease

# File APK rilis siap pasang berada di:
# dist/YourBrowser-1.0.0-android.apk

# 3. Verifikasi Tanda Tangan Digital APK (v2 & v3 Signature Scheme)
$ANDROID_HOME/build-tools/34.0.0/apksigner verify --verbose dist/YourBrowser-1.0.0-android.apk

# 4. Memasang APK ke Perangkat Android via ADB
adb install -r dist/YourBrowser-1.0.0-android.apk
```


