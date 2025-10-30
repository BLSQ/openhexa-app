# Shortcuts Architecture: Generic ContentType-Based Approach

## Overview

The shortcuts feature allows users to create quick-access links to frequently used resources in OpenHEXA. This document explains the architectural decisions behind using Django's ContentType framework for a generic, extensible shortcuts system.

## Executive Summary

**Decision**: Implement shortcuts using Django's `ContentType` framework with a generic foreign key pattern.

**Rationale**: Maximum extensibility to support shortcuts for any model type (webapps, pipelines, datasets, etc.) without schema changes.

**Status**: Implemented (October 2025)

---

## Problem Statement

Users needed a way to create persistent, quick-access links to frequently used resources. The system needed to:

1. Allow users to shortcut any type of resource (webapps, pipelines, datasets, connections, etc.)
2. Display shortcuts in a collapsible sidebar section
3. Be workspace-scoped and user-specific
4. Support future resource types without code changes
5. Allow custom ordering of shortcuts

## Alternatives Considered

### Approach 1: Generic ContentType System (✅ Selected)

**Implementation:**
```python
class Shortcut(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    # Generic foreign key - can point to ANY model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    order = models.IntegerField(default=0)
```

**Pros:**
- ✅ Works with any model without schema changes
- ✅ Single source of truth for shortcuts logic
- ✅ Centralized in one app (`hexa/shortcuts`)
- ✅ Easy to add new resource types
- ✅ Supports custom features (ordering, labels)
- ✅ Proven pattern (metadata system uses it)

**Cons:**
- ⚠️ Slightly more complex than ManyToMany
- ⚠️ Requires ContentType imports
- ⚠️ Query joins are less direct

### Approach 2: ManyToMany Per Model (❌ Rejected)

**Implementation:**
```python
class Webapp(models.Model):
    favorites = models.ManyToManyField(User, related_name="favorite_webapps")
    shortcuts = models.ManyToManyField(User, related_name="shortcut_webapps")  # NEW
```

**Pros:**
- ✅ Simple and straightforward
- ✅ Direct database queries
- ✅ Follows existing favorites pattern

**Cons:**
- ❌ Requires adding field to every model
- ❌ Not extensible to new types
- ❌ Duplicates logic across models
- ❌ Can't support advanced features easily
- ❌ Schema coupling between features

### Approach 3: Separate Shortcut Tables Per Type (❌ Rejected)

**Implementation:**
```python
class WebappShortcut(models.Model):
    user = models.ForeignKey(User)
    webapp = models.ForeignKey(Webapp)

class PipelineShortcut(models.Model):
    user = models.ForeignKey(User)
    pipeline = models.ForeignKey(Pipeline)
# ... one table per type
```

**Pros:**
- ✅ Type-safe queries
- ✅ Simple per-type logic

**Cons:**
- ❌ Massive code duplication
- ❌ Can't query all shortcuts together
- ❌ Maintenance nightmare
- ❌ Need new table for each type

---

## Selected Approach: ContentType System

### Why This Approach?

1. **Proven Pattern**: OpenHEXA already uses ContentType for the metadata system (`hexa/metadata/models.py`), demonstrating it's a trusted pattern in the codebase.

2. **True Extensibility**: The original requirement explicitly stated: *"with idea in mind that in the future we would like to extend the shortcuts for other features"*. ContentType is the only approach that delivers this without ongoing schema changes.

3. **Single Source of Truth**: All shortcut logic lives in `hexa/shortcuts/`, making it easy to maintain, test, and extend.

4. **Future-Proof Features**: Easy to add:
   - Custom ordering (drag-and-drop reordering)
   - Custom labels/aliases
   - Shortcut groups/categories
   - Sharing shortcuts with teams
   - Shortcut analytics

5. **Workspace Scoping**: Naturally supports multi-tenancy with workspace-scoped shortcuts.

### Implementation Details

