# Design Tokens

## Overview

Design tokens define the visual constants — colours, typography, spacing, shadows, and border radii — used across the Streamlit frontend. All CSS in `frontend/app.py` must reference these values directly. Changing a token here propagates the change consistently across the entire UI.

---

## Colour Palette

### Brand Colours

| Token | Hex | Usage |
|---|---|---|
| `--color-primary` | `#1E6FFF` | Primary buttons, active states, links |
| `--color-primary-hover` | `#1558CC` | Primary button hover state |
| `--color-primary-light` | `#E8F0FF` | Subtle background tints, selected states |

### Neutral Colours

| Token | Hex | Usage |
|---|---|---|
| `--color-bg-base` | `#FFFFFF` | Main page background |
| `--color-bg-surface` | `#F7F9FC` | Cards, panels, sidebar background |
| `--color-bg-elevated` | `#FFFFFF` | Source cards, modals |
| `--color-border` | `#E2E8F0` | Card borders, dividers, input borders |
| `--color-border-hover` | `#CBD5E1` | Border on hover |

### Text Colours

| Token | Hex | Usage |
|---|---|---|
| `--color-text-primary` | `#0F172A` | Main body text, headings |
| `--color-text-secondary` | `#475569` | Subtitles, captions, meta text |
| `--color-text-muted` | `#94A3B8` | Placeholders, disabled states |
| `--color-text-link` | `#1E6FFF` | Anchor links |
| `--color-text-link-hover` | `#1558CC` | Anchor link hover |

### Semantic Colours

| Token | Hex | Usage |
|---|---|---|
| `--color-success` | `#16A34A` | API online badge, success states |
| `--color-success-bg` | `#DCFCE7` | Success badge background |
| `--color-error` | `#DC2626` | API offline badge, error messages |
| `--color-error-bg` | `#FEE2E2` | Error badge background |
| `--color-warning` | `#D97706` | Warning messages |
| `--color-warning-bg` | `#FEF3C7` | Warning badge background |
| `--color-info` | `#0284C7` | Info messages, intent chips |
| `--color-info-bg` | `#E0F2FE` | Info badge background |

### Chat Colours

| Token | Hex | Usage |
|---|---|---|
| `--color-chat-user-bg` | `#EFF6FF` | User message bubble background |
| `--color-chat-assistant-bg` | `#F8FAFC` | Assistant message bubble background |
| `--color-chat-user-border` | `#BFDBFE` | User bubble left border accent |
| `--color-chat-assistant-border` | `#E2E8F0` | Assistant bubble left border accent |

---

## Typography

### Font Family

| Token | Value | Usage |
|---|---|---|
| `--font-sans` | `'Inter', 'Segoe UI', system-ui, sans-serif` | All UI text |
| `--font-mono` | `'JetBrains Mono', 'Fira Code', monospace` | Code blocks, chunk IDs |

> Streamlit loads its own system fonts. These tokens apply within injected HTML/CSS blocks.

### Font Sizes

| Token | Value | Usage |
|---|---|---|
| `--text-xs` | `11px` | Score labels, page numbers, timestamps |
| `--text-sm` | `13px` | Source card meta, captions, badges |
| `--text-base` | `15px` | Body text, chat messages |
| `--text-md` | `17px` | Source card titles |
| `--text-lg` | `20px` | Section headings |
| `--text-xl` | `24px` | Page subtitle |
| `--text-2xl` | `30px` | Page title |

### Font Weights

| Token | Value | Usage |
|---|---|---|
| `--font-normal` | `400` | Body text |
| `--font-medium` | `500` | Labels, captions |
| `--font-semibold` | `600` | Source card titles, section headers |
| `--font-bold` | `700` | Page title, strong emphasis |

### Line Heights

| Token | Value | Usage |
|---|---|---|
| `--leading-tight` | `1.25` | Headings |
| `--leading-normal` | `1.5` | Body text |
| `--leading-relaxed` | `1.75` | Long-form text in answers |

---

## Spacing Scale

All spacing values follow a base-4 scale.

| Token | Value | Usage |
|---|---|---|
| `--space-1` | `4px` | Icon-to-text gap, tight padding |
| `--space-2` | `8px` | Badge padding, compact elements |
| `--space-3` | `12px` | Input padding, small gaps |
| `--space-4` | `16px` | Card padding, standard gaps |
| `--space-5` | `20px` | Section spacing |
| `--space-6` | `24px` | Large card padding |
| `--space-8` | `32px` | Between major sections |
| `--space-10` | `40px` | Page-level vertical rhythm |

---

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `4px` | Badges, chips, small tags |
| `--radius-md` | `8px` | Source cards, input fields |
| `--radius-lg` | `12px` | Chat message bubbles |
| `--radius-xl` | `16px` | Large panels |
| `--radius-full` | `9999px` | Pill badges, avatar circles |

---

## Shadows

| Token | Value | Usage |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle card lift |
| `--shadow-md` | `0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04)` | Source cards |
| `--shadow-lg` | `0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04)` | Elevated panels |
| `--shadow-focus` | `0 0 0 3px rgba(30,111,255,0.25)` | Input/button focus ring |

---

## Component Specifications

### Source Card

