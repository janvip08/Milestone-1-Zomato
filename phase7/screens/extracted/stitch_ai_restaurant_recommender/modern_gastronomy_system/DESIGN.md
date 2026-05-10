---
name: Modern Gastronomy System
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#5b403f'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#7f5608'
  on-secondary: '#ffffff'
  secondary-container: '#fdc571'
  on-secondary-container: '#785000'
  tertiary: '#5d5c5b'
  on-tertiary: '#ffffff'
  tertiary-container: '#757474'
  on-tertiary-container: '#fffcfb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffddb1'
  secondary-fixed-dim: '#f4bd6a'
  on-secondary-fixed: '#291800'
  on-secondary-fixed-variant: '#614000'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1b1b1b'
  on-tertiary-fixed-variant: '#474746'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  headline-xl:
    fontFamily: lexend
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: lexend
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: lexend
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 30px
  title-md:
    fontFamily: lexend
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: lexend
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: lexend
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: lexend
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  ai-recommendation:
    fontFamily: lexend
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1200px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 24px
---

## Brand & Style

The design system centers on a high-energy, food-first philosophy. It is designed to evoke appetite and reliability through a sophisticated blend of **Minimalism** and **Corporate Modern** aesthetics. The primary goal is to let high-quality food photography lead the user experience, supported by a clean, functional interface that reduces cognitive load during discovery.

To distinguish the "AI Recommendation" capabilities, the system introduces a "Magical Utility" layer. This utilizes subtle, iridescent gradients and ethereal iconography (sparkles) to denote machine-learning-driven insights, ensuring these features feel premium and distinct from standard search results without breaking the core visual harmony.

## Colors

The color palette is anchored by the iconic **Zomato Red (#E23744)**, used strategically for primary actions, branding, and highlighting essential "hunger-driven" touchpoints. 

- **Primary Red:** Reserved for high-priority CTAs and brand markers.
- **Secondary Gold:** Utilized for "Gold" tier memberships, high ratings, and as a highlight color within AI-driven recommendations.
- **Neutrals:** A deep charcoal (#1C1C1C) provides high-legibility for typography, while an off-white neutral background prevents screen fatigue.
- **AI Accents:** Intelligence-based features use a custom gradient that blends the brand red with a lighter rose and the secondary gold, creating a "shimmer" effect that signifies curated content.

## Typography

The design system utilizes **Lexend** across all levels to ensure maximum readability and a friendly, accessible character. The type scale is optimized for information density:

- **Headlines:** Use tighter letter-spacing and bold weights to create a strong visual anchor for restaurant names and section headers.
- **Body Text:** Maintains a generous line height to ensure descriptions and reviews remain legible even at smaller sizes.
- **Information Hierarchy:** Crucial data points like ratings, delivery times, and price-for-two use medium weights to stand out against descriptive text.
- **AI Styling:** Text specifically generated or curated by AI features uses the `ai-recommendation` style, occasionally paired with a subtle color tint to indicate its unique source.

## Layout & Spacing

This design system employs a **Fixed Grid** model for desktop and a **Fluid Grid** for mobile devices. 

- **Desktop:** A 12-column grid centered in a 1200px container. Large gutters of 16px provide enough "breathing room" for dense card layouts.
- **Mobile:** A 4-column fluid grid with 16px side margins. 
- **Spacing Rhythm:** Based on an 8px square grid. Vertical rhythm is strictly enforced to maintain the "clean" feel, with 24px (md) spacing between distinct content blocks.
- **Card Spacing:** Horizontal scrolling sections (common for "Cuisines" or "Quick Filters") use 12px (sm) spacing between items to encourage discovery.

## Elevation & Depth

Visual hierarchy is established through **Ambient Shadows** and **Tonal Layers**. 

- **Base Level (0dp):** The main background uses the neutral off-white.
- **Card Level (1dp):** Restaurant and dish cards feature a very soft, diffused shadow (0px 4px 12px rgba(0,0,0,0.05)) to lift them slightly off the background, making imagery feel touchable.
- **Interactive Level (2dp):** On hover or active state, cards lift further with a more pronounced shadow to provide tactile feedback.
- **AI Elevation:** AI-specific panels or "Smart Tips" use a faint inner glow or a 1px border using the AI gradient rather than a traditional shadow, signaling that these elements exist on a "digital intelligence" plane.

## Shapes

The shape language is approachable and modern, utilizing **Rounded (0.5rem)** corners as the standard.

- **Standard Cards:** 1rem (rounded-lg) for the main container to feel friendly and safe.
- **Buttons & Inputs:** 0.5rem (base) for a structured, professional appearance.
- **Images:** Always follow the container's corner radius. Imagery should never have sharp corners.
- **AI Elements:** AI chips and "Magic" buttons use the **Pill-shaped (3)** setting to differentiate them from standard rectangular UI components.

## Components

### Buttons
- **Primary:** Solid Red (#E23744) with white text. High-contrast, bold weight.
- **Secondary:** White background with a 1px charcoal border.
- **AI Action:** Gradient background (AI Gradient) with white text and a leading "sparkle" icon.

### Cards
The core of the design system. Cards must have a fixed aspect ratio for images (usually 4:3 or 16:9). Information hierarchy within the card:
1. **Image:** Full-width top section.
2. **Title:** Headline-sm, left-aligned.
3. **Badge:** Ratings use the Secondary Gold background with a star icon.
4. **Metadata:** Small labels for distance and pricing.

### AI Recommendations
A specific "Magic Strip" component. This is a horizontally scrolling list of cards with a subtle gradient border and a "Generated for you" label in the `ai-recommendation` type style.

### Input Fields
Clean, white backgrounds with 1px light gray borders. On focus, the border transitions to Primary Red. The "AI Search" variant includes a subtle shimmer effect in the placeholder text.

### Chips/Filters
Small, rounded-pill shapes. Inactive: gray background; Active: Red background or Red border. AI-curated filters feature a small sparkle icon suffix.