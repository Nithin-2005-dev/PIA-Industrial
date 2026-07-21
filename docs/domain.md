# Domain Model

## Event

Represents an immutable fact that occurred in the external world.

Properties:

* immutable
* append-only
* replayable

---

## Evidence

Represents an immutable interpretation extracted from an Event.

One Event may generate multiple Evidence objects.

Evidence does not contain business decisions.

---

## EntityRef

Immutable lightweight reference to a domain entity.

Used instead of embedding entities.

Supports loose coupling.

---

## ExpertiseEstimate

Immutable snapshot representing the estimated expertise relation between two entities.

Stores:

* raw_score
* confidence
* updated_at

History is reconstructed by replaying events rather than stored inside the estimate.
