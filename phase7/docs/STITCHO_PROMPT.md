# Google Sitcho Prompt for Frontend & UI Image Generation

## Overview

This prompt is designed to help Google Sitcho generate high-quality frontend and UI images for your Phase 7 restaurant recommendation system built with Next.js. The system uses modern React patterns, Tailwind CSS, and a component-based architecture.

## System Context

### Technology Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript with strict type safety
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Custom component library with Radix UI primitives
- **Icons**: Lucide React for consistent iconography
- **State Management**: Zustand with persistence middleware
- **Architecture**: Component-based, modular design
- **Color Scheme**: Modern, clean interface with semantic color usage

### Key Features
1. **Personalized Restaurant Recommendations**
2. **Vector Search & Semantic Matching**
3. **Hybrid Ranking System** (Rules + Vector + LLM)
4. **Multi-City Support**
5. **A/B Testing Framework**
6. **Advanced Analytics Dashboard**
7. **User Profile Management**
8. **Real-time Updates**

---

## 🎨 Design System

### Color Palette
- **Primary**: Blue gradient (`#3B82F6` to `#1E40AF`)
- **Secondary**: Gray tones (`#F3F4F6` to `#9CA3AF`)
- **Accent**: Emerald (`#10B981` to `#059669`)
- **Neutral**: Light grays (`#F9FAFB` to `#6B7280`)
- **Success**: Green (`#10B981` to `#059669`)
- **Warning**: Orange (`#F59E0B` to `#D97706`)
- **Error**: Red (`#EF4444` to `#DC2626`)

### Typography
- **Font Family**: Inter, system-ui, sans-serif
- **Headings**: Bold, 1.25rem - 2rem
- **Body**: Regular, 0.875rem - 1.125rem
- **Small**: 0.75rem
- **Caption**: 0.625rem

### Spacing
- **Scale**: 0.25rem (4px)
- **Components**: 0.5rem (8px), 1rem (16px), 1.5rem (24px), 2rem (32px)
- **Layout**: 1.5rem (24px), 2rem (32px), 3rem (48px), 4rem (64px)

### Border Radius
- **Small**: 0.25rem (4px)
- **Medium**: 0.5rem (8px)
- **Large**: 0.75rem (12px)
- **Full**: 1rem (16px)

---

## 🖼️ Component Library

### Core Components

#### Card Component
- Rounded corners with subtle shadow
- Header, title, and content sections
- Responsive design with hover states
- Loading and disabled states
- Multiple variants (default, elevated, outlined)

#### Button Component
- Multiple variants (primary, secondary, outline)
- Size options (small, medium, large)
- Loading states with spinner
- Icon support
- Focus states with ring effects

#### Badge Component
- Status indicators (default, secondary, outline)
- Color-coded for different states
- Small and compact variants

#### Input Components
- Text inputs with validation states
- Select dropdowns
- Textareas with auto-resize
- Checkbox and radio button groups

---

## 📱 Layout Components

### Header
- Navigation with logo and user menu
- Search bar with autocomplete
- City selector with location detection
- User profile dropdown

### Sidebar
- Navigation menu with active state indicators
- Experiment status display
- Quick action buttons
- Collapsible sections

### Main Layout
- Responsive grid system
- Container with max-width constraints
- Proper spacing and alignment
- Loading and error states

---

## 🎯 Key Pages & Features

### Dashboard Page
- Personalized welcome message
- Quick action cards
- Active experiments display
- Recommendation results with filtering
- Performance metrics overview

### Recommendations Page
- Advanced filtering and sorting
- Hybrid ranking display with strategy indicators
- Interactive restaurant cards with hover effects
- Map view integration
- Save and share functionality

### Profile Management
- Preference configuration with visual builders
- Behavior analytics and insights
- Recommendation history with interaction graphs
- Personalization settings

### Experiments Dashboard
- Active experiment management
- Real-time results monitoring
- Statistical significance indicators
- Traffic split visualization
- Rollback controls

### Analytics Dashboard
- User engagement metrics
- Recommendation performance analytics
- A/B test results visualization
- System health monitoring
- Custom report generation

---

## 🎨 Visual Style Guidelines

### Modern Design Principles
- **Clean Interface**: Minimalist design with ample whitespace
- **Consistent Spacing**: Use 8px grid system throughout
- **Smooth Animations**: Subtle transitions and micro-interactions
- **Accessibility**: WCAG 2.1 AA compliance with proper ARIA labels
- **Responsive**: Mobile-first approach with breakpoints at 768px, 1024px, 1280px
- **Dark Mode Support**: CSS variables for theme switching

### Interactive Elements
- **Hover States**: Smooth color transitions and scale effects
- **Focus States**: Clear focus indicators with outline rings
- **Loading States**: Skeleton screens and spinners
- **Empty States**: Helpful messages with call-to-action
- **Error States**: Clear error messages with recovery options

---

## 🖼️ Image Generation Guidelines

