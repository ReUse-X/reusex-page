# ReUseX Content Management Guide

This guide explains how to customize the content on your ReUseX landing page and manage blog posts through Hugo's content system.

## Quick Start

1. **Homepage Sections**: Edit individual files in `content/sections/` to customize each landing page section
2. **Homepage Content**: Edit `content/_index.md` for basic page metadata and content
3. **Blog Posts**: Create `.md` files in `content/` with `type: "post"`  
4. **Static Pages**: Create `.md` files in `content/` with `type: "page"`

## Section Files

Each section of the homepage is now managed in its own file under `content/sections/`:

- `hero.md` - Hero section with title, subtitle, and call-to-action buttons
- `testimonial.md` - Customer testimonial/quote
- `challenges.md` - Problem statement section
- `solution.md` - Solution features section
- `stats.md` - Impact metrics and statistics
- `cta.md` - Call-to-action section
- `blog.md` - Blog posts display configuration

### Benefits of Separate Section Files

- **Better Organization**: Each section is in its own file, making it easier to find and edit specific content
- **Reduced Complexity**: No more scrolling through a large metadata block in `_index.md`
- **Version Control**: Changes to individual sections are easier to track in git
- **Team Collaboration**: Multiple team members can work on different sections without merge conflicts
- **Maintainability**: Cleaner structure makes it easier to add, remove, or modify sections

## Editable Sections

### 1. Hero Section (`content/sections/hero.md`)
```yaml
---
title: "ReUseX"
subtitle: "Revolutionizing resource reuse for a sustainable future"
cta_primary:
  text: "Get Started Today"
  url: "https://app.reusex.com/signup"
cta_secondary:
  text: "Learn More"
  url: "#about"
headless: true
---
```

### 2. Testimonial/Quote (`content/sections/testimonial.md`)
```yaml
---
quote: "This platform revolutionizes how we think about resource reuse."
author: "Dr. Sarah Chen"
title: "Environmental Expert"
rating: 5
headless: true
---
```

### 3. Current Challenges Section (`content/sections/challenges.md`)
```yaml
---
title: "Current Challenges"
subtitle: "The waste crisis demands urgent action..."
items:
  - icon: "warning"           # Options: warning, puzzle, currency
    title: "Resource Waste"
    description: "Billions of tons of materials..."
    color: "red"             # Options: red, amber, rose
headless: true
---
```

### 4. Solution Features (`content/sections/solution.md`)
```yaml
---
title: "The ReUseX Solution"
subtitle: "Our intelligent platform transforms..."
features:
  - icon: "lightning"        # Options: lightning, network, analytics
    title: "AI-Powered Matching"
    description: "Our advanced algorithms..."
    color: "blue"           # Options: blue, emerald, purple
headless: true
---
```

### 5. Statistics (`content/sections/stats.md`)
```yaml
---
title: "Impact at Scale"
subtitle: "Real results from organizations..."
metrics:
  - value: "85%"
    label: "Waste Reduction"
headless: true
---
```

### 6. Call-to-Action Section (`content/sections/cta.md`)
```yaml
---
title: "Ready to Transform Your Resource Management?"
subtitle: "Join the circular economy revolution..."
primary_button:
  text: "Start Free Trial"
  url: "https://app.reusex.com/signup"
secondary_button:
  text: "Schedule Demo"
  url: "https://calendly.com/reusex/demo"
features:
  - "No credit card required"
  - "30-day free trial"
  - "Cancel anytime"
headless: true
---
```

### 7. Blog Posts Section (`content/sections/blog.md`)
```yaml
---
title: "Latest Updates"
subtitle: "Stay informed about the latest developments..."
show_posts: true
posts_count: 6
headless: true
---
```

## Available Icons

**Challenge Icons:**
- `warning` - Warning triangle
- `puzzle` - Fragmented puzzle pieces
- `currency` - Money/cost symbol

**Solution Icons:**
- `lightning` - Lightning bolt (speed/power)
- `network` - Network/connection icon
- `analytics` - Bar chart/analytics

## Available Colors

