# Add Shortcuts Feature and Workspace Tag Scoping

## Overview
Adds user-specific shortcuts functionality for webapps with workspace scoping, plus fixes tag filtering to respect workspace/organization boundaries.

## Changes

### 1. Shortcuts System
- **New Django app**: `hexa/shortcuts/` with generic ContentType-based model
- **Webapp integration**: Add/remove shortcuts via bookmark button
- **Sidebar display**: Collapsible shortcuts section in workspace navigation
- **GraphQL API**:
  - `shortcuts(workspaceSlug)` query
  - `addToShortcuts(webappId)` mutation
  - `removeFromShortcuts(webappId)` mutation
  - `isShortcut` field on Webapp type

**Design Choice**: Uses Django's ContentType framework (same pattern as metadata system) for extensibility to other resource types (pipelines, datasets, etc.) without schema changes.

**Key Features**:
- User-specific and workspace-scoped
- Unique constraint prevents duplicates
- Custom ordering support (future drag-and-drop)
- Gracefully handles deleted objects

### 2. Tag Scoping Fixes
- **Pipelines**: Tag autocomplete now scoped to current workspace
- **Pipeline Templates**: Tag autocomplete scoped to organization (templates are org-level)
- **Tests**: Comprehensive test coverage for workspace/org tag isolation

## Testing
- ✅ Backend model tests (6/6 passing)
- ✅ Workspace tag scoping tests (comprehensive)
- ✅ i18n extraction successful
- ✅ Linting passed (only pre-existing warnings)

## Technical Details

### Backend Structure
```
hexa/shortcuts/
├── models.py              # Shortcut model with ContentType
├── schema/
│   ├── mutations.py       # Add/remove mutations
│   └── queries.py         # Shortcuts query
├── graphql/schema.graphql # GraphQL definitions
└── tests/test_models.py   # Model tests
```

### Frontend Structure
```
frontend/src/webapps/features/ShortcutWebappButton/  # Toggle component
frontend/src/workspaces/layouts/WorkspaceLayout/Sidebar.tsx  # Shortcuts display
```

### Helper Methods (on Webapp model)
```python
webapp.is_shortcut(user)         # Check if shortcuted
webapp.add_to_shortcuts(user)     # Add to shortcuts
webapp.remove_from_shortcuts(user) # Remove from shortcuts
```

## Future Extensibility
To add shortcuts for other models (e.g., Dataset):
1. Add helper methods to model (`is_shortcut`, `add_to_shortcuts`, `remove_from_shortcuts`)
2. Update shortcuts query resolver to handle new ContentType
3. Add UI component

No schema changes or migrations required.

## Migration
```bash
docker compose run app manage migrate
```

## Screenshots
- Shortcut button on webapp cards (bookmark icon)
- Collapsible "Shortcuts" section in sidebar
- Toast notifications on add/remove

## Notes
- Shortcuts are complementary to favorites (different UX patterns)
- Sidebar query skipped when collapsed for performance
- Apollo Client cache invalidation on mutations
