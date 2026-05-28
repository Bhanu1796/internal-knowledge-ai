# Design Tokens

## Overview

Design tokens define the visual constants — colours, typography, spacing, shadows, and border radii — used across the Streamlit frontend. All CSS in `frontend/app.py` must reference these values directly.

> **Theme:** Dark — AI-native dark theme with purple/violet primary accent and aurora background glow.

---

## Colour Palette

### Background

| Token | Hex | Usage |
|---|---|---|
| `--color-bg-base` | `#070712` | App background (near-black, slight purple tint) |
| `--color-bg-sidebar` | `#0D0D1C` | Sidebar background |
| `--color-bg-surface` | `rgba(255,255,255,0.025)` | Cards, expanders |
| `--color-bg-surface-hover` | `rgba(255,255,255,0.04)` | Card hover state |
| `--color-bg-input` | `rgba(255,255,255,0.035)` | Chat input, form fields |

### Brand / Accent

| Token | Hex | Usage |
|---|---|---|
| `--color-primary` | `#7C3AED` | Primary accent — violet |
| `--color-primary-dim` | `rgba(124,58,237,0.12)` | Tinted backgrounds |
| `--color-primary-border` | `rgba(124,58,237,0.28)` | Tinted borders |
| `--color-secondary` | `#4F46E5` | Secondary gradient stop — indigo |
| `--color-glow` | `rgba(109,40,217,0.22)` | Aurora radial glow |

### Text

| Token | Hex | Usage |
|---|---|---|
| `--color-text-primary` | `#F1F5F9` | Main body text, headings |
| `--color-text-secondary` | `#94A3B8` | Subtitles, sidebar labels |
| `--color-text-muted` | `#64748B` | Captions, meta, disabled |
| `--color-text-faint` | `#475569` | Timestamps, doc labels |
| `--color-text-accent` | `#A78BFA` | Intent chips, entity pills |

### Borders

| Token | Value | Usage |
|---|---|---|
| `--color-border` | `rgba(255,255,255,0.07)` | Card and panel borders |
| `--color-border-active` | `rgba(124,58,237,0.45)` | Focus / active states |
| `--color-border-sidebar` | `rgba(255,255,255,0.05)` | Sidebar dividers |

### Semantic

| Token | Hex | Usage |
|---|---|---|
| `--color-success` | `#34D399` | API online dot |
| `--color-success-glow` | `rgba(52,211,153,0.7)` | API dot box-shadow |
| `--color-error` | `#F87171` | API offline dot, errors |

### Intent Chip Colours

| Intent | Background | Text | Border |
|--------|-----------|------|--------|
| POLICY_LOOKUP | `rgba(139,92,246,0.14)` | `#A78BFA` | `rgba(139,92,246,0.28)` |
| PROCESS_INQUIRY | `rgba(6,182,212,0.11)` | `#67E8F9` | `rgba(6,182,212,0.24)` |
| CONTACT_LOOKUP | `rgba(52,211,153,0.11)` | `#6EE7B7` | `rgba(52,211,153,0.24)` |
| GENERAL_INFO | `rgba(251,191,36,0.11)` | `#FCD34D` | `rgba(251,191,36,0.24)` |
| UNKNOWN | `rgba(100,116,139,0.11)` | `#94A3B8` | `rgba(100,116,139,0.22)` |

---

## Typography

### Font Family

| Token | Value |
|---|---|
| `--font-sans` | `'Inter', system-ui, -apple-system, sans-serif` |

### Font Sizes

| Token | Value | Usage |
|---|---|---|
| `--text-2xs` | `10px` | Section labels, uppercase headers |
| `--text-xs` | `11px` | Source meta, timestamps, badges |
| `--text-sm` | `12.5px` | Doc items, button labels |
| `--text-base` | `13px` | Source card titles, chat body |
| `--text-md` | `0.92rem` | Chat input |
| `--text-lg` | `1.05rem` | Page header title |
| `--text-xl` | `1.55rem` | Welcome title |

### Font Weights

| Token | Value | Usage |
|---|---|---|
| `--font-normal` | `400` | Body text, example pill labels |
| `--font-medium` | `500` | Status pill, button labels |
| `--font-semibold` | `600` | Source card titles |
| `--font-bold` | `700` | Page title, stat numbers, sidebar logo |
| `--font-extrabold` | `800` | Welcome title |

---

## Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `--space-1` | `4px` | Icon gap, tight padding |
| `--space-2` | `7–8px` | Doc item padding, chip padding |
| `--space-3` | `10–12px` | Stat card, source card padding |
| `--space-4` | `14–16px` | Card padding, standard gaps |
| `--space-5` | `18–20px` | Section spacing |
| `--space-6` | `22px` | Welcome icon margin |
| `--space-8` | `34px` | Welcome sub margin-bottom |

---

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `5–6px` | Score badges, entity pills |
| `--radius-md` | `7–8px` | Buttons, doc items, sidebar expanders |
| `--radius-lg` | `10px` | Source cards |
| `--radius-xl` | `14px` | Chat input, page header icon |
| `--radius-2xl` | `22px` | Welcome glow icon |
| `--radius-full` | `20px` | Status pills, sidebar logo |

---

## Shadows & Glows

| Token | Value | Usage |
|---|---|---|
| `--shadow-header-icon` | `0 4px 16px rgba(124,58,237,0.4)` | Page header icon |
| `--shadow-send-btn` | `0 2px 12px rgba(124,58,237,0.45)` | Chat send button |
| `--shadow-welcome-glow` | `0 0 50px rgba(124,58,237,0.14)` | Welcome icon ambient |
| `--shadow-focus-ring` | `0 0 0 3px rgba(124,58,237,0.07)` | Input focus ring |
| `--glow-status-online` | `0 0 7px rgba(52,211,153,0.7)` | API online dot |

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
