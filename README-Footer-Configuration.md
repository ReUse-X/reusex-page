# Footer Configuration Guide

The footer is fully configurable through your `hugo.toml` file. This allows you to customize social media links, footer menus, and description without touching any code.

## Basic Footer Setup

Add this to your `hugo.toml` file under the `[params]` section:

```toml
[params.footer]
  description = "Building the future of sustainable resource management through innovative technology and collaborative networks."
```

## Social Media Links

Add social media links that will appear as icons in the footer:

```toml
[params.footer.social]
  twitter = "https://twitter.com/reusex"
  linkedin = "https://linkedin.com/company/reusex"
  facebook = "https://facebook.com/reusex"
  github = "https://github.com/reusex"
  instagram = "https://instagram.com/reusex"
```

**Available Social Platforms:**
- `twitter` - Twitter/X 
- `linkedin` - LinkedIn
- `facebook` - Facebook
- `github` - GitHub
- `instagram` - Instagram

**Notes:**
- Only configured platforms will show up
- Leave empty or remove lines you don't want
- Links automatically open in new tabs
- Icons use recognizable brand SVGs

## Footer Menus

Create organized footer navigation with multiple columns:

```toml
# First Menu Column
[[params.footer.menus]]
  title = "Product"
  [[params.footer.menus.links]]
    name = "Features"
    url = "/features"
  [[params.footer.menus.links]]
    name = "Pricing" 
    url = "#demo"
  [[params.footer.menus.links]]
    name = "Documentation"
    url = "/docs"
  [[params.footer.menus.links]]
    name = "API Reference"
    url = "/api"

# Second Menu Column    
[[params.footer.menus]]
  title = "Support"
  [[params.footer.menus.links]]
    name = "Help Center"
    url = "/help"
  [[params.footer.menus.links]]
    name = "Contact Us"
    url = "/contact"
  [[params.footer.menus.links]]
    name = "Privacy Policy"
    url = "/privacy"
  [[params.footer.menus.links]]
    name = "Terms of Service"
    url = "/terms"
```

## Complete Example

Here's a complete footer configuration:

```toml
[params.footer]
  description = "Revolutionizing resource management for a sustainable future through AI-powered matching and collaborative networks."
  
  [params.footer.social]
    twitter = "https://twitter.com/reusex"
    linkedin = "https://linkedin.com/company/reusex"
    github = "https://github.com/reusex"
    
  [[params.footer.menus]]
    title = "Product"
    [[params.footer.menus.links]]
      name = "Features"
      url = "/features"
    [[params.footer.menus.links]]
      name = "Pricing" 
      url = "#demo"
    [[params.footer.menus.links]]
      name = "Case Studies"
      url = "/case-studies"
      
  [[params.footer.menus]]
    title = "Company"
    [[params.footer.menus.links]]
      name = "About Us"
      url = "/about"
    [[params.footer.menus.links]]
      name = "Careers"
      url = "/careers"
    [[params.footer.menus.links]]
      name = "Contact"
      url = "/contact"
      
  [[params.footer.menus]]
    title = "Resources"
    [[params.footer.menus.links]]
      name = "Blog"
      url = "/blog"
    [[params.footer.menus.links]]
      name = "Help Center"
      url = "/help"
    [[params.footer.menus.links]]
      name = "API Docs"
      url = "/api"
```

## URL Types Supported

**Internal Pages:**
- `/about` - Links to about page (automatically handles subdirectories)
- `/contact` - Links to contact page (automatically handles subdirectories)
- `/features` - Links to features page (automatically handles subdirectories)

**Page Sections:**
- `#demo` - Scrolls to demo section on current page
- `#about` - Scrolls to about section on current page

**External Links:**
- `https://docs.reusex.com` - Links to external documentation
- `https://app.reusex.com` - Links to your application
- `mailto:hello@reusex.com` - Opens email client
- `tel:+1-555-123-4567` - Opens phone dialer

### Smart URL Handling

The theme automatically handles different URL types:

- **Internal links** (like `/contact`) are automatically adjusted for subdirectories
- **External links** (starting with `http`) are used as-is
- **Anchors** (starting with `#`) are used as-is  
- **Email/phone** links (starting with `mailto:` or `tel:`) are used as-is

This means you never need to worry about your site's subdirectory - just use `/contact` and it will work whether your site is at `example.com` or `example.com/my-site/`.

## Fallback Behavior

If no footer menus are configured, the footer will automatically:
1. Show a "Navigation" menu using your main site navigation
2. Show a "Support" menu with basic Contact/About links

This ensures your footer never appears empty.

## Styling Notes

- Footer uses a dark background with white text
- Social icons have hover effects
- Links have smooth color transitions
- Responsive design works on all device sizes
- Copyright notice is automatically generated with current year

## Testing Your Configuration

After updating `hugo.toml`:

1. Save the file
2. Restart `hugo server` if running
3. Check the footer at the bottom of any page
4. Test that all links work correctly
5. Verify social media icons appear and link properly

## Common Configurations

**Minimal Setup:**
```toml
[params.footer.social]
  linkedin = "https://linkedin.com/company/yourcompany"
```

**SaaS Product:**
```toml
[[params.footer.menus]]
  title = "Product"
  [[params.footer.menus.links]]
    name = "Features"
    url = "/features"
  [[params.footer.menus.links]]
    name = "Pricing"
    url = "/pricing"
    
[[params.footer.menus]]
  title = "Support"  
  [[params.footer.menus.links]]
    name = "Help Center"
    url = "/help"
  [[params.footer.menus.links]]
    name = "Contact"
    url = "/contact"
```

**Service Business:**
```toml
[[params.footer.menus]]
  title = "Services"
  [[params.footer.menus.links]]
    name = "Consulting"
    url = "/consulting"
  [[params.footer.menus.links]]
    name = "Implementation"
    url = "/implementation"
    
[[params.footer.menus]]
  title = "Company"
  [[params.footer.menus.links]]
    name = "About"
    url = "/about"
  [[params.footer.menus.links]]
    name = "Team"
    url = "/team"
```