# Medi AI Features - Complete Documentation

## Overview

This document provides a comprehensive guide to the **Medi AI** application's feature-based architecture. The application is organized by features for better code organization, maintainability, and scalability.

## Project Structure

```
src/
├── features/                          # Feature-based modules
│   ├── auth/                          # Authentication & Login
│   ├── books/                         # Book/Resource Management
│   ├── chat/                          # AI Chat Interface
│   ├── dashboard/                     # Student Dashboard
│   └── questionBuilder/               # AI Question Builder
├── shared/                            # Shared components & utilities
│   ├── components/                    # Reusable components (Navbar, etc.)
│   ├── contexts/                      # React Context (AuthContext)
│   ├── services/                      # API services
│   └── styles/                        # Global styles
├── App.js                             # Main App component
├── index.js                           # Entry point
└── index.css                          # Global styles
```

## Color Theme: Pink & White

The entire application uses a cohesive **pink and white color scheme** for a modern, clean aesthetic.

### Color Palette

| Color | Hex Code | Tailwind Class | Usage |
|-------|----------|---|---|
| Primary Pink | `#ec4899` | `pink-500` | Buttons, links, highlights |
| Dark Pink | `#db2777` | `pink-600` | Hover states, emphasis |
| Light Pink | `#f472b6` | `pink-400` | Gradients, secondary |
| Very Light Pink | `#fce7f3` | `pink-100` | Backgrounds, subtle |
| White | `#ffffff` | `white` | Card backgrounds |
| Gray | `#6b7280` | `gray-500` | Text, descriptions |

### Gradient Examples
- `from-pink-400 to-pink-600` - Button gradients
- `from-pink-500 to-pink-700` - Feature highlights
- `bg-gradient-pink` - Page backgrounds (light pink gradient)

## Feature Breakdown

### 1. Dashboard Feature (`src/features/dashboard/`)

**Purpose:** Student dashboard with progress tracking and analytics

**Key Components:**
- `Dashboard.jsx` - Main page
- `DashboardCards.jsx` - Key metrics (Progress, Questions, Exams, Streak)
- `ProgressChart.jsx` - Visual progress and weekly activity
- `RecommendationSection.jsx` - Study recommendations

**Folder Structure:**
- `pages/` - Page components
- `components/` - Reusable dashboard components
- `constants/` - Dashboard constants
- `hooks/` - Custom hooks (`useDashboardData`)
- `utils/` - Utility functions
- `config/` - Feature configuration
- `styles/` - Dashboard-specific styles
- `README.md` - Detailed documentation

**Key Files:**
- `constants/dashboardConstants.js` - API endpoints, default data, colors
- `hooks/useDashboardData.js` - Data fetching hook
- `utils/dashboardUtils.js` - Helper functions
- `config/dashboardConfig.js` - Feature settings

**Color Implementation:**
All colors are consistently pink/white across:
- Card backgrounds: White with pink borders
- Buttons: Pink gradients
- Text: Pink for emphasis, gray for secondary
- Charts: Pink gradients for progress visualization

[See Dashboard README for details](./dashboard/README.md)

### 2. Authentication Feature (`src/features/auth/`)

**Purpose:** User login and authentication

**Key Components:**
- `Login.jsx` - Login page

**Current Structure:**
- `pages/` - Authentication pages
- `components/` - Auth-related components
- `contexts/` - Auth context (in shared)
- `services/` - Auth services (in shared)

**Color Scheme:**
- Background: Light pink gradient
- Buttons: Pink gradient
- Input fields: Pink border focus states
- Text: Gray body, pink headers

### 3. Books Feature (`src/features/books/`)

**Purpose:** Medical book/resource browsing and filtering

**Key Components:**
- `Booklist.jsx` - List of books
- `BookCard.jsx` - Individual book card
- `BookDetailView.jsx` - Book details
- `FilterPanel.jsx` - Filtering options
- `SearchBar.jsx` - Search functionality

**Color Scheme:**
- Cards: White with pink borders
- Buttons: Pink gradients for interactions
- Tags: Pink backgrounds for categorization
- Hover states: Light pink backgrounds

