# YourBrowser Design System: Unified UI/UX Specification & Token Blueprint
*Versi: 2.0.0 | Status: Production Standard | Platform: Desktop Linux / PyQt6 Chromium Engine*

---

## 1. Filosofi Desain & Karakter Visual

**YourBrowser Design System** dibangun di atas fondasi: **Modern, Professional, Cohesive, and Visually Tactile**.

* **Obsidian Precision (Dark Mode First)**: Menggunakan kedalaman visual bertingkat (*tiered elevation surfaces*) dari Deep Obsidian Canvas (`#0B0E14`), Surface Cards (`#121622` ke `#181D2C`), hingga High-Contrast Primary Text (`#F8FAFC`).
* **Fluid Pill & Smooth Rounded Shapes**: Elemen interaktif utama (Omnibox, Action Buttons, Badges, Tabs, Dialog Container) mengusung bentuk **pill / capsule** (`border-radius: 9999px` atau `14-18px`) dan **smooth rounded corners** (`12-16px`) untuk memberikan nuansa antarmuka modern setara macOS / ChromeOS Next-Gen.
* **Vibrant Functional Gradients**: Gradasi warna yang kaya dan terkalibrasi digunakan secara fungsional untuk mengarahkan atensi pengguna:
  * **Brave Flame Gradient** (`#FF5500` → `#FF2A54`): Aksi utama, aktivasi perlindungan privasi (Shields), dan bookmarking.
  * **Cyber Cyan Gradient** (`#06B6D4` → `#3B82F6`): Keamanan, enkripsi vault, dan dialog autentikasi tab.
  * **Emerald Glow Gradient** (`#10B981` → `#059669`): Koneksi SSL aman dan unduhan selesai.
  * **Obsidian Glass Depth** (`#161B28` → `#10141F`): Permukaan kartu dan dialog popover.
* **Single Source of Truth**: Semua token warna, gradasi, radius, typografi, dan style generator diatur terpusat di `src/resources/design_system.py` dan dikonsumsi oleh `src/resources/style.py` serta seluruh modul UI.

---

## 2. Fondasi Token Desain (Design Tokens)

### 2.1 Palet Warna & Semantic Mapping (`Colors`)

| Token | Hex Value | Peruntukan Fungsional |
| :--- | :--- | :--- |
| `BG_CANVAS` | `#0B0E14` | Kanvas jendela utama dan window backdrop |
| `BG_BASE` | `#0E121A` | Latar Omnibox, search input, dan counter box |
| `SURFACE_1` | `#121622` | Surface kartu profil, list items, dan tab non-aktif |
| `SURFACE_2` | `#181D2C` | Surface elevated, hover state tombol sekunder |
| `SURFACE_3` | `#22293D` | Active selection, input fokus, dan pill badge bg |
| `SURFACE_OVERLAY` | `#161B26` | Context menu dan floating popover modal |
| `BORDER_SUBTLE` | `#1C2333` | Garis pembatas tab strip dan divider halus |
| `BORDER_DEFAULT`| `#263045` | Garis tepi komponen default (kartu, input, tombol) |
| `BORDER_HOVER` | `#3A4765` | Garis tepi saat pointer mouse melayang (*hover*) |
| `BORDER_ACTIVE` | `#FF5500` | Aksen garis aktif atau seleksi fokus |
| `TEXT_PRIMARY` | `#F8FAFC` | Judul, URL aktif, teks input (kontras tinggi 15:1) |
| `TEXT_SECONDARY`| `#94A3B8` | Deskripsi, URL path, subjudul |
| `TEXT_MUTED` | `#64748B` | Shortcut hint, placeholder, ikon non-aktif |
| `STATUS_SUCCESS`| `#10B981` | Indikator HTTPS SSL dan download selesai |
| `STATUS_WARNING`| `#F59E0B` | Bintang bookmark aktif |
| `STATUS_DANGER` | `#EF4444` | Hapus profil, pembatalan unduhan, tab terkunci |

---

### 2.2 Token Gradasi Linear (`Gradients`)

| Token Name | Formula Gradasi QSS | Kegunaan |
| :--- | :--- | :--- |
| `PRIMARY_FLAME` | `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5500, stop:1 #FF2A54)` | Tombol aksi primer, Shields UP, New Profile |
| `PRIMARY_FLAME_HOVER` | `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6A1F, stop:1 #FF4267)` | Hover state tombol primer |
| `CYBER_CYAN` | `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #3B82F6)` | Tombol keamanan & proteksi password tab |
| `CYBER_CYAN_HOVER` | `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22D3EE, stop:1 #60A5FA)` | Hover state cyber security |
| `EMERALD_GLOW` | `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669)` | Indikator status aman / SSL verified |
| `PURPLE_STEALTH` | `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #6366F1)` | Badge mode Incognito / Private Window |
| `DANGER_CRIMSON` | `qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626)` | Tombol delete / wipe tab session |
| `SURFACE_CARD` | `qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161B28, stop:1 #10141F)` | Latar belakang bertekstur kartu profil |
| `SURFACE_DIALOG` | `qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #141824, stop:1 #0C0F17)` | Latar belakang dialog & modal popover |

---

### 2.3 Skala Geometri & Corner Radii (`Radii`)

| Token | Ukuran | Komponen Sasaran |
| :--- | :--- | :--- |
| `XS` | `4px` | Scrollbar thumb handle, separator |
| `SM` | `8px` | Menu items, list widget item, sub-controls |
| `MD` | `12px` | Group box, search input standard, find bar |
| `LG` | `16px` | Kartu profil, dialog container, popup popovers |
| `XL` | `20px` | Overlay card autentikasi sesi enkripsi |
| `PILL` | `9999px` | Capsule Omnibox, Primary Action Buttons, Pill Badges |

---

## 3. Komponen Utama & Pola Penggunaan

### 3.1 Capsule Omnibox Frame
```css
#omnibox_capsule {
    background-color: #0E121A;
    border: 1px solid #263045;
    border-radius: 19px;
    min-height: 38px;
    max-height: 38px;
    padding-left: 14px;
    padding-right: 12px;
}
```

### 3.2 Pill Action Button (Primary Flame Gradient)
```python
from src.resources.design_system import pill_button_primary

btn = QPushButton("+ New Profile")
btn.setStyleSheet(pill_button_primary(height=38, font_size="13px"))
```

### 3.3 Status Badges (Pill Tags)
```python
from src.resources.design_system import pill_badge, Colors

badge = QLabel("🔒 Locked")
badge.setStyleSheet(pill_badge(Colors.STATUS_DANGER_BG, "#FCA5A5", "10.5px"))
```

### 3.4 Sleek Inputs
```python
from src.resources.design_system import rounded_input, Radii

input_field = QLineEdit()
input_field.setStyleSheet(rounded_input(height=38, radius=Radii.SM))
```

---

## 4. Struktur Modul Desain

```text
src/
└── resources/
    ├── design_system.py   # Single source of truth untuk tokens & QSS helpers
    ├── style.py           # Global BRAVE_THEME_QSS dibangun dari tokens
    └── icons.py           # Vector SVG icons generator
```
