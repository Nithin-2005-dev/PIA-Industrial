class StrategyComparisonService:

    def compare(
        self,
        outcomes,
    ):

        return sorted(
            outcomes,
            key=lambda outcome: (
                outcome.predicted_health
            ),
            reverse=True,
        )