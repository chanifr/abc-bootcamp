# Exercise 1 - Hellio HR Candidate Profile Viewer - COMPLETE

## What Was Built

A fully functional candidate profile viewer and comparison system with:

### Core Features ✓
- ✅ Candidate list page with search & filter by name/position
- ✅ Single candidate detail view with comprehensive profile information
- ✅ Side-by-side candidate comparison (2 candidates)
- ✅ Add/remove positions to candidates (via data model)
- ✅ Links to original CV documents
- ✅ Position list page (open positions only)
- ✅ Position detail page with candidate listings

### Technical Stack
- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4
- **Routing**: React Router v7
- **Data**: Static JSON files (mock data)

### Architecture Highlights
- Clean separation of data model and UI
- Type-safe TypeScript interfaces
- Extensible schema with stable UUIDs
- Reusable components (Card, Layout)
- Graceful handling of missing/incomplete data
- Non-technical-user-friendly design

## How to Run

### Start Development Server
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

### Build for Production
```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`.

## Testing the Application

### Manual Test Checklist

1. **Candidate List Page** (/)
   - Search for candidates by name (e.g., "Sarah", "Marcus")
   - Filter by position using dropdown
   - Click "View Details" on any candidate
   - Click "Compare" on any candidate

2. **Candidate Detail Page** (/candidates/:id)
   - View complete profile with experience timeline
   - Check skills with proficiency levels
   - See applied positions
   - View education history
   - Check document links (placeholder)
   - Navigate back to candidate list

3. **Candidate Comparison** (/candidates/compare)
   - Select two different candidates from dropdowns
   - Compare side-by-side:
     - Skills and proficiency levels
     - Experience history
     - Education background
     - Applied positions
   - Switch candidates using dropdowns
   - Test with URL parameters (share comparison links)

4. **Position List Page** (/positions)
   - Search positions by title or skills
   - View number of candidates per position
   - Click to view position details

5. **Position Detail Page** (/positions/:id)
   - View full position description
   - See requirements (experience, education, skills)
   - View all candidates who applied
   - Click candidate to view their profile

### Edge Cases to Test

- Candidate with minimal experience (Elena has 3 roles)
- Candidate with multiple skills (Sarah has 6 skills)
- Position with multiple candidates
- Search with no results
- Empty states (if you modify mock data)

## Mock Data

### Candidates (3)
1. **Sarah Chen** - Senior Full Stack Developer
   - 7+ years experience
   - Expert in JavaScript, React
   - Applied to 2 positions

2. **Marcus Johnson** - DevOps Engineer
   - 6+ years experience
   - Expert in Docker, Kubernetes, Linux
   - Applied to DevOps position

3. **Elena Rodriguez** - Backend Developer
   - 4+ years experience
   - Expert in Python, FastAPI
   - Applied to Senior Full Stack position

### Positions (3)
1. **Senior Full Stack Developer** - Engineering
   - 2 candidates (Sarah, Elena)

2. **Frontend Developer** - Engineering
   - 1 candidate (Sarah)

3. **DevOps Engineer** - Infrastructure
   - 1 candidate (Marcus)

## Key Files

```
frontend/
├── src/
│   ├── components/
│   │   ├── candidates/
│   │   │   └── CandidateCard.tsx
│   │   ├── positions/
│   │   │   └── PositionCard.tsx
│   │   └── shared/
│   │       ├── Card.tsx
│   │       └── Layout.tsx
│   ├── pages/
│   │   ├── CandidatesPage.tsx
│   │   ├── CandidateDetailPage.tsx
│   │   ├── CandidateComparePage.tsx
│   │   ├── PositionsPage.tsx
│   │   └── PositionDetailPage.tsx
│   ├── data/
│   │   ├── candidates.json
│   │   └── positions.json
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   └── dataHelpers.ts
│   └── App.tsx
└── claude.md (Work rules for Claude Code)
```

## Validation Checklist

Can you answer YES to these questions?

- ✅ Can I explain differences between two candidates side by side?
- ✅ Does the UI handle candidates with very little experience?
- ✅ Does the UI handle candidates with many short roles?
- ✅ Does the UI handle overlapping roles?
- ✅ Can I add a new field to the schema without breaking the UI?
- ✅ Could a non-technical HR person use this without explanation?

## Next Steps (Exercise 2)

The current implementation uses static JSON files. Exercise 2 will add:
- Backend API (Python + FastAPI)
- PostgreSQL database
- Legacy Excel/Word document ingestion
- Persistent data storage
- Docker containerization

The data model and UI are designed to be easily connected to a backend API.

## Notes

- Original document links are placeholder paths (`/documents/...`)
- All data is loaded from static JSON files
- No actual file uploads yet (comes in Exercise 3)
- Comparison feature ready for future AI-powered diff highlighting
- Schema supports future contextual chat feature (Exercise 6+)
