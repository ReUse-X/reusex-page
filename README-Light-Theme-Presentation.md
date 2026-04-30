# ReUseX — Light Color Scheme & Presentation Layout

This document describes the **light color scheme** (`data-theme="light"`) and the graphical layout of the ReUseX pitch-deck presentation, so that anyone setting up or extending slides can keep a consistent look.

---

## 1. Activating the Light Theme

The site supports three themes selectable by the user (via the sun/moon toggle in the header):

| Attribute value | When active |
|---|---|
| *(none / default)* | "Nordic Deep-Tech" dark palette |
| `data-theme="dark"` | Dark-gray palette (`#343634`) |
| `data-theme="light"` | **Off-white / high-contrast palette** |

The theme is stored in `localStorage` and applied to the `<html>` element as `data-theme="light"`.

---

## 2. Light Color Palette

All values below are the CSS custom properties that are overridden inside `[data-theme="light"]` in `themes/reusex/assets/css/main.css`.

### 2.1 Global Tokens

| Token | Value | Role |
|---|---|---|
| `--surface-bg` | `#F5F4F0` | Page / card background |
| `--header-bg` | `rgba(245,244,240,0.95)` | Sticky nav bar (frosted) |
| `--footer-bg` | `#F5F4F0` | Footer background |
| `--border` | `#000000` | Card / divider borders |
| `--border-subtle` | `#000000` | Subtle borders |
| `--graphic` | `#000000` | SVG graphic strokes |
| `--heading-text` | `#000000` | All headings |
| `--body-text` | `#000000` | Body paragraphs |
| `--muted-text` | `#000000` | Secondary / caption text |
| `--disabled-text` | `#94A3B8` | Disabled / placeholder text |
| `--link` | `#0284C7` | Hyperlink color |
| `--link-hover` | `#0369A1` | Hyperlink hover color |
| `--highlight` | `#D97706` | Amber accent (callouts) |
| `--highlight-soft-bg` | `#FEF3C7` | Soft amber callout background |

### 2.2 Action Colors

| Token | Value | Role |
|---|---|---|
| `--primary-teal` | `#0D9488` | Primary teal (buttons, accents) |
| `--primary-hover` | `#0F766E` | Primary button hover |
| `--primary-active` | `#115E59` | Primary button active |
| `--card-hover` | `#ECEAE4` | Card elevated / hover background |
| `--cta-bg` | `#000000` | "Log in / Get Started" button fill |
| `--cta-text` | `#FFFFFF` | "Log in / Get Started" button label |

### 2.3 Pitch-Deck Accent Colors

| Token | Value | Role |
|---|---|---|
| `--pitchdeck-accent` | `#000000` | Slide numbers, step numbers, bullet chevrons |
| `--pitchdeck-accent-text` | `#FFFFFF` | Text on accent-colored backgrounds |

---

## 3. Section Themes in Light Mode

The site divides every page into three named section bands. In light mode **all three share the same off-white background** (`#F5F4F0`) while text is forced to pure black for maximum contrast.

### Section 1 (Hero / CTA band)

| Token | Value |
|---|---|
| `--section1-bg` | `#F5F4F0` |
| `--section1-text` | `#000000` |
| `--section1-card-bg` | `#F5F4F0` |
| `--section1-card-border` | `#000000` |
| `--section1-card-heading` | `#000000` |
| `--section1-card-body` | `#000000` |
| `--section1-card-muted` | `#000000` |
| `--section1-btn-primary-bg` | `#0F172A` |
| `--section1-btn-primary-text` | `#F5F4F0` |
| `--section1-btn-primary-hover` | `#1E293B` |

> **Hero background override:** The hero section in light mode also reads the `heroBg` front-matter field from `content/sections/hero.md` (e.g. `heroBg: "#D2D2CD"`) and applies it as `--hero-bg-light`. Set this field to change only the hero strip without affecting the rest of Section 1.

### Section 2 (Main content band)

