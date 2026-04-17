# Dashboard Feature Documentation

## Overview
The Dashboard feature provides a comprehensive student learning dashboard with progress tracking, exam schedules, recommendations, and analytics. The design uses a **pink and white color theme** for a modern, clean interface.

## Folder Structure

```
dashboard/
├── pages/
│   └── Dashboard.jsx              # Main dashboard page component
│
├── components/
│   ├── DashboardCards.jsx         # Key metrics cards (Progress, Questions, Exams, Streak)
│   ├── ProgressChart.jsx          # Progress visualization and weekly activity chart
│   └── RecommendationSection.jsx  # High-yield topics, exam recommendations, popular books
│
├── constants/
│   └── dashboardConstants.js      # All hardcoded constants and default values
│
├── hooks/
│   └── useDashboardData.js        # Custom hook for data fetching and state management
│
├── utils/
│   └── dashboardUtils.js          # Utility functions for data transformation
│
├── config/
│   └── dashboardConfig.js         # Feature configuration and settings
│
├── styles/
│   └── (Custom CSS files)          # Dashboard-specific styles (if needed)
│
└── README.md                       # This file
```

## Component Details

### Dashboard Page (`pages/Dashboard.jsx`)
The main page component that orchestrates the entire dashboard.

**Features:**
- Fetches user statistics from API
- Handles loading and error states
- Displays dashboard cards, progress chart, and recommendations
- Provides refresh functionality

**State:**
- `studentData`: User progress and statistics
- `loading`: Loading state
- `error`: Error messages

**Usage:**
```jsx
import Dashboard from './features/dashboard/pages/Dashboard';

function App() {
  return <Dashboard />;
}
```

### DashboardCards Component
Displays four key metric cards:
1. **Overall Progress** - Progress percentage with visual bar
2. **Questions Today** - Number of questions answered today
3. **Upcoming Exams** - Number and details of upcoming exams
4. **Day Streak** - Consecutive days of studying

**Props:**
- `progress` (number): Overall progress percentage
- `questionsToday` (number): Questions answered today
- `upcomingExams` (array): Array of exam objects

**Color Scheme:**
- Progress Card: Pink gradient
- Questions Card: Pink shades
- Exams Card: Pink to rose gradient
- Streak Card: Pink gradient

### ProgressChart Component
Visualizes learning progress through multiple formats:
1. **Circular Progress** - Overall progress percentage
2. **Weekly Activity Chart** - Bar chart showing daily activity
3. **Stats Summary** - Topics completed, questions asked, study time

**Props:**
- `progress` (number): Overall progress percentage

### RecommendationSection Component
Provides personalized recommendations in three categories:
1. **High-Yield Topics** - Important study topics
2. **Exam Recommended Chapters** - Chapters with exam weight
3. **Most Accessed Books** - Popular reference materials

**Props:**
- `onBookClick` (function): Callback when user clicks a book

**Color Scheme:**
- All sections use pink borders and pink color accents
- Tags and badges use pink backgrounds with pink text

## Constants (`constants/dashboardConstants.js`)

Centralized constants used throughout the dashboard:

```javascript
// API Endpoints
DASHBOARD_API_ENDPOINTS.USER_STATS

// Default Data Structure
DEFAULT_DASHBOARD_DATA

// Color Palette
DASHBOARD_COLORS = {
  primary: '#ec4899',       // Pink
  primaryDark: '#db2777',   // Dark Pink
  primaryLight: '#f472b6',  // Light Pink
  secondary: '#fce7f3',     // Very Light Pink
  white: '#ffffff',
  gray: '#6b7280',
  lightGray: '#f3f4f6'
}

// Animation Configuration
ANIMATION_DELAYS

// High-Yield Topics, Exam Recommendations, Books
HIGH_YIELD_TOPICS
EXAM_RECOMMENDED_CHAPTERS
MOST_ACCESSED_BOOKS
```

## Custom Hooks (`hooks/useDashboardData.js`)

### useDashboardData
Manages all dashboard data fetching and state.

**Parameters:**
- `token` (string): Authentication token for API calls

**Returns:**
```javascript
{
  studentData,      // Current dashboard data
  loading,          // Loading state
  error,            // Error message (if any)
  loadingState,     // Detailed loading state
  refreshData       // Function to refresh data
}
```

**Example:**
```javascript
const { studentData, loading, error, refreshData } = useDashboardData(token);

if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error} />;

return (
  <Dashboard data={studentData} onRefresh={refreshData} />
);
```

## Utility Functions (`utils/dashboardUtils.js`)

Helpful functions for data manipulation:

| Function | Purpose |
|----------|---------|
| `calculateProgress(current, total)` | Calculate progress percentage |
| `formatDate(date)` | Format date to readable string |
| `calculateDaysRemaining(targetDate)` | Calculate days until target date |
| `findNearestExam(exams)` | Get the nearest upcoming exam |
| `sortTopicsByImportance(topics)` | Sort topics by importance level |
| `sortBooksByViews(books)` | Sort books by view count |
| `getPerformanceLevel(score)` | Get text description of performance |
| `getPerformanceColor(score)` | Get color class based on score |
| `formatLargeNumber(num)` | Format numbers (1000 → 1K) |
| `validateDashboardData(data)` | Validate data structure |

**Example:**
```javascript
import { calculateProgress, formatDate } from './utils/dashboardUtils';

const progress = calculateProgress(25, 100); // Returns 25
const formattedDate = formatDate('2026-03-01'); // Returns 'Mar 1, 2026'
```

