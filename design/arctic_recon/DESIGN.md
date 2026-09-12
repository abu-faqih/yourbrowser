---
name: Arctic Recon
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#3f4850'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#707881'
  outline-variant: '#bfc7d2'
  surface-tint: '#006398'
  primary: '#006194'
  on-primary: '#ffffff'
  primary-container: '#007bb9'
  on-primary-container: '#fdfcff'
  inverse-primary: '#93ccff'
  secondary: '#006c4a'
  on-secondary: '#ffffff'
  secondary-container: '#82f5c1'
  on-secondary-container: '#00714e'
  tertiary: '#bb0112'
  on-tertiary: '#ffffff'
  tertiary-container: '#e02928'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cce5ff'
  primary-fixed-dim: '#93ccff'
  on-primary-fixed: '#001d31'
  on-primary-fixed-variant: '#004b73'
  secondary-fixed: '#85f8c4'
  secondary-fixed-dim: '#68dba9'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#ffdad6'
  tertiary-fixed-dim: '#ffb4ab'
  on-tertiary-fixed: '#410002'
  on-tertiary-fixed-variant: '#93000b'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.005em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
  code-stream:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2rem
  space-xxs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
  space-2xl: 2rem
---

## Brand & Style

This design system delivers an austere, ultra-crisp daylight operations console for zero-knowledge browsing, parallel network telemetry, and forensic media sniffing. Departing from tired dark-mode cyberpunk clichés, it approaches cybersecurity through an "Arctic Recon" visual philosophy: surgical precision, absolute optical clarity, and high-visibility contrast engineered for daylight and bright ambient operational conditions.

The visual style combines **Technical Precision Minimalism** with structured data-dense utilities:
- **Optical Precision:** Razor-sharp outlines, low-diffusion ambient containment, and strict geometric alignment replace decorative blur and heavy glow effects.
- **Controlled Density:** High information throughput designed for forensic inspection, protocol verification, and concurrent network stream monitoring without interface clutter.
- **Operational Clarity:** Clear visual distinctions between non-volatile state containers, sandboxed memory spaces, encrypted vaults, and destructive panic triggers.
- **Tactical Utility:** Instant visual feedback for parallel sniffers, thread status, cryptographic hashes, and active packet streams.

## Colors

The palette employs an arctic light hierarchy built on structural slate neutrals, tactical state accents, and zero-compromise contrast ratios satisfying WCAG AAA standards across all functional levels.

### Surface Architecture
- **Canvas Base (`#F8FAFC`):** Slate-50 acts as the uncompromised outer canvas, reducing screen glare while maintaining daylight legibility.
- **Card & Workspace Containers (`#FFFFFF`):** High-purity white surfaces anchor sandboxed panels, media sniffer queues, and inspector tables.
- **Muted Sub-surfaces (`#F1F5F9`):** Slate-100 distinguishes nested process cards, raw payload inspectors, and secondary telemetry rails.

### Structural Lines
- **Hairline Dividers (`#E2E8F0`):** Slate-200 provides 1px structural separation between grid elements and list entries.
- **Active Structural Borders (`#CBD5E1`):** Slate-300 emphasizes interactive container boundaries, input surfaces, and data partitions.
- **Focused Perimeter (`#0284C7`):** Primary cyan accent for active sniffer captures and focused input nodes.

### Forensic & Security Accents
- **Primary / Sniffer Signal (`#0284C7`):** Ocean cyan-600 commands active media stream detection, stream download buffers, and network requests.
- **Secondary / Encrypted Safe State (`#059669`):** Emerald-600 validates verified SSL/TLS handshakes, zero-trace sandboxes, hardware token bindings, and encrypted storage vaults.
- **Tertiary / Panic & Kill-Switch (`#DC2626`):** Red-600 enforces zeroization routines, memory wipe protocols, active threat locks, and immediate session termination triggers.
- **Advisory / Warning (`#D97706`):** Amber-600 alerts to mixed-content warnings, certificate mismatches, and DNS leak hazards.