| Token | Value |
|---|---|
| `--section2-bg` | `#F5F4F0` |
| `--section2-heading` | `#000000` |
| `--section2-body` | `#000000` |
| `--section2-muted` | `#000000` |
| `--section2-link` | `#0284C7` |
| `--section2-link-hover` | `#0369A1` |
| `--section2-card-bg` | `#F5F4F0` |
| `--section2-card-border` | `#000000` |
| `--section2-card-hover` | `#ECEAE4` |
| `--section2-callout-bg` | `#FEF3C7` |
| `--section2-callout-title` | `#D97706` |

### Section 3 (Dark base / Footer)

| Token | Value |
|---|---|
| `--section3-bg` | `#F5F4F0` |
| `--section3-heading` | `#000000` |
| `--section3-body` | `#000000` |
| `--section3-muted` | `#000000` |
| `--section3-link` | `#0284C7` |
| `--section3-link-hover` | `#0369A1` |
| `--section3-card-bg` | `#F5F4F0` |
| `--section3-card-border` | `#000000` |
| `--section3-divider` | `#000000` |

### Icon & Timeline Tokens

| Token | Value |
|---|---|
| `--icon-color` | `#000000` |
| `--timeline-heading` | `#000000` |
| `--timeline-text` | `#000000` |

---

## 4. Pitch-Deck Presentation Layout

The pitch deck lives at `/pitchdeck/` and is built from individual Markdown slide files in `content/pitchdeck/`. Slides are sorted by the `order` front-matter field.

### 4.1 Page Structure

```
Fixed header (nav + theme toggle)
└── #pitchdeck  (full-viewport wrapper, background: --section3-bg)
    └── .pitchdeck-slides  (overflow: hidden)
        ├── .pitchdeck-slide  (one per slide, display: flex / none)
        │   └── .pitchdeck-slide-inner  (max-width: 900–1100 px)
        │       ├── .pitchdeck-slide-header  (slide number + h2 + subtitle)
        │       └── <slide-specific content>
        └── …
    ← arrow button (prev)
    → arrow button (next)
    ⊕ fullscreen button
    • dot navigation bar (#pitchdeck-nav)
```

### 4.2 Slide Types

Each slide file's front-matter determines which layout variant is rendered:

| Front-matter key | Slide variant | Example file |
|---|---|---|
| *(none, `order: 1`)* | **Cover** — giant title, subtitle, tagline, CTA button | `01-cover.md` |
| `points` (list) | **Bullet list** — items in card-style rows with `→` chevron | `02-problem.md` |
| `steps` (list) | **Steps grid** — numbered cards in a responsive grid | `05-how-it-works.md` |
| `milestones` (list) | **Milestones grid** — year + label + description cards | `09-roadmap.md` |
| `pilots` (list) | **Pilots grid** — pilot cards with eyebrow label | `07-pilots.md` |
| `cards` (list) | **Team cards** — portrait image + name + role | `10-team.md` |
| `metrics` + `points` | **Metrics + bullets** — stat blocks above a checklist | `11-impact.md` |
| `cta` (object, last slide) | **Call-to-action** — centered headline + bullet list + CTA button | `12-cta.md` |

### 4.3 Slide Front-Matter Fields

```yaml
---
title: "Slide Heading"        # Displayed as <h2> (or <h1> on cover)
subtitle: "Optional tagline"  # Displayed below the heading
order: 3                      # Determines slide order (required)
slide: true                   # Must be true to include this file
---
```

Additional fields per slide type:

**Bullet-list slide:**
```yaml
points:
  - "**Stat** — description of the point"
```

**Steps slide:**
```yaml
steps:
  - number: "01"
    label: "Step Name"
    description: "What happens in this step."
```

**Milestones slide:**
```yaml
milestones:
  - year: "2024"
    label: "Phase label"
    description: "What was achieved."
```

**Pilots slide:**
```yaml
pilots:
  - label: "Pilot Name"
    description: "Description of the pilot."
```

**Team-cards slide:**
```yaml
cards:
  - name: "Full Name"
    role: "Job Title"
    image: "portraits/filename.jpg"   # relative to content/people/
    social:
      linkedin: "https://linkedin.com/in/handle"
```