## Configuration (`config/dashboardConfig.js`)

Central configuration for the entire dashboard feature:

```javascript
DASHBOARD_CONFIG = {
  enabled: true,
  refreshInterval: 300000,        // 5 minutes
  features: {
    progressChart: true,
    dashboardCards: true,
    recommendationSection: true,
    weakAreasAnalysis: true
  },
  theme: {
    primaryColor: '#ec4899',      // Pink
    primaryDark: '#db2777'        // Dark Pink
  },
  data: {
    maxRecentTopics: 5,
    maxUpcomingExams: 4,
    maxRecommendedTopics: 5
  }
}
```

## Color Theme: Pink & White

The dashboard uses a cohesive pink and white color scheme:

**Primary Colors:**
- **Pink (`#ec4899`)**: Main accent color for buttons, headers, and interactive elements
- **Dark Pink (`#db2777`)**: Darker shade for hover states and emphasis
- **Light Pink (`#f472b6`)**: Lighter shade for backgrounds and secondary elements
- **Very Light Pink (`#fce7f3`)**: Very subtle background color

**Supporting Colors:**
- **White (`#ffffff`)**: Card backgrounds, primary text background
- **Gray (`#6b7280`)**: Text color for descriptions
- **Light Gray (`#f3f4f6`)**: Subtle backgrounds

**Tailwind Classes:**
- `from-pink-400 to-pink-600` - Gradient backgrounds
- `text-pink-600` - Emphasized text
- `bg-pink-50` - Subtle backgrounds
- `border-pink-100` - Subtle borders

## Data Flow

```
Dashboard.jsx (Page)
    ↓
useDashboardData() Hook
    ├── Fetches from API
    ├── Transforms data
    └── Manages loading/error states
    ↓
Components (DashboardCards, ProgressChart, RecommendationSection)
    ├── Receive props
    ├── Use utility functions
    └── Render with pink/white theme
```

## Component Integration

### Passing Data Down
```javascript
// In Dashboard.jsx
<DashboardCards
  progress={studentData.progress}
  questionsToday={studentData.questionsToday}
  upcomingExams={studentData.upcomingExams}
/>
```

### Using Utilities
```javascript
// In components
import { formatDate, calculateDaysRemaining } from '../utils/dashboardUtils';

const formattedDate = formatDate(examDate);
const daysLeft = calculateDaysRemaining(examDate);
```

### Using Constants
```javascript
// In components
import { MOST_ACCESSED_BOOKS } from '../constants/dashboardConstants';

const books = MOST_ACCESSED_BOOKS.map(book => (
  <BookCard key={book.id} book={book} />
));
```

## API Integration

The dashboard communicates with the backend via:

**Endpoint:** `http://localhost:8000/api/user-stats`

**Expected Response:**
```json
{
  "progress_score": 75,
  "recent_activity": 12,
  "average_rating": 4.5
}
```

**Authentication:** Bearer token in Authorization header

## Styling

**Tailwind CSS Classes Used:**
- `card-soft` - White card with pink border
- `bg-gradient-pink` - Light pink gradient background
- `text-gradient` - Pink gradient text
- `shadow-soft` - Soft pink-tinted shadow
- `animate-slide-in` - Slide-in animation

## File Modification Guide

When modifying dashboard components:

1. **Change Colors**: Update in `constants/dashboardConstants.js` and `config/dashboardConfig.js`
2. **Add New Data**: Add to `useDashboardData.js` custom hook
3. **New Utility Function**: Add to `utils/dashboardUtils.js`
4. **New Component**: Create in `components/` folder
5. **Constants**: Add to `constants/dashboardConstants.js`

## Testing

Example test structure:
```javascript
import { calculateProgress } from '../utils/dashboardUtils';

describe('Dashboard Utilities', () => {
  test('calculateProgress returns correct percentage', () => {
    expect(calculateProgress(25, 100)).toBe(25);
  });
});
```

## Common Tasks

### Adding a New Card
1. Create component in `components/`
2. Add constants in `constants/dashboardConstants.js`
3. Import and use in `Dashboard.jsx`
4. Use pink/white color scheme

### Fetching New Data
1. Add API endpoint to `constants/dashboardConstants.js`
2. Add data transformation in `useDashboardData.js`
3. Use in components with props

### Changing Theme Colors
1. Update `DASHBOARD_COLORS` in `dashboardConstants.js`
2. Update `theme` in `dashboardConfig.js`
3. Update Tailwind classes in JSX files

## Best Practices

1. ✅ Keep all constants in `dashboardConstants.js`
2. ✅ Use utility functions from `dashboardUtils.js`
3. ✅ Use the `useDashboardData` hook for API calls
4. ✅ Follow the pink and white color scheme
5. ✅ Add JSDoc comments to new functions
6. ✅ Validate data with `validateDashboardData()`
7. ✅ Handle loading and error states gracefully

## Troubleshooting

**Q: Dashboard not loading?**
A: Check console for API errors. Ensure token is valid and API endpoint is accessible.

**Q: Colors look wrong?**
A: Verify Tailwind CSS is properly imported and configured in `tailwind.config.js`.

**Q: Data not updating?**
A: Check `useDashboardData` hook. Call `refreshData()` function to manually refresh.

## Contributing

When contributing to the dashboard:
1. Follow the existing folder structure
2. Add comprehensive JSDoc comments
3. Update this README if adding new features
4. Maintain the pink and white color scheme
5. Test all changes before submitting

---

**Last Updated:** April 2026  
**Theme:** Pink & White  
**Framework:** React with Tailwind CSS