```css
.source-card {
    background:    var(--color-bg-elevated);       /* #FFFFFF */
    border:        1px solid var(--color-border);  /* #E2E8F0 */
    border-radius: var(--radius-md);               /* 8px */
    padding:       var(--space-4);                 /* 16px */
    box-shadow:    var(--shadow-md);
    transition:    box-shadow 0.15s ease, border-color 0.15s ease;
}

.source-card:hover {
    box-shadow:    var(--shadow-lg);
    border-color:  var(--color-border-hover);      /* #CBD5E1 */
}

.source-title {
    font-size:     var(--text-md);                 /* 17px */
    font-weight:   var(--font-semibold);           /* 600 */
    color:         var(--color-text-primary);      /* #0F172A */
    margin-bottom: var(--space-1);                 /* 4px */
}

.source-meta {
    font-size:     var(--text-sm);                 /* 13px */
    font-weight:   var(--font-medium);             /* 500 */
    color:         var(--color-text-secondary);    /* #475569 */
    margin-bottom: var(--space-2);                 /* 8px */
}

.source-link {
    font-size:     var(--text-sm);                 /* 13px */
    font-weight:   var(--font-medium);             /* 500 */
    color:         var(--color-text-link);         /* #1E6FFF */
    text-decoration: none;
}

.source-link:hover {
    color:         var(--color-text-link-hover);   /* #1558CC */
    text-decoration: underline;
}
```

---

### API Status Badge

```css
.badge-online {
    display:       inline-flex;
    align-items:   center;
    gap:           var(--space-1);                 /* 4px */
    padding:       var(--space-1) var(--space-2);  /* 4px 8px */
    background:    var(--color-success-bg);        /* #DCFCE7 */
    color:         var(--color-success);           /* #16A34A */
    border-radius: var(--radius-full);             /* 9999px */
    font-size:     var(--text-xs);                 /* 11px */
    font-weight:   var(--font-semibold);           /* 600 */
}

.badge-offline {
    display:       inline-flex;
    align-items:   center;
    gap:           var(--space-1);
    padding:       var(--space-1) var(--space-2);
    background:    var(--color-error-bg);          /* #FEE2E2 */
    color:         var(--color-error);             /* #DC2626 */
    border-radius: var(--radius-full);
    font-size:     var(--text-xs);
    font-weight:   var(--font-semibold);
}
```

---

### Intent Chip

```css
.intent-chip {
    display:       inline-block;
    padding:       var(--space-1) var(--space-2);  /* 4px 8px */
    background:    var(--color-info-bg);           /* #E0F2FE */
    color:         var(--color-info);              /* #0284C7 */
    border-radius: var(--radius-sm);               /* 4px */
    font-size:     var(--text-xs);                 /* 11px */
    font-weight:   var(--font-medium);             /* 500 */
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
```

---

### Sidebar Title

```css
.sidebar-title h2 {
    font-size:     var(--text-lg);                 /* 20px */
    font-weight:   var(--font-bold);               /* 700 */
    color:         var(--color-text-primary);      /* #0F172A */
    margin-bottom: var(--space-1);                 /* 4px */
}

.sidebar-title p {
    font-size:     var(--text-sm);                 /* 13px */
    color:         var(--color-text-secondary);    /* #475569 */
    margin: 0;
}
```

---

## CSS Custom Properties — Full Declaration

Inject this block once at the top of the CSS string in `frontend/app.py`:

```css
:root {
    /* Brand */
    --color-primary:              #1E6FFF;
    --color-primary-hover:        #1558CC;
    --color-primary-light:        #E8F0FF;

    /* Neutrals */
    --color-bg-base:              #FFFFFF;
    --color-bg-surface:           #F7F9FC;
    --color-bg-elevated:          #FFFFFF;
    --color-border:               #E2E8F0;
    --color-border-hover:         #CBD5E1;

    /* Text */
    --color-text-primary:         #0F172A;
    --color-text-secondary:       #475569;
    --color-text-muted:           #94A3B8;
    --color-text-link:            #1E6FFF;
    --color-text-link-hover:      #1558CC;

    /* Semantic */
    --color-success:              #16A34A;
    --color-success-bg:           #DCFCE7;
    --color-error:                #DC2626;
    --color-error-bg:             #FEE2E2;
    --color-warning:              #D97706;
    --color-warning-bg:           #FEF3C7;
    --color-info:                 #0284C7;
    --color-info-bg:              #E0F2FE;

    /* Chat */
    --color-chat-user-bg:         #EFF6FF;
    --color-chat-assistant-bg:    #F8FAFC;
    --color-chat-user-border:     #BFDBFE;
    --color-chat-assistant-border:#E2E8F0;

    /* Typography */
    --font-sans:   'Inter', 'Segoe UI', system-ui, sans-serif;
    --font-mono:   'JetBrains Mono', 'Fira Code', monospace;
    --text-xs:     11px;
    --text-sm:     13px;
    --text-base:   15px;
    --text-md:     17px;
    --text-lg:     20px;
    --text-xl:     24px;
    --text-2xl:    30px;
    --font-normal:   400;
    --font-medium:   500;
    --font-semibold: 600;
    --font-bold:     700;
    --leading-tight:   1.25;
    --leading-normal:  1.5;
    --leading-relaxed: 1.75;

    /* Spacing */
    --space-1:  4px;
    --space-2:  8px;
    --space-3:  12px;
    --space-4:  16px;
    --space-5:  20px;
    --space-6:  24px;
    --space-8:  32px;
    --space-10: 40px;

    /* Border Radius */
    --radius-sm:   4px;
    --radius-md:   8px;
    --radius-lg:   12px;
    --radius-xl:   16px;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm:    0 1px 2px rgba(0,0,0,0.05);
    --shadow-md:    0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04);
    --shadow-lg:    0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
    --shadow-focus: 0 0 0 3px rgba(30,111,255,0.25);
}
```
