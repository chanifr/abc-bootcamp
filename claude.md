# Hellio HR - Claude Code Work Rules

## Project Overview
Building an AI-powered HR system for candidate management and recruitment workflow automation.
**Current Phase:** Exercise 1 - Candidate Profile Viewer & Diff

## Technology Stack

### Frontend
- React 18+ with Vite
- Tailwind CSS for styling
- TypeScript for type safety
- React Router for navigation

### Backend (Exercise 2+)
- Python 3.11+
- FastAPI
- PostgreSQL
- Docker

### Current Exercise (Exercise 1)
- Static JSON files for data storage
- No backend API yet
- Focus on UI/UX and data model design

## Core Principles

### 1. Clarity Over Cleverness
- Write explicit, readable code
- Prefer simple solutions over complex abstractions
- No premature optimization

### 2. Traceability Over Automation
- Maintain clear links between normalized data and original sources
- Every candidate action should be auditable
- Original documents are never modified

### 3. Humans in Control
- UI must be intuitive for non-technical HR users
- All agent actions require human review
- Clear feedback for all operations

### 4. Extensibility First
- Design for future AI/agent integration
- Schema should support adding fields without UI rewrites
- Prepare for "contextual chat" feature in future exercises

## Data Model Rules

### Candidate Schema
```json
{
  "id": "string (UUID)",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "phone": "string",
  "status": "Active | Inactive | Hired",
  "appliedPositions": ["position-id-1", "position-id-2"],
  "experience": [
    {
      "id": "string (UUID)",
      "company": "string",
      "title": "string",
      "startDate": "YYYY-MM-DD",
      "endDate": "YYYY-MM-DD | null",
      "description": "string",
      "sortOrder": "number"
    }
  ],
  "education": [
    {
      "id": "string (UUID)",
      "institution": "string",
      "degree": "string",
      "field": "string",
      "graduationDate": "YYYY-MM-DD | null",
      "sortOrder": "number"
    }
  ],
  "skills": [
    {
      "id": "string (UUID)",
      "name": "string",
      "level": "Beginner | Intermediate | Advanced | Expert",
      "sortOrder": "number"
    }
  ],
  "originalDocuments": [
    {
      "id": "string (UUID)",
      "filename": "string",
      "type": "CV | Resume | Cover Letter",
      "path": "string",
      "uploadDate": "ISO 8601"
    }
  ],
  "notes": "string",
  "createdAt": "ISO 8601",
  "updatedAt": "ISO 8601"
}
```

### Position Schema
```json
{
  "id": "string (UUID)",
  "title": "string",
  "department": "string",
  "status": "Open | Closed | On Hold",
  "description": "string",
  "requirements": {
    "experience": "string",
    "education": "string",
    "skills": ["string"]
  },
  "candidates": ["candidate-id-1", "candidate-id-2"],
  "createdAt": "ISO 8601",
  "updatedAt": "ISO 8601"
}
```

### Key Data Model Rules
1. **Stable IDs**: All entities and sub-entities must have UUIDs
2. **Sorting**: Lists with `sortOrder` field for consistent display
3. **Dates**: ISO 8601 format (YYYY-MM-DD for dates, full ISO for timestamps)
4. **References**: Use IDs, never duplicate data
5. **Extensibility**: New fields can be added without breaking existing UI

## File Structure

```
/
├── claude.md (this file)
├── README.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── candidates/
│   │   │   ├── positions/
│   │   │   └── shared/
│   │   ├── pages/
│   │   │   ├── CandidatesPage.tsx
│   │   │   ├── CandidateDetailPage.tsx
│   │   │   ├── CandidateComparePage.tsx
│   │   │   └── PositionsPage.tsx
│   │   ├── data/
│   │   │   ├── candidates.json
│   │   │   └── positions.json
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   └── dataHelpers.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   └── documents/ (original CV files)
│   └── package.json
└── data/
    └── raw/ (original PDFs/Word docs before normalization)
```

## UI/UX Guidelines

