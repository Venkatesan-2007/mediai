# Medi AI - Complete Project Structure Guide

## Quick Navigation

This guide helps you understand and navigate the **Medi AI** medical learning platform codebase.

- **Theme:** Pink & White 🎨
- **Framework:** React 18 with Tailwind CSS
- **Architecture:** Feature-Based Components
- **State Management:** React Context + Custom Hooks

---

## Project Tree Overview

```
medi-ai/
├── public/                              # Static assets
│   ├── index.html
│   └── manifest.json
│
├── src/                                 # Source code
│   ├── features/                        # ⭐ Feature modules (MAIN CODE)
│   │   ├── auth/                        # Login & Authentication
│   │   ├── books/                       # Medical books/resources
│   │   ├── chat/                        # AI chat interface
│   │   ├── dashboard/                   # Student dashboard (DOCUMENTED)
│   │   ├── questionBuilder/             # AI question generator
│   │   ├── README.md                    # Features overview
│   │   └── STRUCTURE.md                 # Feature architecture guide
│   │
│   ├── shared/                          # 🔑 Shared code (ALL FEATURES USE)
│   │   ├── components/                  # Global reusable components
│   │   │   └── Navbar.jsx               # Navigation bar
│   │   │
│   │   ├── contexts/                    # React Context
│   │   │   └── AuthContext.jsx          # Authentication state
│   │   │
│   │   ├── services/                    # API services
│   │   │   └── authService.js           # Auth API calls
│   │   │
│   │   └── styles/                      # Global styles
│   │       ├── Chat.css
│   │       └── Login.css
│   │
│   ├── App.js                           # Main app component (routing)
│   ├── App.css                          # App-level styles
│   ├── index.js                         # React entry point
│   └── index.css                        # Global Tailwind imports
│
├── docker-compose.yml                   # Docker container setup
├── Dockerfile                           # Docker image config
├── package.json                         # NPM dependencies
├── tailwind.config.js                   # Tailwind CSS configuration
├── postcss.config.js                    # PostCSS configuration
└── README.md                            # Project README
```

---

## 📁 Detailed Structure

### `/src/features/` - Feature Modules

Each feature is **self-contained** with its own structure:

#### Dashboard Feature (Fully Documented)
```
dashboard/
├── README.md                    # 📖 Complete feature documentation
├── pages/
│   └── Dashboard.jsx            # Main dashboard page
├── components/
│   ├── DashboardCards.jsx       # 4 metric cards (Progress, Q's, Exams, Streak)
│   ├── ProgressChart.jsx        # Chart visualizations
│   └── RecommendationSection.jsx # Recommendations & high-yield topics
├── constants/
│   └── dashboardConstants.js    # All constants, default values, colors
├── hooks/
│   └── useDashboardData.js      # Custom hook for data fetching
├── utils/
│   └── dashboardUtils.js        # Utility functions (format, calculate, etc.)
└── config/
    └── dashboardConfig.js       # Feature settings & configuration
```

#### Auth Feature
```
auth/
├── pages/
│   └── Login.jsx                # Login page
└── components/
    └── (Auth related components)
```

#### Books Feature
```
books/
├── pages/
│   └── Booklist.jsx             # Books list page
└── components/
    ├── BookCard.jsx             # Individual book card
    ├── BookDetailView.jsx       # Book detail view
    ├── FilterPanel.jsx          # Filter options
    └── SearchBar.jsx            # Search functionality
```

#### Chat Feature
```
chat/
├── pages/
│   └── Chat.jsx                 # Chat interface
└── components/
    └── MessageBubble.jsx        # Message component
```

#### Question Builder Feature
```
questionBuilder/
├── pages/
│   └── QuestionBuilder.jsx      # Question builder page
└── components/
    └── (Builder components)
```

### `/src/shared/` - Shared Resources

Code and components used across **all features**:

```
shared/
├── components/
│   └── Navbar.jsx               # Navigation bar (all pages)
├── contexts/
│   └── AuthContext.jsx          # Global auth state
├── services/
│   └── authService.js           # API calls for auth
└── styles/
    ├── Chat.css                 # Chat feature styles
    └── Login.css                # Login feature styles
```

### `/src/` - Core Files

```
App.js                           # Main component, routing setup
App.css                          # App-level styles
App.test.js                      # App tests
index.js                         # React DOM render
index.css                        # Global Tailwind, fonts, animations
reportWebVitals.js               # Performance reporting
setupTests.js                    # Test setup
```

---

## 🎨 Color Theme: Pink & White

### Color Palette Reference