### 4. Chat Feature (`src/features/chat/`)

**Purpose:** AI chat interface for medical questions

**Key Components:**
- `Chat.jsx` - Chat interface
- `MessageBubble.jsx` - Message component

**Color Scheme:**
- User messages: Pink gradient backgrounds
- AI messages: White with pink borders
- Chat container: Light pink background
- Input field: Pink border focus

### 5. Question Builder Feature (`src/features/questionBuilder/`)

**Purpose:** AI-powered question generation

**Key Components:**
- `QuestionBuilder.jsx` - Question builder interface

**Color Scheme:**
- Buttons: Pink gradients
- Input fields: Pink borders
- Generated questions: Pink highlight
- Submit button: Dark pink gradient

## Shared Resources (`src/shared/`)

### Components
- **Navbar.jsx** - Navigation bar (pink logo, pink active states)
- Custom components used across features

### Contexts
- **AuthContext.jsx** - Global authentication state

### Services
- **authService.js** - Authentication API calls

### Styles
- **Chat.css** - Chat feature styles
- **Login.css** - Login feature styles
- **Global CSS** - Shared styles

## Feature Architecture Pattern

Each feature follows this structure:

```
feature-name/
├── pages/              # Page components (usually one)
├── components/         # Reusable components within feature
├── constants/          # Constants & config values
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── config/             # Feature configuration
├── styles/             # Feature-specific CSS
└── README.md           # Feature documentation
```

### Best Practices

1. **Keep Features Independent**: Each feature should be self-contained
2. **Use Constants**: Define all constants in `constants/` folder
3. **Custom Hooks**: Use custom hooks in `hooks/` for data fetching
4. **Utilities**: Keep utility functions in `utils/` folder
5. **Consistent Colors**: Always use the pink/white theme
6. **Documentation**: Create README.md in each feature
7. **Props & Types**: Document component props with JSDoc

## Component Communication

```
App.jsx
    ↓ Routes
├─→ Dashboard ─→ DashboardCards
│              ├─→ ProgressChart
│              └─→ RecommendationSection
│
├─→ Login (Auth)
│
├─→ Booklist (Books)
│   ├─→ SearchBar
│   ├─→ FilterPanel
│   ├─→ BookCard
│   └─→ BookDetailView
│
├─→ Chat
│   └─→ MessageBubble
│
├─→ QuestionBuilder
│
└─→ Navbar (Shared - renders on all pages)
```

## API Integration

**Base URL:** `http://localhost:8000/api/`

### Endpoints by Feature

**Dashboard:**
- `GET /api/user-stats` - User statistics and progress

**Auth:**
- `POST /api/login` - User login
- `POST /api/logout` - User logout

**Books:**
- `GET /api/books` - List of books
- `GET /api/books/:id` - Book details

**Chat:**
- `POST /api/chat` - Send message to AI
- `GET /api/chat/history` - Chat history

**Questions:**
- `POST /api/questions/generate` - Generate questions

## Styling Approach

### Tailwind CSS Utility-First

The project uses **Tailwind CSS** with custom configuration:

**Custom Classes:**
- `.card-soft` - White card with pink border
- `.btn-primary` - Pink gradient button
- `.btn-secondary` - White button with pink border
- `.input-field` - Input with pink focus
- `.message-bubble-user` - User chat message
- `.message-bubble-ai` - AI chat message
- `.text-gradient` - Pink gradient text

**Responsive Design:**
- Mobile-first approach
- Breakpoints: `sm`, `md`, `lg`
- Flexbox and Grid layouts

## Running the Application

### Development
```bash
cd frontend/medi-ai
npm install
npm start
```

### Build
```bash
npm run build
```

## File Organization Rules

When adding new files:

1. **Page Components** → `features/feature-name/pages/`
2. **Sub-Components** → `features/feature-name/components/`
3. **Constants** → `features/feature-name/constants/`
4. **Hooks** → `features/feature-name/hooks/`
5. **Utils** → `features/feature-name/utils/`
6. **Shared Components** → `shared/components/`
7. **Services** → `shared/services/`