### Design Principles
1. **Readability over density** - generous spacing, clear typography
2. **Scannable layouts** - use headers, sections, visual hierarchy
3. **Graceful degradation** - missing data should not break UI
4. **Consistent patterns** - reuse components, maintain visual consistency

### Component Guidelines
- Use semantic HTML
- Ensure keyboard navigation works
- Add loading and error states
- Show empty states with helpful messages
- Use icons sparingly and meaningfully

### Comparison View Requirements
- Side-by-side layout on desktop
- Clear visual distinction between candidates
- Highlight differences (future enhancement)
- Easy navigation between sections

## Git Workflow

### Commit Frequency
- Commit after each working feature
- Commit after completing each sub-task
- Commit before major refactoring

### Commit Message Format
```
<type>: <short description>

<optional longer description>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Examples
- `feat: add candidate list component`
- `feat: implement side-by-side candidate comparison`
- `refactor: extract experience timeline component`
- `docs: update data schema documentation`

## Development Guidelines

### Code Style
- Use TypeScript for type safety
- Functional components with hooks (React)
- Destructure props
- Use early returns to reduce nesting
- Keep components focused (single responsibility)

### Naming Conventions
- **Components**: PascalCase (e.g., `CandidateCard.tsx`)
- **Files**: camelCase for utilities, PascalCase for components
- **Variables**: camelCase
- **Constants**: UPPER_SNAKE_CASE
- **Types/Interfaces**: PascalCase with descriptive names

### What to Avoid
- Hard-coding assumptions about data shape
- Mixing UI logic with data transformation
- Over-engineering for out-of-scope features
- Creating abstractions for single-use cases
- Adding features not in requirements

## Testing & Validation

### Manual Testing Checklist
1. Can I compare two candidates side by side?
2. Does UI handle missing/incomplete data gracefully?
3. Can I add/remove positions from a candidate?
4. Are original document links accessible?
5. Can a non-technical user navigate without help?
6. Does comparison work with:
   - Very little experience?
   - Many short roles?
   - Overlapping roles?

### Self-Check Questions
- Can I add a new field (e.g., certifications) without major UI changes?
- Is the data model separate from UI concerns?
- Are original documents preserved and accessible?

## Exercise-Specific Requirements

### Must Have (Exercise 1)
- [x] Candidate list with search & filter by name/position
- [x] Single candidate detail view
- [x] Side-by-side candidate comparison
- [x] Add/remove positions to candidate
- [x] Links to original CV documents
- [x] Position list (open positions)
- [x] Position detail with candidate list

### Out of Scope (Future Exercises)
- Backend API (Exercise 2)
- Database persistence (Exercise 2)
- PDF/Word ingestion automation (Exercise 3)
- LLM-based enrichment (Exercise 3)
- Semantic search (Exercise 5)
- Agent workflows (Exercise 6)
- MCP integration (Exercise 7)

## Mock Data Requirements

### Candidates (Create 2-3)
- Mix of experience levels (junior, mid, senior)
- Variety in role types (frontend, backend, full-stack, DevOps)
- Different education backgrounds
- Some with gaps in employment
- Some with overlapping roles
- Include realistic skills and proficiency levels

### Positions (Create 2-3)
- Different departments
- Different seniority levels
- Clear requirements
- Associate candidates with positions

## Notes for Claude Code

### When Asked to Implement Features
1. Read existing code first
2. Follow the data model schema exactly
3. Maintain consistency with existing components
4. Commit after each working step
5. Test manually before marking complete

### When Creating Components
- Check if similar component exists first
- Follow the component structure in existing code
- Use Tailwind utility classes
- Add TypeScript types
- Handle loading/error/empty states

### When Modifying Data
- Never change the schema without discussion
- Maintain referential integrity (IDs must match)
- Update both candidates and positions if relationship changes
- Preserve sortOrder fields

## Questions to Ask Before Implementing
1. Does this align with "clarity over cleverness"?
2. Is this extensible for future exercises?
3. Will this work for non-technical users?
4. Am I over-engineering?
5. Does this maintain separation between data and UI?