### Restaurant Cards
- **High-quality food photography** style
- **Consistent lighting** and composition
- **Cultural diversity** in food presentation
- **Brand-appropriate styling** for different restaurant types

### UI Elements
- **Clean, modern interface** with clear typography
- **Intuitive navigation** with visual hierarchy
- **Responsive layouts** that work on all devices
- **Loading states** with smooth animations
- **Error states** with helpful guidance

### Data Visualization
- **Clean charts and graphs** with consistent styling
- **Color-coded metrics** for easy interpretation
- **Interactive elements** with hover and click states
- **Mobile-optimized** visualizations

---

## 🔧 Technical Specifications

### Component Props
- **TypeScript interfaces** for all components
- **Consistent naming** conventions
- **JSDoc comments** for complex props
- **Default values** for optional props

### State Management
- **Zustand stores** with TypeScript support
- **Persistence middleware** for data persistence
- **Selectors** for optimized re-renders
- **Actions** for state mutations

### Performance Considerations
- **React.memo** for pure components
- **useCallback** and **useMemo** optimizations
- **Code splitting** for reduced bundle sizes
- **Image optimization** with Next.js Image component

---

## 📊 Example Use Cases

### Dashboard Visualization
```
Generate a modern dashboard interface showing:
- User engagement metrics with line charts and bar graphs
- Real-time recommendation performance indicators
- Active A/B test status with confidence intervals
- Clean card-based layout with responsive grid system
- Subtle animations and hover effects for interactive elements
```

### Recommendation Cards
```
Create restaurant recommendation cards featuring:
- High-quality food photography with consistent lighting
- Restaurant name, rating, and price information
- Distance indicators and map integration
- User preference matching indicators
- Clean, modern card design with hover effects
- Mobile-responsive layout with touch-friendly interactions
```

### Analytics Charts
```
Generate data visualization components including:
- Clean line charts with smooth curves
- Bar charts with color-coded categories
- Pie charts for distribution analysis
- Responsive design that works on mobile devices
- Interactive tooltips and legend
- Consistent color scheme matching the design system
```

---

## 🎯 Quality Standards

### Image Requirements
- **Resolution**: 72dpi for web, 144dpi for print
- **Format**: WebP with PNG fallback
- **Compression**: Optimized for fast loading
- **Aspect Ratios**: 16:9 for cards, 4:3 for hero images
- **Color Accuracy**: sRGB color space with proper calibration

### Code Standards
- **Semantic HTML5** with proper structure
- **ARIA labels** for accessibility
- **Keyboard navigation** support
- **Touch-friendly** interactions for mobile
- **Progressive enhancement** with graceful degradation

---

## 🚀 Performance Targets

### Loading Performance
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3.0s
- **Cumulative Layout Shift**: < 0.1

### Bundle Size
- **JavaScript**: < 100KB gzipped for initial load
- **CSS**: < 50KB gzipped
- **Images**: Optimized with lazy loading
- **Total Page Weight**: < 500KB for initial load

### Accessibility
- **WCAG 2.1 AA**: Full compliance
- **Keyboard Navigation**: Complete support
- **Screen Reader**: Compatible with NVDA, JAWS, VoiceOver
- **Color Contrast**: 4.5:1 minimum ratio

---

## 🔍 Testing Requirements

### Visual Testing
- **Cross-browser compatibility**: Chrome, Firefox, Safari, Edge
- **Responsive testing**: Mobile, tablet, desktop
- **Retina display** support for high-DPI screens
- **Dark mode** compatibility testing

### Functional Testing
- **Component interactions**: Click, hover, focus states
- **Form validation**: Error states and success feedback
- **Data persistence**: Local storage and IndexedDB
- **API integration**: Mock responses for testing

---

## 📝 Implementation Notes

### Next.js Integration
- Use `next/image` for optimized image loading
- Implement proper error boundaries and loading states
- Utilize App Router for client-side navigation
- Configure proper meta tags and SEO optimization

### State Management
- Implement proper TypeScript types for all stores
- Use Zustand persist middleware for data persistence
- Implement optimistic updates with rollback capability
- Add proper error handling and recovery mechanisms

### API Integration
- Implement proper error handling and retry logic
- Use React Query (SWR) for server state management
- Implement proper loading states and error boundaries
- Add request/response interceptors for debugging

---

## 🎨 Creative Direction

### Brand Personality
- **Modern & Clean**: Minimalist design with sophisticated typography
- **Approachable**: Friendly and professional appearance
- **Intelligent**: Smart interactions that anticipate user needs
- **Consistent**: Unified design language throughout

### Visual Hierarchy
- **Primary Actions**: Clear call-to-action buttons
- **Secondary Information**: Subtle supporting details
- **Navigation**: Clear information architecture
- **Feedback**: Immediate response to user interactions

This prompt provides Google Sitcho with comprehensive context about your Phase 7 restaurant recommendation system, enabling the generation of high-quality, consistent frontend and UI images that match your modern Next.js implementation.
