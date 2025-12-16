# ReUseX Color Scheme — Nordic Deep-Tech + Section Themes

This document defines the **NEW color scheme** for the ReUseX website and how to apply it consistently across all pages/sections.

The site uses **three section themes** (background styles). **Each section must use exactly ONE theme**.

---

## Goals

- Create a consistent, VC-friendly “Nordic Deep-Tech” look.
- Use **Teal** only as an intentional accent band (CTAs / hero moments).
- Make sections readable, high-contrast, and predictable across pages.
- Keep implementation flexible (Tailwind + Hugo), but consistent in output.

---

## Color Palette (Option A)

### Section Backgrounds
- **Section 1 (Teal band):** `#14B8A6`
- **Section 2 (Navy alt):** `#0D1628`
- **Section 3 (Dark base):** `#0B1220`

### Shared UI Colors
- **Surface / Cards / Panels:** `#0F172A`
- **Border:** `#1E293B`
- **Border subtle:** `#22314A`
- **Card hover / elevated surface (optional):** `#111E36`

### Text (for dark sections: Section 2 & 3)
- **Heading text:** `#E2E8F0`
- **Body text:** `#CBD5E1`
- **Muted text:** `#94A3B8`
- **Disabled text:** `#64748B`

### Links
- **Link:** `#38BDF8`
- **Link hover:** `#0EA5E9`

### Primary Actions (when used as a button fill)
- **Primary:** `#14B8A6`
- **Hover:** `#0D9488`
- **Active:** `#0F766E`
- **Primary button text (on teal button):** `#071018`

### Highlight (sparingly)
- **Highlight:** `#FBBF24`
- **Highlight soft background:** `#2A2010`

---

## Section Themes (rules for what colors to use inside each section)

### Section 1 Theme (Teal band)
Background: `#14B8A6`

Text:
- Headings: `#0B1220`
- Body: `#0B1220`
- Muted/small: `#0B1220` at ~70% opacity (or use `#0F172A` if opacity isn’t convenient)

Links:
- Link: `#0B1220` (use underline or semibold)
- Hover: `#0F172A`

Cards/panels inside Section 1:
- Card bg: `#0F172A`
- Card border: `#1E293B`
- Card heading/body/muted: `#E2E8F0 / #CBD5E1 / #94A3B8`

Buttons inside Section 1 (**important rule**):
- Do **NOT** use teal buttons on teal background.
- Primary button:
  - bg `#0F172A`
  - text `#E2E8F0`
  - hover bg `#111E36`
- Secondary button:
  - bg `transparent`
  - border `#0B1220`
  - text `#0B1220`
  - hover bg `rgba(11,18,32,0.08)` (or a slightly darker teal tint)

---

### Section 2 Theme (Navy alt — main content band)
Background: `#0D1628`

Text:
- Headings: `#E2E8F0`
- Body: `#CBD5E1`
- Muted: `#94A3B8`

Links:
- Link `#38BDF8`, hover `#0EA5E9`

Cards/panels:
- Card bg `#0F172A`, border `#1E293B`, optional hover `#111E36`

Buttons:
- Primary button bg `#14B8A6`, text `#071018`, hover `#0D9488`, active `#0F766E`
- Secondary button bg `transparent`, border `#1E293B`, text `#E2E8F0`, hover border `#22314A`

Callouts/highlights (sparingly):
- Callout bg `#2A2010`, title `#FBBF24`, body `#CBD5E1`

---

### Section 3 Theme (Dark base — anchor band)
Background: `#0B1220`

Use the **same** component colors as Section 2 (text, links, cards, buttons).
Section 3 is primarily used for hero/footer/foundational blocks and to create rhythm against Section 2.

Footer defaults (if footer uses Section 3):
- Divider/border: `#1E293B`
- Small text: `#94A3B8`

---

## Section Theme Assignment (by section file)

Each section file must map to exactly one theme:

### Section 1 (Teal)
- `hero.md`
- `cta.md` (teal CTA version)

### Section 2 (Default)
- `challenges.md`
- `stats.md`
- `blog.md`
- All other pages/sections not explicitly listed below

### Section 3 (Dark)
- `solution.md`
- `_index.md`
- `cta.md` (dark CTA version, if used)

### Important note about `cta.md` (potential conflict)
If you only have ONE CTA section: make it **Section 1 (teal)**.

If you need TWO CTAs (one teal + one dark), create **two CTA variants**, e.g.:
- `cta-teal.md` → Section 1 theme
- `cta-dark.md` → Section 3 theme

(Alternative: add a parameter like `sectionStyle: 1|3` and choose the theme class in the template.)

---

## Implementation Notes (Tailwind + Hugo)

Implementation approach is flexible, but recommended pattern:

1) Add these palette values as Tailwind tokens (e.g. `reusex.*`) or CSS variables.
2) Define 3 reusable section classes:
   - `.section-1` → Section 1 theme
   - `.section-2` → Section 2 theme
   - `.section-3` → Section 3 theme
3) Apply the correct section class in each section template/partial rendering `hero.md`, `solution.md`, etc.
4) Ensure SVG icons use `currentColor` (Tailwind `fill-current` / `stroke-current`) so they adapt automatically.

---

## Quick QA Checklist

- Every section uses exactly one theme: Section 1 OR Section 2 OR Section 3.
- Only one (or very few) sections use the teal Section 1 band per page.
- Text contrast is readable on all backgrounds (especially teal band).
- Primary button on teal band is **dark**, not teal.
- Links look like links (color + hover + underline/weight).
- Cards consistently use `#0F172A` with `#1E293B` borders.
