# Critique checklist

Use on every screenshot round. Look at the image, not the code. Note the 3–5
worst issues, not every nit.

## First: the machine checks
- Zero `CHECK FAIL` lines from shot.py for the pages you touched.
- Numbers measured with `shot.py --probe`, not guessed (contrast, tap
  target size, font size) — in both themes.
- `token_lint.py <touched files>` clean for the lines you wrote.

## Brief
- Does the page do its one job? Is the primary action obvious within 3 s?
- Does it read as ReUseX — building reuse, scanning, circularity — or could
  any SaaS logo be swapped in?

## Both themes (compare the light and dark shot side by side)
- Every band is readable in both: no dark text on dark, no white card on a
  dark page, no invisible borders/icons.
- Dark mode is designed, not inverted: surfaces step in lightness, accents
  don't glow.
- Images/logos with transparent backgrounds still work on both.

## Hierarchy (squint test)
- Blur your eyes: 1st, 2nd, 3rd thing — does that match importance?
- One dominant element per band; competing focal points are a defect.
- Section bands alternate with intent (colorScheme 1/2/3), not at random —
  and actually look different (schemes 2 and 3 currently share a colour).

## Layout and alignment
- One container width and left edge across bands; nothing a few px off.
- Related items closer than unrelated ones; one vertical rhythm between bands.
- Nothing clipped, overlapping, or overflowing (shot.py flags horizontal
  overflow; look for vertical clipping yourself).
- The fixed header doesn't cover the first heading or anchor targets.

## Typography
- Clear scale, no two sizes that look almost the same.
- Body line length 45–80 characters; line-height ~1.5 for body.
- No widows in headlines; no awkward breaks (check mobile especially).

## Colour
- Body text contrast ≥ 4.5:1, large text ≥ 3:1, in both themes.
- Teal/accent used for meaning (CTA, highlight), not sprinkled.

## Components and polish
- Buttons share height/padding/radius; primary vs secondary obvious.
- Cards in a row have equal height and aligned content.
- Icons one set, one stroke weight, aligned with text.
- Hover/focus visible on links and buttons.

## Content
- Real, specific copy; no lorem ipsum, no "Feature 1", no placeholder links
  (`#`, `twitter.com/reusex` that doesn't exist).
- CTAs name the action and keep the same name everywhere.
- Spelling — the site is English; watch for Danish leaking in
  ("projekt").

## Mobile (390 px shot)
- No horizontal scroll; menu collapses and opens (`--js` to open it).
- Tap targets ≥ 44 px; body text ≥ 16 px.
- Column stacking order still makes sense.

## Restraint
- One memorable move per page, everything else calm.
- Remove one decorative element before calling it done.
