# Ansible Job Platform - Design System

基于 Apple/PaaS 风格的设计系统重构。

## Design Principles

### Core Principles
1. **Single Accent Color**: Only #0066cc (Action Blue) for interactive elements
2. **Photography-First**: UI recedes, content speaks
3. **Alternating Tiles**: Light → Dark → Light section rhythm
4. **Low Density**: Generous whitespace, 80px section padding
5. **One Shadow Rule**: Only product imagery gets shadows

### Typography Rules
- **Display**: SF Pro Display, 600 weight, negative letter-spacing
- **Body**: 17px (not 16px), 400 weight, 1.47 line-height
- **No weight 500**: 300 → 400 → 600 → 700 only

## Design Tokens

### Colors
```css
--color-primary: #0066cc;          /* Action Blue */
--color-primary-focus: #0071e3;    /* Focus Blue */
--color-ink: #1d1d1f;              /* Near-black text */
--color-canvas: #ffffff;           /* White background */
--color-canvas-parchment: #f5f5f7; /* Off-white */
--color-surface-tile-1: #272729;   /* Dark tile */
```

### Border Radius
```css
--rounded-sm: 8px;     /* Utility buttons */
--rounded-lg: 18px;    /* Cards */
--rounded-pill: 9999px;/* Primary CTAs */
```

## Key Components

### Product Tile - Light
- White background
- Large centered typography
- 80px vertical padding
- Two blue pill buttons
- No shadows

### Product Tile - Dark
- Dark near-black (#272729)
- White text
- Blue links (Sky Link Blue #2997ff)

### Buttons
- **Primary Pill**: Blue background, pill shape
- **Secondary Pill**: Ghost, blue border, pill shape
- **Dark Utility**: Dark background, 8px radius, compact

### Cards
- 18px radius
- 1px hairline border
- No shadow by default

## Page Structure

### Login Page
1. Dark Hero Tile: Title + Tagline
2. Light Form Tile: Sign in form

### Dashboard
1. Dark Hero Tile: Welcome + CTAs
2. Light Stats Tile: Statistics grid
3. Parchment Actions Tile: Quick actions

## Micro-Interactions

- **Button Active**: `transform: scale(0.95)`
- **Button Hover**: `transform: scale(1.02)`
- **Card Hover**: Lift slightly (optional)

## Responsive Breakpoints

- 1440px: Content lock
- 1068px: Small desktop
- 833px: Tablet landscape
- 734px: Tablet portrait
- 640px: Phone
- 419px: Small phone
