from datetime import UTC, datetime, timedelta

from app.estimator.policies.exponential_decay_policy import (
    ExponentialDecayPolicy,
)


def main():

    policy = ExponentialDecayPolicy(
        decay_rate=0.002,
    )

    now = datetime.now(UTC)

    score = 100.0

    scenarios = [
        ("Today", 0),
        ("30 Days", 30),
        ("90 Days", 90),
        ("180 Days", 180),
        ("365 Days", 365),
        ("730 Days", 730),
    ]

    print("\n=== EXPERTISE DECAY ===\n")

    for label, days in scenarios:

        last_updated = (
            now - timedelta(days=days)
        )

        decayed_score = policy.apply(
            score=score,
            last_updated=last_updated,
            current_time=now,
        )

        print(
            f"{label:<10}"
            f" -> "
            f"{decayed_score:.2f}"
        )


if __name__ == "__main__":
    main()