## Code Examples

### Import a Component
```javascript
import Dashboard from './features/dashboard/pages/Dashboard';
import { Navbar } from './shared/components/Navbar';
```

### Use a Custom Hook
```javascript
import { useDashboardData } from './features/dashboard/hooks/useDashboardData';

const { studentData, loading } = useDashboardData(token);
```

### Use Utilities
```javascript
import { formatDate, calculateProgress } from './features/dashboard/utils/dashboardUtils';

const date = formatDate(new Date());
const percent = calculateProgress(25, 100);
```

### Use Constants
```javascript
import { DASHBOARD_COLORS, HIGH_YIELD_TOPICS } from './features/dashboard/constants/dashboardConstants';

const primaryColor = DASHBOARD_COLORS.primary; // '#ec4899'
```

## Color Implementation Examples

### Pink Button
```jsx
<button className="bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded-lg">
  Click Me
</button>
```

### Pink Gradient
```jsx
<div className="bg-gradient-to-r from-pink-400 to-pink-600 text-white p-4 rounded-lg">
  Feature Highlight
</div>
```

### Pink Border Card
```jsx
<div className="bg-white border border-pink-100 rounded-xl p-4 shadow-soft">
  Card Content
</div>
```

### Pink Text
```jsx
<p className="text-pink-600 font-semibold">Important Text</p>
```

## Common Tasks

### Add a New Feature
1. Create folder: `src/features/new-feature/`
2. Create subfolders: `pages/`, `components/`, `constants/`, `hooks/`, `utils/`
3. Create `README.md` with documentation
4. Add constants in `constants/`
5. Create custom hooks in `hooks/`
6. Use pink/white color scheme throughout

### Add a New Component
1. Determine if it's feature-specific or shared
2. Place in `features/feature-name/components/` or `shared/components/`
3. Add JSDoc comments
4. Use pink/white theme
5. Export and document usage

### Change Colors
1. Update in `constants/featureConstants.js`
2. Update in `config/featureConfig.js`
3. Update Tailwind classes if needed
4. Update `tailwind.config.js` if adding new colors

## Deployment

The app is containerized with Docker:

**Dockerfile:** `frontend/medi-ai/Dockerfile`
**Docker Compose:** `frontend/medi-ai/docker-compose.yml`

## Documentation Files

Each feature has its own `README.md`:
- [Dashboard Documentation](./dashboard/README.md)
- [Auth Documentation](./auth/README.md) (to be created)
- [Books Documentation](./books/README.md) (to be created)
- [Chat Documentation](./chat/README.md) (to be created)
- [Question Builder Documentation](./questionBuilder/README.md) (to be created)

## Git Commit Guidelines

When committing changes:
```
[feature-name] Brief description of change

- Detailed change 1
- Detailed change 2
```

Example:
```
[dashboard] Update colors to pink/white theme

- Changed DashboardCards colors from purple/amber to pink
- Updated RecommendationSection with pink accents
- Updated ProgressChart stats colors
```

## Troubleshooting

**Q: Colors not showing?**
A: Ensure Tailwind CSS is properly configured and imported in `index.css`.

**Q: Components not rendering?**
A: Check component paths and default exports.

**Q: API calls failing?**
A: Verify backend is running on `http://localhost:8000` and token is valid.

**Q: Style conflicts?**
A: Check for duplicate class names and CSS specificity issues.

## Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- Backend API: `http://localhost:8000`

## Contributing Guidelines

1. Follow the feature-based architecture
2. Maintain pink/white color consistency
3. Add comprehensive documentation
4. Use JSDoc for functions
5. Test components before pushing
6. Update relevant README files
7. Follow git commit guidelines

## Contact & Support

For questions about the codebase structure, refer to:
1. Feature-specific README.md files
2. Component JSDoc comments
3. `src/shared/` for global utilities

---

**Last Updated:** April 2026  
**Theme:** Pink & White  
**Framework:** React with Tailwind CSS  
**State Management:** React Context + Custom Hooks
