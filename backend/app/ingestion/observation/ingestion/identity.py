from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnifiedDeveloperIdentity:
    developer_id: str
    display_name: str
    aliases: tuple[str, ...]
    is_canonical: bool = True


class UnifiedIdentityResolver:
    def __init__(
        self,
    ):
        self._aliases: dict[tuple[str, str], UnifiedDeveloperIdentity] = {}

    def register(
        self,
        provider: str,
        external_id: str,
        developer_id: str,
        display_name: str | None = None,
        aliases: tuple[str, ...] = (),
    ) -> UnifiedDeveloperIdentity:
        identity = UnifiedDeveloperIdentity(
            developer_id=developer_id,
            display_name=display_name or developer_id,
            aliases=aliases,
        )
        self._aliases[
            (
                provider,
                external_id,
            )
        ] = identity
        return identity

    def resolve(
        self,
        provider: str,
        external_id: str | None,
    ) -> UnifiedDeveloperIdentity | None:
        if external_id is None:
            return None
        return self._aliases.get(
            (
                provider,
                external_id,
            ),
            UnifiedDeveloperIdentity(
                developer_id=f"UNRESOLVED_{external_id}",
                display_name=external_id,
                aliases=(external_id,),
                is_canonical=False,
            ),
        )

    def merge(
        self,
        primary_developer_id: str,
        secondary_developer_id: str,
    ) -> None:
        """Merge a secondary developer's aliases into a primary developer identity."""
        primary_identity = None
        for identity in self._aliases.values():
            if identity.developer_id == primary_developer_id:
                primary_identity = identity
                break
                
        if not primary_identity:
            raise ValueError(f"Primary identity '{primary_developer_id}' not found.")
            
        keys_to_update = []
        for key, identity in self._aliases.items():
            if identity.developer_id == secondary_developer_id:
                keys_to_update.append(key)
                
        if not keys_to_update:
            raise ValueError(f"Secondary identity '{secondary_developer_id}' not found.")
            
        for key in keys_to_update:
            self._aliases[key] = primary_identity

