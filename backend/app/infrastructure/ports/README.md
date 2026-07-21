# Ports Layer

The ports layer defines boundaries between the core system and external
platforms.

The core should never depend on GitHub, Jira, Slack, GitLab, Azure DevOps, or
vendor SDK DTOs. It depends on abstract capabilities that return canonical
observations.

## ObservationSourcePort

Provides immutable `Observation` objects from an external source.

```text
External Platform
        |
        v
Vendor Adapter
        |
        v
ObservationSourcePort
        |
        v
Canonical Observation
```

`EventSourcePort` remains as a deprecated import alias only. New adapters must
return `app.observation.domain.Observation`.
