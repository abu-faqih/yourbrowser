---
name: Stealth Obsidian
colors:
  surface: '#0e131f'
  surface-dim: '#0e131f'
  surface-bright: '#343946'
  surface-container-lowest: '#080e1a'
  surface-container-low: '#161c28'
  surface-container: '#1a202c'
  surface-container-high: '#242a36'
  surface-container-highest: '#2f3542'
  on-surface: '#dde2f3'
  on-surface-variant: '#bcc9cd'
  inverse-surface: '#dde2f3'
  inverse-on-surface: '#2b303d'
  outline: '#869397'
  outline-variant: '#3d494c'
  surface-tint: '#4cd7f6'
  primary: '#4cd7f6'
  on-primary: '#003640'
  primary-container: '#06b6d4'
  on-primary-container: '#00424f'
  inverse-primary: '#00687a'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb3ad'
  on-tertiary: '#68000a'
  tertiary-container: '#ff817a'
  on-tertiary-container: '#7e000f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#acedff'
  primary-fixed-dim: '#4cd7f6'
  on-primary-fixed: '#001f26'
  on-primary-fixed-variant: '#004e5c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#0e131f'
  on-background: '#dde2f3'
  surface-variant: '#2f3542'
  surface-ground: '#030712'
  surface-card: '#0b0f19'
  surface-overlay: '#111827'
  surface-border: '#1f2937'
  accent-sniffer: '#06b6d4'
  accent-secure: '#10b981'
  accent-panic: '#ef4444'
  accent-warning: '#f59e0b'
  text-primary: '#f9fafb'
  text-secondary: '#9ca3af'
  text-disabled: '#4b5563'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 22px
  title-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

# DESIGN_SYSTEM.md — YourBrowser UI/UX Architecture & Specifications

Dokumentasi resmi standar desain UI/UX, token desain, prinsip interaksi, keamanan anti-forensik, dan wireframe ASCII untuk aplikasi **YourBrowser** (Android SDK 26–35).

## 1. Filosofi Desain & Prinsip Utama
1. **Plausible Deniability & Zero-Knowledge First**
2. **Stealth Obsidian Aesthetics (OLED Friendly)**: Latar belakang ultra-gelap (`#030712` & `#0B0F19`).
3. **Ergonomis Thumb Zone**: Semua kontrol navigasi krusial di Bottom Bar & Bottom Sheet.
4. **Sniffer Reaktif Tanpa Obstruksi Viewport**: Cyan Neon pulse badge (`#06B6D4`).

## 2. Palet Warna (Color System)
- `surface-ground`: `#030712` (Background layar utama)
- `surface-card`: `#0B0F19` (Surface kontainer, toolbar, bottom sheet)
- `surface-overlay`: `#111827` (Kartu, dialog modal)
- `surface-border`: `#1F2937` (Garis pemisah & border)
- `accent-sniffer`: `#06B6D4` (Cyan Neon — Streaming sniffer)
- `accent-secure`: `#10B981` (Emerald Green — SSL & status vault aman)
- `accent-panic`: `#EF4444` (Red Alert — Tombol Panic / Wipe Session)
- `accent-warning`: `#F59E0B` (Amber — Tracker blocker & warning)
- `text-primary`: `#F9FAFB`
- `text-secondary`: `#9CA3AF`
- `text-disabled`: `#4B5563`

## 3. Tipografi
- Font Family: Inter, system-ui, sans-serif
- Monospace Family: JetBrains Mono, Fira Code, monospace