**For Challenge Items:**
- `red` - Red gradient backgrounds
- `amber` - Amber/yellow gradient backgrounds  
- `rose` - Rose/pink gradient backgrounds

**For Solution Features:**
- `blue` - Blue gradient backgrounds
- `emerald` - Green gradient backgrounds
- `purple` - Purple gradient backgrounds

## Adding Blog Posts

Create new markdown files in the `content/` directory with front matter and set `type: "post"`:

```yaml
---
title: "Your Post Title"
date: 2024-12-01
summary: "Brief description for the homepage preview"
type: "post"
---

Your post content in Markdown...
```

The most recent posts will automatically appear on the homepage if `blog.show_posts` is set to `true`.

## Content Organization

**Homepage Sections**: Individual files in `content/sections/` directory, each marked as `headless: true`
**Homepage Content**: Basic metadata and content in `content/_index.md`
**Blog Posts**: Set `type: "post"` in front matter - these appear on homepage
**Static Pages**: Set `type: "page"` in front matter - these don't appear in blog listings

## Button Links

All buttons support both `text` and `url` properties:

```yaml
button_name:
  text: "Button Text"
  url: "https://example.com"
```

### Common URL Patterns

**External Links:**
- `"https://app.reusex.com/signup"` - Your app signup page
- `"https://calendly.com/reusex/demo"` - Calendly scheduling link
- `"mailto:sales@reusex.com"` - Email links

**Internal Links:**
- `"#about"` - Jump to section on same page
- `"/contact"` - Link to other pages on your site (automatically handles subdirectories)
- `"/features#pricing"` - Link to specific section on another page

**Special Links:**
- `"tel:+1-555-123-4567"` - Phone number links
- `"#"` - Disabled/placeholder link

### Smart URL Handling

The theme automatically detects and properly handles different URL types:
- **Internal paths** like `/contact` work regardless of subdirectory hosting
- **External URLs** like `https://app.example.com` are used as-is
- **Anchors** like `#about` are used as-is for page sections
- **Email/phone** links like `mailto:` and `tel:` are preserved

## Footer Configuration

The footer is configured in `hugo.toml` under `[params.footer]`:

```toml
[params.footer]
  description = "Your footer description text"
  
  # Social Media Links (all optional)
  [params.footer.social]
    twitter = "https://twitter.com/yourcompany"
    linkedin = "https://linkedin.com/company/yourcompany"
    facebook = "https://facebook.com/yourcompany"
    github = "https://github.com/yourcompany"
    instagram = "https://instagram.com/yourcompany"
    
  # Footer Menus
  [[params.footer.menus]]
    title = "Product"
    [[params.footer.menus.links]]
      name = "Features"
      url = "/features"
    [[params.footer.menus.links]]
      name = "Pricing" 
      url = "#demo"
      
  [[params.footer.menus]]
    title = "Support"
    [[params.footer.menus.links]]
      name = "Contact Us"
      url = "/contact"
```

### Social Media Options
- `twitter` - Twitter/X profile URL
- `linkedin` - LinkedIn company page URL
- `facebook` - Facebook page URL  
- `github` - GitHub organization/user URL
- `instagram` - Instagram profile URL

### Footer Menu Structure
- Each menu has a `title` and multiple `links`
- Links have `name` (display text) and `url` (destination)
- You can have multiple menu columns
- If no footer menus are configured, it falls back to the main site menu

## Tips

1. Keep titles concise but descriptive
2. Summaries should be 1-2 sentences for best display
3. Use consistent language and tone across sections
4. Test changes by running `hugo server` locally
5. The `posts_count` setting controls how many blog posts show on the homepage (default: 6)
6. Always test button links to ensure they work correctly
7. Use HTTPS links for external websites
8. Internal section links (like `#about`) should match section IDs in your template
9. Social media links will only appear if configured - leave them empty to hide icons
10. Footer menus support both internal (`/about`) and external (`https://...`) links
11. You don't need to worry about subdirectories - `/contact` works for both `example.com/contact` and `example.com/my-site/contact`