### Text & Telemetry Contrast
- **Primary Text (`#0F172A`):** Deep slate-900 provides definitive contrast against white and slate-50 backgrounds.
- **Secondary Metadata (`#475569`):** Slate-600 handles network headers, process IDs, and protocol labels.
- **Muted & Passive Metadata (`#64748B`):** Slate-500 defines timestamps, dormant ports, and non-critical cryptographic annotations.

## Typography

Typography balances ergonomic UI interaction through **Inter** with technical authenticity via **JetBrains Mono**.

### Functional Hierarchy
- **Primary Interface (Inter):** Headlines, navigations, form fields, and status descriptions leverage Inter's tall x-height and neutral grotesque forms, ensuring instantaneous readability under daylight conditions.
- **Forensic Data & Cryptography (JetBrains Mono):** Network addresses, stream codecs, memory pointers, packet sizes, TLS cipher specs, and hash values are rendered strictly in JetBrains Mono. Its fixed character metrics prevent tabular layout shifting during high-speed parallel stream sniffing.

### Typographic Discipline
- **Tabular Numerics:** Enable tabular figures (`tnum`) across all dynamic numeric values (transfer speeds, byte counts, countdown timers).
- **Truncation & Zero-Width Wrapping:** Cryptographic strings (e.g., SHA-256 signatures, public keys) truncate with an ellipsis in the center (`0x8F24...E98B`) rather than clipping at the end, preserving key identity.

## Layout & Spacing

The layout is built upon an 8-point base grid (supplemented with a 4-point micro-step for compact data tables), engineered for high situational awareness across multi-window operational environments.

### Grid & Breakpoints
- **Compact Viewport (< 640px):** Single-column layout. The live browser sandbox occupies the primary viewport with floating bottom-sheet panels for sniffer feeds and panic execution. Gutters and outer margins default to `1rem` (`space-lg`).
- **Intermediate Viewport (640px – 1024px):** Dual-split view. Browser sandbox (60%) alongside a collapsible telemetry sidebar (40%). Margins step to `1.5rem`.
- **Expanded Operational Viewport (> 1024px):** 12-column adaptive layout. Left-hand rail for identity/isolated proxy containers (2 columns), central stage for active browser session (6 or 7 columns), and right-hand persistent inspector for concurrent media streams, packet headers, and forensic logs (3 or 4 columns). Canvas margins scale to `2rem`.

### Spatial Rhythms
- **Inspector Density:** Compact padding (`space-xs` and `space-sm`) governs internal table rows, network badges, and sniffer capture targets to maximize vertical data visibility.
- **Structural Separation:** Section blocks, panels, and modal bounds use `space-lg` to `space-xl` to prevent accidental touch/click misfires on critical controls.

## Elevation & Depth

To guarantee daylight readability, this system rejects heavy dark drop shadows and tinted blurs in favor of **Crisp Tonal Layering and High-Definition Perimeters**.

### Depth Layers
- **Ground Floor (Base Canvas):** `#F8FAFC`. Zero elevation, serving as the foundational surface.
- **Layer 1 (Contained Panels & Workspaces):** Pure `#FFFFFF` resting on `#F8FAFC`. Depth is established via a 1px continuous border of `#E2E8F0` with an ultra-subtle ambient lift: `box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.04)`.
- **Layer 2 (Floating Inspect Panels & Popovers):** Pure `#FFFFFF` bordered by `#CBD5E1`. Shadow properties: `box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.06), 0 2px 4px -2px rgba(15, 23, 42, 0.06)`.
- **Layer 3 (Modals & Zeroization Warnings):** Pure `#FFFFFF` encapsulated by a 2px border in `#DC2626` (Panic) or `#0F172A` (System). Ambient containment: `box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04)`.

### Ghost Perimeters
Interactive and focusable elements must never rely purely on color transitions. Elements utilize an interior or exterior 1px structural outline that transitions from `#E2E8F0` to `#CBD5E1` on hover, and `#0284C7` on active focus.

## Shapes

