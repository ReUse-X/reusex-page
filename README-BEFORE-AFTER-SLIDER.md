# Before-and-After Image Slider Component

## Overview

This document describes the before-and-after image slider component that allows users to interactively compare two images by sliding a handle horizontally. The component is lightweight, accessible, and requires no external dependencies or build tools.

## Features

- **Lightweight**: Pure HTML, CSS, and JavaScript - no frameworks or libraries required
- **Accessible**: Full keyboard navigation support (arrow keys, Home, End)
- **Responsive**: Works on desktop, tablet, and mobile devices
- **Touch-Enabled**: Supports touch gestures for mobile devices
- **Multiple Sliders**: Can have multiple sliders on the same page without conflicts
- **ARIA Support**: Includes proper ARIA labels for screen readers
- **Visual Feedback**: Smooth animations and hover effects

## Files

The slider component consists of three parts:

1. **CSS**: `/themes/reusex/assets/css/main.css` (bottom section)
2. **JavaScript**: `/themes/reusex/assets/js/main.js` (bottom section)
3. **Images**: `/static/images/before.jpg` and `/static/images/after.jpg` (sample images)

## Usage

### Basic HTML Structure

To add a before-and-after slider to any page, use the following HTML structure:

```html
<!-- Before-and-After Image Slider Container -->
<div class="before-after-slider">
  <div class="before-after-wrapper">
    <!-- REPLACE THESE IMAGE PATHS with your own images -->
    <img src="/images/after.jpg" alt="After: Your after image description" class="after-image">
    <img src="/images/before.jpg" alt="Before: Your before image description" class="before-image">
  </div>
  <div class="before-after-divider">
    <div class="before-after-handle" tabindex="0"></div>
  </div>
  <!-- Optional labels -->
  <span class="before-after-label before" aria-hidden="true">Before</span>
  <span class="before-after-label after" aria-hidden="true">After</span>
</div>
```

### Customizing Images

1. **Add your images** to the `/static/images/` directory
2. **Replace the image paths** in the HTML:
   - Replace `/images/after.jpg` with your "after" image path
   - Replace `/images/before.jpg` with your "before" image path
3. **Update alt text** to describe your images for accessibility

### Image Requirements

- **Format**: JPG, PNG, or WebP
- **Recommended Size**: 800x600px or similar aspect ratio
- **Aspect Ratio**: Images should have the same aspect ratio (default is 4:3)
- **File Size**: Optimize images for web (< 500KB recommended)

## Integration Examples

### Example 1: In Hugo Content (Markdown)

For Hugo-based pages, you can add the slider using HTML in your markdown files:

```markdown
---
title: "My Page"
---

## Before and After Comparison

<div class="before-after-slider">
  <div class="before-after-wrapper">
    <img src="/images/my-after.jpg" alt="After renovation" class="after-image">
    <img src="/images/my-before.jpg" alt="Before renovation" class="before-image">
  </div>
  <div class="before-after-divider">
    <div class="before-after-handle" tabindex="0"></div>
  </div>
  <span class="before-after-label before" aria-hidden="true">Before</span>
  <span class="before-after-label after" aria-hidden="true">After</span>
</div>

Regular markdown content continues here...
```

### Example 2: Multiple Sliders on One Page

You can have multiple sliders on the same page. Each slider operates independently:

```html
<div class="grid gap-12">
  <!-- First Slider -->
  <div>
    <h3>Project A</h3>
    <div class="before-after-slider">
      <div class="before-after-wrapper">
        <img src="/images/project-a-after.jpg" alt="Project A After" class="after-image">
        <img src="/images/project-a-before.jpg" alt="Project A Before" class="before-image">
      </div>
      <div class="before-after-divider">
        <div class="before-after-handle" tabindex="0"></div>
      </div>
      <span class="before-after-label before" aria-hidden="true">Before</span>
      <span class="before-after-label after" aria-hidden="true">After</span>
    </div>
  </div>

  <!-- Second Slider -->
  <div>
    <h3>Project B</h3>
    <div class="before-after-slider">
      <div class="before-after-wrapper">
        <img src="/images/project-b-after.jpg" alt="Project B After" class="after-image">
        <img src="/images/project-b-before.jpg" alt="Project B Before" class="before-image">
      </div>
      <div class="before-after-divider">
        <div class="before-after-handle" tabindex="0"></div>
      </div>
      <span class="before-after-label before" aria-hidden="true">Before</span>
      <span class="before-after-label after" aria-hidden="true">After</span>
    </div>
  </div>
</div>
```

### Example 3: In Hugo Templates

For use in Hugo template files (`.html` files in `/themes/reusex/layouts/`):

