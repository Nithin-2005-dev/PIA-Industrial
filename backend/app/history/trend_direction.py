from enum import Enum


class TrendDirection(
    str,
    Enum,
):

    IMPROVING = "IMPROVING"

    STABLE = "STABLE"

    DECLINING = "DECLINING"