**Metrics slide:**
```yaml
metrics:
  - value: "40%"
    label: "Short metric label"
points:
  - "Supporting statement"
```

**CTA slide (last slide):**
```yaml
cta:
  url: "/contact/"
  text: "Button Label"
points:
  - "Reason to act"
```

### 4.4 Graphical Details

#### Colors used inside slides (light theme)

| Element | CSS token used | Light value |
|---|---|---|
| Slide wrapper background | `--section3-bg` | `#F5F4F0` |
| Card / step / pilot backgrounds | `--section2-bg` | `#F5F4F0` |
| Metric highlight cards | `--section1-bg` | `#F5F4F0` |
| Card borders | `--border` | `#000000` |
| Heading text (`<h1>`, `<h2>`) | `--heading-text` | `#000000` |
| Body / description text | `--body-text` | `#000000` |
| Accent (slide numbers, step numbers, chevrons) | `--pitchdeck-accent` | `#000000` |
| Accent text (badge on accent bg) | `--pitchdeck-accent-text` | `#FFFFFF` |
| Navigation arrows | `--section2-bg` / `--body-text` | `#F5F4F0` / `#000000` |

#### Typography

| Element | Size (clamp) | Weight |
|---|---|---|
| Cover title (`<h1>`) | `3rem → 6rem` | 900 |
| Slide heading (`<h2>`) | `2rem → 3.5rem` | 800 |
| Subtitle | `1.25rem` | 400 |
| Step/card number | `2.5rem` | 900 |
| Step/card label | `1.25rem` | 700 |
| Step/card description | `0.95rem` | 400 |
| Slide counter label | `0.85rem` | 700, uppercase, letter-spacing |

#### Navigation & Controls

- **Left / right arrows** — fixed at vertical center, `0.75 rem` from viewport edges; `2.75 rem` diameter circles.
- **Dot navigation bar** (`#pitchdeck-nav`) — centered at the bottom; one filled dot per slide, active dot highlighted.
- **Fullscreen button** — shown in the nav bar; uses the native Fullscreen API with a CSS fallback for iOS Safari.
- **Close (×) button** — appears top-right only while fullscreen is active.

#### Responsive / Mobile Behaviour

| Breakpoint | Behaviour |
|---|---|
| `≤ 480 px` | Arrow buttons shrink to `2 rem` |
| `≤ 1024 px` (portrait) | `.pitchdeck-slide-inner` gets a `min-width: 720px` and is CSS-scaled to fit the viewport |
| `≤ 1024 px` (landscape) | Slides are condensed: grids switch to 4 / 3 columns, typography is scaled down, team portraits become `60 px` tall rows |

---

## 5. Adding or Modifying Slides

1. Create a new file in `content/pitchdeck/`, e.g. `06b-market.md`.
2. Set `order` to position it in the sequence (existing slides will re-number automatically).
3. Set `slide: true`.
4. Choose a front-matter structure from [Section 4.2](#42-slide-types) above.
5. No template changes are needed — the layout in `layouts/pitchdeck/list.html` selects the correct rendering variant automatically.

---

## 6. Quick QA Checklist (Light Theme + Presentation)

- [ ] `data-theme="light"` is set on `<html>` (check via DevTools or the theme toggle).
- [ ] All slide backgrounds are `#F5F4F0`; no leftover dark values appear.
- [ ] Headings and body text are `#000000`; contrast ratio ≥ 7:1 on off-white.
- [ ] Accent elements (slide numbers, chevrons, badge) use `#000000` with `#FFFFFF` text.
- [ ] Logos switch to the black-on-white variant (`.logo-light-only` is shown; `.logo-default` is hidden).
- [ ] CTA / "Log in" button: black fill (`#000000`) with white text (`#FFFFFF`).
- [ ] Callout blocks use amber (`#FEF3C7` bg, `#D97706` title) only sparingly.
- [ ] Slides are ordered correctly (verify `order` values are unique and sequential).
- [ ] All slides have `slide: true` in front-matter.
- [ ] Fullscreen works on desktop (native API) and iOS Safari (CSS fallback).
