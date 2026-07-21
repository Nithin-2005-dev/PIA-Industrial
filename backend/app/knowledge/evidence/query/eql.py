from dataclasses import dataclass

from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.domain import EvidencePriority
from app.knowledge.evidence.domain import EvidenceSeverity


@dataclass(frozen=True)
class EqlQuery:
    tenant_id: str
    find: str
    hop_depth: int | None = None
    target_node: str | None = None
    filters: tuple[tuple[str, str, str], ...] = ()
    order_by: str | None = None
    descending: bool = True


class EqlParser:

    def parse(
        self,
        text: str,
        tenant_id: str,
    ) -> EqlQuery:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]
        if not lines or not lines[0].upper().startswith("FIND "):
            raise ValueError(
                "EQL query must start with FIND"
            )

        find = lines[0].split(
            maxsplit=1
        )[1]
        
        hop_depth = None
        target_node = None
        
        import re
        match = re.match(r"(\d+)-HOP\s+DEPENDENCIES\s+OF\s+(.*)", find, re.IGNORECASE)
        if match:
            raw_hops = int(match.group(1))
            hop_depth = min(raw_hops, 5)
            target_node = match.group(2).strip()

        filters = []
        order_by = None
        descending = True

        for line in lines[1:]:
            upper = line.upper()
            if upper == "WHERE" or upper == "AND":
                continue
            if upper.startswith("ORDER BY "):
                parts = line.split()
                order_by = parts[2]
                descending = (
                    len(
                        parts
                    )
                    < 4
                    or parts[3].upper() == "DESC"
                )
                continue

            cleaned = line
            if cleaned.upper().startswith("AND "):
                cleaned = cleaned[4:]
            for operator in (">=", "<=", ">", "<", "==", "="):
                if operator in cleaned:
                    field, value = cleaned.split(
                        operator,
                        maxsplit=1,
                    )
                    filters.append(
                        (
                            field.strip(),
                            operator,
                            value.strip(),
                        )
                    )
                    break

        return EqlQuery(
            tenant_id=tenant_id,
            find=find,
            hop_depth=hop_depth,
            target_node=target_node,
            filters=tuple(
                filters
            ),
            order_by=order_by,
            descending=descending,
        )


class EqlEngine:

    def query(
        self,
        evidence: tuple[Evidence, ...],
        query: EqlQuery,
    ) -> tuple[Evidence, ...]:
        
        if query.hop_depth is not None and query.target_node:
            adjacency: dict[str, set[str]] = {}
            for item in evidence:
                adjacency.setdefault(item.evidence_id, set()).update(item.lineage.parent_evidence_ids)
                adjacency.setdefault(item.evidence_id, set()).update(item.lineage.derived_from)
            
            visited_nodes = {query.target_node}
            current_level = {query.target_node}
            
            for _ in range(query.hop_depth):
                next_level = set()
                for node in current_level:
                    neighbors = adjacency.get(node, set())
                    for neighbor in neighbors:
                        if neighbor not in visited_nodes:
                            visited_nodes.add(neighbor)
                            next_level.add(neighbor)
                current_level = next_level
                if not current_level:
                    break
                    
            evidence = tuple(item for item in evidence if item.evidence_id in visited_nodes)
            
        results = tuple(
            item
            for item in evidence
            if getattr(item.provenance, 'tenant_id', None) == query.tenant_id
            and self._matches_find(
                item,
                query.find,
            )
            and all(
                self._matches_filter(
                    item,
                    field,
                    operator,
                    expected,
                )
                for field, operator, expected in query.filters
            )
        )

        if query.order_by:
            results = tuple(
                sorted(
                    results,
                    key=lambda item: self._field_value(
                        item,
                        query.order_by or "",
                    ),
                    reverse=query.descending,
                )
            )

        return results

    def _matches_find(
        self,
        evidence: Evidence,
        find: str,
    ) -> bool:
        if "HOP DEPENDENCIES OF" in find.upper():
            return True
        if find.lower() in {
            "evidence",
            "all",
        }:
            return True
        return find.lower() in {
            evidence.name.replace(
                " ",
                "",
            ).lower(),
            evidence.category.lower(),
            evidence.evidence_id.lower(),
        } or find.lower() in evidence.name.lower()

    def _matches_filter(
        self,
        evidence: Evidence,
        field: str,
        operator: str,
        expected: str,
    ) -> bool:
        actual = self._field_value(
            evidence,
            field,
        )
        expected_value = self._parse_value(
            field,
            expected,
        )

        if operator in {
            "=",
            "==",
        }:
            return actual == expected_value
        if operator == ">":
            return actual > expected_value
        if operator == ">=":
            return actual >= expected_value
        if operator == "<":
            return actual < expected_value
        if operator == "<=":
            return actual <= expected_value
        return False

    def _field_value(
        self,
        evidence: Evidence,
        field: str,
    ):
        normalized = field.lower()
        if normalized == "confidence":
            return evidence.confidence
        if normalized == "severity":
            return evidence.severity.rank()
        if normalized == "priority":
            return evidence.priority.rank()
        if normalized == "quality":
            return evidence.quality
        if normalized == "strength":
            return evidence.strength
        if normalized == "category":
            return evidence.category
        return evidence.metadata.get(
            field,
            ""
        )

    def _parse_value(
        self,
        field: str,
        value: str,
    ):
        normalized = field.lower()
        cleaned = value.strip().strip('"').strip("'")
        if normalized == "severity":
            return EvidenceSeverity[
                cleaned.upper()
            ].rank()
        if normalized == "priority":
            return EvidencePriority[
                cleaned.upper()
            ].rank()
        try:
            return float(
                cleaned
            )
        except ValueError:
            return cleaned

