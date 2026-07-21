from uuid import NAMESPACE_URL, uuid5


def stable_measurement_id(
    *parts: object,
) -> str:
    normalized = ":".join(str(part) for part in parts)

    return str(
        uuid5(
            NAMESPACE_URL,
            normalized,
        )
    )