#### Backend Structure

```
backend/hexa/shortcuts/
├── __init__.py
├── apps.py
├── models.py              # Shortcut model with ContentType
├── permissions.py         # Permission checks
├── admin.py               # Django admin interface
├── migrations/            # Database migrations
├── graphql/
│   └── schema.graphql     # GraphQL type definitions
├── schema/
│   ├── __init__.py
│   ├── types.py           # GraphQL type resolvers
│   ├── queries.py         # Query resolvers
│   └── mutations.py       # Mutation resolvers
└── tests/
    └── test_models.py     # Unit tests
```

#### Key Components

**1. Shortcut Model** (`hexa/shortcuts/models.py`)
- Uses Django's `GenericForeignKey` to reference any model
- Includes `order` field for custom sorting
- Has `filter_for_user()` and `filter_for_workspace()` QuerySet methods

**2. Helper Methods** (on individual models)
- `is_shortcut(user)` - Check if resource is shortcuted
- `add_to_shortcuts(user)` - Add resource to shortcuts
- `remove_from_shortcuts(user)` - Remove from shortcuts

**3. GraphQL Schema** (`hexa/shortcuts/graphql/schema.graphql`)
- `shortcuts(workspaceSlug)` query - Returns all shortcuts for workspace
- `addToShortcuts` mutation - Add resource to shortcuts
- `removeFromShortcuts` mutation - Remove resource from shortcuts

**4. Frontend Components**
- `ShortcutWebappButton` - Toggle shortcut status
- Sidebar shortcuts section - Collapsible list of shortcuts
- Uses Apollo Client for GraphQL mutations

### Adding New Resource Types

To add shortcuts support for a new resource type (e.g., `Dataset`):

**Backend** (add to model):
```python
# hexa/datasets/models.py
def is_shortcut(self, user: User):
    from hexa.shortcuts.models import Shortcut
    from django.contrib.contenttypes.models import ContentType

    content_type = ContentType.objects.get_for_model(self.__class__)
    return Shortcut.objects.filter(
        user=user, content_type=content_type, object_id=self.id
    ).exists()

# Similar for add_to_shortcuts() and remove_from_shortcuts()
```

**Frontend** (extend queries resolver):
```python
# hexa/shortcuts/schema/queries.py
dataset_content_type = ContentType.objects.get_for_model(Dataset)

if shortcut.content_type == dataset_content_type:
    dataset = Dataset.objects.get(pk=shortcut.object_id)
    shortcut_items.append({
        "id": str(dataset.id),
        "name": dataset.name,
        "url": f"/workspaces/{workspace.slug}/datasets/{dataset.id}",
        "type": "dataset",
    })
```

That's it! No schema changes, no new tables, just add the helper methods and extend the resolver.

---

## Comparison with Existing Patterns

### Favorites (ManyToMany)

OpenHEXA currently uses ManyToMany for favorites:
- `Webapp.favorites = ManyToManyField(User)`
- Simple but not extensible
- Each model needs its own favorites field

**Shortcuts are different** because:
- Shortcuts appear in **persistent navigation** (sidebar)
- Shortcuts support **multiple resource types** in one list
- Shortcuts need **custom ordering**

### Metadata System (ContentType)

OpenHEXA already uses ContentType for metadata:
```python
class MetadataAttribute(Base):
    object_content_type = models.ForeignKey(ContentType)
    object_id = models.UUIDField()
    target = GenericForeignKey('object_content_type', 'object_id')
    key = models.CharField(max_length=255)
    value = models.JSONField(default=dict)
```

Shortcuts follow the **exact same pattern**, demonstrating consistency with existing architecture.

### Dataset Pinning (Boolean Field)

Datasets use `DatasetLink.is_pinned = BooleanField()`:
- Workspace-level (not user-specific)
- Simple boolean flag
- Different use case than shortcuts

---

## Trade-offs and Considerations

### Performance Considerations