```javascript
// Tailwind CSS Colors
{
  pink-50: '#fdf2f8'     // Extremely light pink background
  pink-100: '#fce7f3'    // Very light pink (secondary background)
  pink-200: '#fbcfe8'    # Light pink borders
  pink-300: '#f9a8d4'    # Light pink
  pink-400: '#f472b6'    # Medium light pink (gradients)
  pink-500: '#ec4899'    # PRIMARY PINK (main accent)
  pink-600: '#db2777'    # Medium pink (hover, emphasis)
  pink-700: '#be185d'    # Dark pink (dark mode)
  
  white: '#ffffff'       # Card backgrounds, text
  gray-500: '#6b7280'    # Secondary text
  gray-600: '#4b5563'    # Primary text
}
```

### Usage Examples

**Buttons:**
```jsx
// Primary button
<button className="bg-pink-600 hover:bg-pink-700">Click me</button>

// Gradient button
<button className="bg-gradient-to-r from-pink-400 to-pink-600">Action</button>
```

**Cards:**
```jsx
// Card with pink border
<div className="bg-white border border-pink-100 rounded-xl p-4 shadow-soft">
  Content
</div>
```

**Text:**
```jsx
// Emphasized pink text
<p className="text-pink-600 font-semibold">Important</p>

// Gradient text
<h1 className="text-gradient">Medi AI</h1>
```

**Backgrounds:**
```jsx
// Light pink backgrounds
<div className="bg-pink-50 rounded-lg">Light content</div>

// Page background
<div className="bg-gradient-pink">Page content</div>
```

---

## 📋 Feature Structure Pattern

Each feature follows this **consistent pattern**:

### Folder Organization
```
feature-name/
├── pages/              # Page components (entry points)
├── components/         # UI subcomponents
├── constants/          # Constants, default values, colors
├── hooks/              # Custom React hooks
├── utils/              # Helper functions
├── config/             # Feature configuration
├── styles/             # Feature-specific CSS (optional)
└── README.md           # Feature documentation
```

### File Naming Conventions
- **Components:** PascalCase (e.g., `DashboardCards.jsx`)
- **Utilities:** camelCase (e.g., `dashboardUtils.js`)
- **Constants:** CONSTANT_CASE for exports
- **Hooks:** Start with `use` (e.g., `useDashboardData.js`)

---

## 🔄 Data Flow Example

### Dashboard Components Communication

```
Dashboard.jsx
    ↓ Uses Hook
useDashboardData(token)
    ├─ Fetches from API
    ├─ Transforms with dashboardUtils
    └─ Returns { data, loading, error }
    
    ↓ Passes props to child components
DashboardCards
    ├─ Uses dashboardConstants
    └─ Displays metrics with pink theme

ProgressChart
    ├─ Uses dashboardConstants for colors
    └─ Visualizes data with pink gradients

RecommendationSection
    ├─ Uses HIGH_YIELD_TOPICS constant
    ├─ Displays with pink accents
    └─ Interactive with pink hover states
```

---

## 🔗 Import Patterns

### Import Shared Components
```javascript
import Navbar from '../../shared/components/Navbar';
import { useAuth } from '../../shared/contexts/AuthContext';
```

### Import Feature Resources
```javascript
// From same feature
import DashboardCards from '../components/DashboardCards';
import { DASHBOARD_COLORS } from '../constants/dashboardConstants';
import { useDashboardData } from '../hooks/useDashboardData';
import { formatDate } from '../utils/dashboardUtils';
```

### Import Utilities
```javascript
// Utility functions
import { calculateProgress } from '../utils/dashboardUtils';

// Constants
import { DEFAULT_DASHBOARD_DATA } from '../constants/dashboardConstants';
```

---

## 📚 Component Examples

### Feature Component (Dashboard.jsx)
```jsx
import Navbar from '../../../shared/components/Navbar';
import DashboardCards from '../components/DashboardCards';
import { useDashboardData } from '../hooks/useDashboardData';

const Dashboard = () => {
  const { studentData, loading } = useDashboardData(token);
  
  return (
    <div className="bg-gradient-pink">
      <Navbar />
      <DashboardCards {...dashboardProps} />
    </div>
  );
};
```

### Sub-Component (DashboardCards.jsx)
```jsx
import React from 'react';

const DashboardCards = ({ progress, questionsToday, upcomingExams }) => {
  return (
    <div className="grid grid-cols-4 gap-4">
      <div className="card-soft bg-white">
        <div className="bg-gradient-to-br from-pink-400 to-pink-600">
          {/* Content */}
        </div>
      </div>
    </div>
  );
};

export default DashboardCards;
```

### Utility Function (dashboardUtils.js)
```javascript
/**
 * Calculate progress percentage
 * @param {number} current - Current value
 * @param {number} total - Total value
 * @returns {number} Progress percentage
 */
export const calculateProgress = (current, total) => {
  if (total === 0) return 0;
  return Math.round((current / total) * 100);
};
```

---

## 🎯 Common Tasks

### Task: Add New Component to Dashboard
1. Create file: `src/features/dashboard/components/NewComponent.jsx`
2. Add to `Dashboard.jsx` as child component
3. Pass props from parent
4. Use pink/white theme