```html
{{ with .Params.before_after_images }}
<div class="before-after-slider">
  <div class="before-after-wrapper">
    <img src="{{ .after | relURL }}" alt="{{ .after_alt }}" class="after-image">
    <img src="{{ .before | relURL }}" alt="{{ .before_alt }}" class="before-image">
  </div>
  <div class="before-after-divider">
    <div class="before-after-handle" tabindex="0"></div>
  </div>
  <span class="before-after-label before" aria-hidden="true">Before</span>
  <span class="before-after-label after" aria-hidden="true">After</span>
</div>
{{ end }}
```

Then in your front matter:

```yaml
---
title: "My Page"
before_after_images:
  before: "/images/before.jpg"
  before_alt: "Before renovation"
  after: "/images/after.jpg"
  after_alt: "After renovation with reused materials"
---
```

## User Interactions

### Mouse/Trackpad
- **Click and drag** the circular handle to move the divider
- **Click anywhere** on the image to jump the divider to that position
- **Hover** over the handle for visual feedback

### Touch (Mobile/Tablet)
- **Touch and drag** the handle to move the divider
- **Tap anywhere** on the image to jump the divider to that position

### Keyboard (Accessibility)
- **Tab** to focus on the handle
- **Arrow Left/Right** to move the divider in 5% increments
- **Home** to move divider to the far left (100% before image)
- **End** to move divider to the far right (100% after image)

## Customization

### Changing the Aspect Ratio

To change the aspect ratio, modify the `padding-top` value in `/themes/reusex/assets/css/main.css`:

```css
/* For 16:9 aspect ratio */
.before-after-slider::before {
  padding-top: 56.25%; /* (9/16) * 100 */
}

/* For 1:1 square */
.before-after-slider::before {
  padding-top: 100%;
}

/* For 3:2 aspect ratio */
.before-after-slider::before {
  padding-top: 66.67%; /* (2/3) * 100 */
}
```

### Changing Colors

To customize the colors, modify these CSS properties:

```css
/* Handle color */
.before-after-handle {
  background-color: white; /* Change to your preferred color */
}

/* Divider line color */
.before-after-divider {
  background-color: white; /* Change to your preferred color */
}

/* Label background */
.before-after-label {
  background-color: rgba(0, 0, 0, 0.6); /* Change to your preferred color */
  color: white; /* Change text color */
}
```

### Changing the Starting Position

By default, the slider starts at 50% (centered). To change this, modify the JavaScript in `/themes/reusex/assets/js/main.js`:

```javascript
// Find this line near the end of initBeforeAfterSliders():
updateSliderPosition(50); // Change 50 to your preferred percentage (0-100)
```

## Troubleshooting

### Slider Not Working
1. Ensure JavaScript is enabled in the browser
2. Check browser console for errors
3. Verify that all HTML elements have the correct class names
4. Ensure images are loading properly (check Network tab in dev tools)

### Images Not Showing
1. Verify image paths are correct
2. Check that images exist in `/static/images/` directory
3. Ensure image file names match exactly (case-sensitive)
4. Check that images have appropriate permissions

### Multiple Sliders Conflicting
- The component is designed to handle multiple sliders automatically
- Each slider is initialized independently
- If issues occur, check that each slider has unique image sources

### Styling Issues
1. Ensure the CSS is loaded (check browser dev tools)
2. Check for CSS conflicts with other components
3. Verify that parent containers aren't constraining the slider unexpectedly

## Browser Support

The slider component works in all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

**Note**: Internet Explorer is not supported due to use of modern CSS features.

## Accessibility Features

- **ARIA Attributes**: Proper role, label, and value attributes for screen readers
- **Keyboard Navigation**: Full keyboard support for users who cannot use a mouse
- **Focus Indicators**: Visible focus outline when using keyboard navigation
- **Alt Text**: Images should include descriptive alt text
- **Color Contrast**: Labels have sufficient contrast for readability

## Performance Considerations

- Images are loaded normally (not lazy-loaded by default)
- Component has minimal JavaScript overhead
- CSS uses GPU-accelerated properties (transform, clip-path)
- No external dependencies means faster page loads

## Demo Location

A working example can be found on the home page in the "The ReUseX Solution" section, or you can view it directly at:
- Live Site: `https://[your-domain]/` (Solution section)
- Development: Run `hugo server` and navigate to the home page

## Credits

Component created for the ReUseX project by Link Arkitektur.
No third-party libraries used - pure HTML, CSS, and JavaScript.

## License

SPDX-License-Identifier: GPL-3.0-or-later

This component is part of the ReUseX project and is licensed under the GPL-3.0-or-later license.