**Query Performance:**
- ContentType queries add a JOIN to `django_content_type`
- This is negligible for sidebar queries (typically <10 shortcuts)
- Can optimize with `select_related('content_type')` if needed

**Caching Strategy:**
- Shortcuts query runs once per page load
- Skipped when sidebar is collapsed
- Apollo Client caches results automatically

### Database Constraints

**Unique Constraint:**
```python
models.UniqueConstraint(
    fields=['user', 'workspace', 'content_type', 'object_id'],
    name='unique_user_workspace_content_shortcut'
)
```

Ensures users can't create duplicate shortcuts for the same resource.

### Migration Path

**From Favorites to Shortcuts:**
- Favorites and shortcuts are **complementary**, not replacements
- Favorites = Feature-specific bookmarking with visual prominence
- Shortcuts = Cross-feature navigation menu

**No data migration needed** - they serve different purposes:
- Favorites: Show cards at top of webapps page
- Shortcuts: Persist in sidebar across all pages

---

## Future Enhancements

The ContentType architecture enables these future features:

### 1. Custom Ordering
```python
# Already supported in model
order = models.IntegerField(default=0)

# Frontend: Add drag-and-drop reordering
# Backend: Update order field via mutation
```

### 2. Custom Labels
```python
class Shortcut(Base):
    # Add optional custom label
    custom_label = models.CharField(max_length=255, null=True, blank=True)
```

### 3. Shortcut Groups
```python
class ShortcutGroup(Base):
    name = models.CharField(max_length=255)
    shortcuts = models.ManyToManyField(Shortcut)
```

### 4. Team Shortcuts
```python
class Shortcut(Base):
    # Make user optional for team shortcuts
    user = models.ForeignKey(User, null=True)
    team = models.ForeignKey(Team, null=True)
```

### 5. Global Shortcuts
Support shortcuts across multiple workspaces:
```python
# Make workspace optional
workspace = models.ForeignKey(Workspace, null=True)
```

---

## Testing Strategy

### Backend Tests

**Model Tests** (`test_models.py`):
- Test shortcut creation/deletion
- Test uniqueness constraints
- Test QuerySet filtering
- Test helper methods on models

**Schema Tests** (`test_schema.py`):
- Test GraphQL queries
- Test mutations
- Test permissions
- Test error handling

### Frontend Tests

**Component Tests**:
- Test ShortcutWebappButton rendering
- Test toggle behavior
- Test toast notifications

**Integration Tests**:
- Test sidebar shortcuts section
- Test collapsible behavior
- Test shortcuts query

---

## Migration Instructions

### Running the Migration

```bash
# Run migration
docker compose run app manage migrate

# Create superuser if needed
docker compose run app manage createsuperuser
```

### Testing the Feature

1. Navigate to webapps page
2. Click bookmark icon next to a webapp
3. Check sidebar - webapp should appear in "Shortcuts" section
4. Click shortcut in sidebar - should navigate to webapp
5. Click bookmark again - should remove from shortcuts

---

## Conclusion

The ContentType-based shortcuts system provides maximum flexibility and extensibility while maintaining clean architecture. It follows established patterns in the OpenHEXA codebase (metadata system) and enables future enhancements without schema changes.

**Key Benefits:**
- ✅ Extensible to any resource type
- ✅ Single source of truth
- ✅ Follows existing patterns
- ✅ Easy to test and maintain
- ✅ Enables advanced features

**This approach aligns with OpenHEXA's principle of building maintainable, extensible systems that can evolve with user needs.**

---

## References

- **Django ContentTypes Documentation**: https://docs.djangoproject.com/en/stable/ref/contrib/contenttypes/
- **Existing Metadata System**: `backend/hexa/metadata/models.py`
- **Favorites Implementation**: `backend/hexa/webapps/models.py`
- **Original Requirements**: "with idea in mind that in the future we would like to extend the shortcuts for other features"