### Task: Add Dashboard Constant
1. Open `src/features/dashboard/constants/dashboardConstants.js`
2. Add your constant object
3. Export it
4. Import where needed

### Task: Add Utility Function
1. Open `src/features/dashboard/utils/dashboardUtils.js`
2. Write function with JSDoc
3. Export it
4. Import and use in components

### Task: Change Color Scheme
1. Update `DASHBOARD_COLORS` in constants
2. Update Tailwind classes in components
3. Ensure consistency across feature

### Task: Create New Feature
1. Create folder: `src/features/new-feature/`
2. Create subfolders: `pages/`, `components/`, `constants/`, `hooks/`, `utils/`
3. Create `README.md` with documentation
4. Add route to `App.js`
5. Follow pink/white color scheme

---

## 🔌 API Integration Points

The app connects to backend at: `http://localhost:8000/api/`

### Dashboard Endpoints
```
GET /api/user-stats          # User progress, statistics
```

### Auth Endpoints
```
POST /api/login              # User login
POST /api/logout             # User logout
```

### Data passed to API
```javascript
// Authorization header for all requests
Authorization: `Bearer ${token}`
```

---

## 🎨 Tailwind CSS Configuration

Located in `tailwind.config.js`:

### Custom Colors
```javascript
colors: {
  pink: { /* pink color spectrum */ },
  primary: '#ec4899',    // Main pink
  secondary: '#fce7f3',  // Light pink
}
```

### Custom Classes
```css
.card-soft            /* White card with pink border */
.btn-primary          /* Pink gradient button */
.text-gradient        /* Pink gradient text */
.bg-gradient-pink     /* Light pink page background */
```

### Box Shadows
```css
shadow-soft           /* Pink-tinted soft shadow */
shadow-card           /* Card shadow */
shadow-glass          /* Glass effect shadow */
```

---

## 📖 Documentation Files

Find detailed docs here:

1. **Features Overview:** `src/features/README.md`
2. **Dashboard Details:** `src/features/dashboard/README.md`
3. **Project Structure:** This file

---

## 🚀 Running the Project

### Install Dependencies
```bash
cd frontend/medi-ai
npm install
```

### Start Development Server
```bash
npm start
```
Runs on `http://localhost:3000`

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
npm test
```

---

## 📦 Key Dependencies

```json
{
  "react": "^18.2.0",           // UI library
  "react-router-dom": "^6.x",   // Routing
  "axios": "^1.x",               // HTTP requests
  "tailwindcss": "^3.x"          // CSS framework
}
```

---

## ✅ Best Practices Checklist

When working on this codebase:

- ✅ Keep features self-contained
- ✅ Use shared components from `shared/` folder
- ✅ Store constants in `constants/` folder
- ✅ Use custom hooks for data fetching
- ✅ Add JSDoc comments to functions
- ✅ Follow pink/white color scheme
- ✅ Update relevant README files
- ✅ Test changes before committing
- ✅ Use feature-based folder structure
- ✅ Keep imports relative within feature

---

## 🤝 Sharing Code Guide

To help others understand your code:

1. **Document in README.md** - Add feature explanation
2. **Use JSDoc comments** - Document all functions
3. **Name things clearly** - Use descriptive names
4. **Follow structure** - Use consistent folder layout
5. **Color consistently** - Use pink/white theme
6. **Provide examples** - Show usage in comments
7. **Add constants** - Keep magic numbers out
8. **Use custom hooks** - Encapsulate logic

---

## 📞 Quick Reference

| Task | Location |
|------|----------|
| Change colors | `constants/dashboardConstants.js` |
| Add API endpoint | Import from `shared/services/` |
| Create hook | `features/feature-name/hooks/` |
| Add utility | `features/feature-name/utils/` |
| Global style | `src/index.css` |
| Global component | `shared/components/` |
| Feature documentation | `features/feature-name/README.md` |
| Update routes | `src/App.js` |

---

## 📝 Git Commit Examples

```bash
# Feature implementation
[dashboard] Add color theme updates
- Updated DashboardCards to pink/white
- Changed ProgressChart colors
- Updated RecommendationSection styling

# Bug fix
[auth] Fix login error handling
- Added proper error messages
- Improved loading state

# Documentation
[docs] Add dashboard structure guide
- Created comprehensive README
- Added code examples
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Colors not showing | Check Tailwind CSS imports in `index.css` |
| Component not found | Verify import path and export in component file |
| API fails | Check backend running on `localhost:8000` |
| Styles conflict | Use Tailwind's `@apply` or increase specificity |
| Hook error | Ensure hook is used inside React component |

---

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [JavaScript Features Guide](./FEATURES.md)
- Feature-specific READMEs in each feature folder

---

**Last Updated:** April 2026  
**Framework:** React 18 with Tailwind CSS  
**Architecture:** Feature-Based Components  
**Color Theme:** Pink & White 🎨

For detailed information about specific features, see `src/features/README.md` or individual feature README files.