The design system adopts a **Soft Geometric (0.25rem / 4px base)** shape profile. 

- **Base Radius (`0.25rem` / `4px`):** Applied to buttons, input fields, sniffer queue rows, tags, status badges, and tab headers. This tight radius preserves an engineered, technical posture while eliminating harsh sharp corners.
- **Container Radius (`rounded-lg` / `0.5rem` / `8px`):** Applied to parent application panels, browser viewport containers, log monitors, and modal dialogs.
- **Pill Radius (`9999px`):** Reserved exclusively for dynamic status pings (e.g., active sniffing indicators, memory wipe counters, connection integrity beacons).

## Components

### Buttons & Operational Actions
- **Primary Sniffer Action:** Background `#0284C7`, text `#FFFFFF`, border `1px solid #0369A1`. Hover: `#0369A1`. Focus-visible: 2px offset ring with `#0284C7`.
- **Vault/Safe Action:** Background `#059669`, text `#FFFFFF`, border `1px solid #047857`. Used for committing credentials to encrypted hardware storage or verifying zero-trace sandboxes.
- **Emergency Panic / Kill-Switch:** Background `#DC2626`, text `#FFFFFF`, font-family `JetBrains Mono`, uppercase, letter-spacing `0.05em`. Active click invokes instantaneous DOM destruction and memory zeroization.
- **Secondary Ghost Controls:** Background `#FFFFFF`, text `#0F172A`, border `1px solid #CBD5E1`. Hover: background `#F1F5F9`.

### Chips & Protocol Badges
- **Format:** Typography `label-sm` (`JetBrains Mono`), padding `2px 8px`, border radius `4px`.
- **Sniffer Stream Detected:** Background `#F0F9FF`, text `#0284C7`, border `1px solid #BAE6FD`.
- **Vault Secured / Encrypted:** Background `#ECFDF5`, text `#059669`, border `1px solid #A7F3D0`.
- **Forensic Alert / Leak:** Background `#FEF2F2`, text `#DC2626`, border `1px solid #FECACA`.

### Media Sniffer Inspection Cards
- **Structure:** Encapsulated white cards (`#FFFFFF`) with a 1px outline of `#E2E8F0`. Hover state elevates the border to `#CBD5E1`.
- **Contents:** 
  - Header: Sniffed file title in `body-md` (Inter, weight 600) + MIME-type badge (JetBrains Mono).
  - Metadata Grid: Resolution, bitrate, segmented chunks (HLS/DASH), and packet origin in `label-sm` slate-600.
  - Action Rail: Single-click download buffer button, stream intercept toggle, and isolated hex viewer launcher.

### Inputs & Omnibox Address Field
- **Surface:** `#FFFFFF` background with 1px border `#CBD5E1`. Internal horizontal padding: `12px`.
- **Security Lock Indicator:** Left-aligned icon and status tag in `#059669` (Encrypted) or `#D97706` (Unverified/Plaintext).
- **Stealth / Incognito Marker:** Distinct right-aligned badge confirming TOR/Proxy/Zero-Trace chain routing.
- **Focus State:** 1px border `#0284C7` with a 2px outer outline in `rgba(2, 132, 199, 0.15)`.

### Checkboxes, Toggles & Selection Elements
- **Checkboxes:** 16x16px boxes with `#CBD5E1` border and 2px border radius. Checked state fills with `#0284C7` displaying a crisp white 1.5px check icon.
- **Cryptographic Toggles:** Monospaced binary switches indicating `[0 / 1]` or `[OFF / ON]` with high-contrast thumb movement and definitive state borders.

### Telemetry Lists & Network Logs
- **Row Styling:** Alternating subtle row backgrounds (`#FFFFFF` to `#F8FAFC`), divided by 1px `#E2E8F0`.
- **Columns:** Monospaced timestamps (`HH:mm:ss.SSS`), HTTP status codes (color-coded: 2xx `#059669`, 4xx/5xx `#DC2626`), transfer latency, and cryptographic payload hash signatures.