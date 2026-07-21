"""
===============================================================================

Platform Showcase Analytics

===============================================================================

Reusable analytics utilities for the showcase.

NO business logic.

NO rendering.

NO platform-specific assumptions.

These functions simply aggregate immutable objects.

Every showcase stage should use this library.

===============================================================================
"""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median
from math import sqrt


# =============================================================================
# Generic Statistics
# =============================================================================


def average(values):

    values = list(values)

    if not values:
        return 0.0

    return mean(values)


def median_value(values):

    values = list(values)

    if not values:
        return 0.0

    return median(values)


def minimum(values):

    values = list(values)

    if not values:
        return 0

    return min(values)


def maximum(values):

    values = list(values)

    if not values:
        return 0

    return max(values)


def standard_deviation(values):

    values = list(values)

    if len(values) < 2:
        return 0.0

    avg = average(values)

    variance = sum(
        (x - avg) ** 2
        for x in values
    ) / len(values)

    return sqrt(variance)


# =============================================================================
# Counter Helpers
# =============================================================================


def counter(iterable):

    return Counter(iterable)


def top(counter_obj, limit=10):

    return counter_obj.most_common(limit)


# =============================================================================
# Observation Analytics
# =============================================================================


def observation_type_distribution(observations):

    return Counter(
        o.observation_type.value
        for o in observations
    )


def observation_category_distribution(observations):

    return Counter(
        o.observation_category.value
        for o in observations
    )


def observation_platform_distribution(observations):

    return Counter(
        o.source_platform
        for o in observations
    )


def observation_adapter_distribution(observations):

    return Counter(
        o.source_adapter
        for o in observations
    )


def observation_lifecycle_distribution(observations):

    return Counter(
        o.lifecycle.value
        for o in observations
    )


# =============================================================================
# Repository Analytics
# =============================================================================


def contributor_distribution(observations):

    contributors = Counter()

    for observation in observations:

        for actor in observation.actors:

            contributors[actor.id] += 1

    return contributors


def changed_file_distribution(observations):

    files = Counter()

    for observation in observations:

        facts = observation.facts

        if not hasattr(facts, "files"):
            continue

        for file in facts.files:

            files[file.path] += 1

    return files


def directory_distribution(observations):

    directories = Counter()

    for observation in observations:

        facts = observation.facts

        if not hasattr(facts, "files"):
            continue

        for file in facts.files:

            directory = "/".join(
                file.path.split("/")[:-1]
            )

            directories[directory] += 1

    return directories


def extension_distribution(observations):

    extensions = Counter()

    for observation in observations:

        facts = observation.facts

        if not hasattr(facts, "files"):
            continue

        for file in facts.files:

            if "." in file.path:

                ext = file.path.rsplit(".", 1)[-1]

                extensions[ext] += 1

    return extensions


# =============================================================================
# Timeline Analytics
# =============================================================================


def monthly_activity(observations):

    activity = Counter()

    for observation in observations:

        activity[
            observation.timestamp.strftime("%Y-%m")
        ] += 1

    return activity


def weekday_activity(observations):

    activity = Counter()

    for observation in observations:

        activity[
            observation.timestamp.strftime("%A")
        ] += 1

    return activity


def hourly_activity(observations):

    activity = Counter()

    for observation in observations:

        activity[
            observation.timestamp.hour
        ] += 1

    return activity


# =============================================================================
# Measurement Analytics
# =============================================================================


def measurement_category_distribution(measurements):

    return Counter(
        m.category.value
        for m in measurements
    )


def validation_distribution(measurements):

    return Counter(
        m.validation_status.value
        for m in measurements
    )


def confidence_statistics(measurements):

    confidences = [
        m.confidence
        for m in measurements
    ]

    return {

        "average": average(confidences),

        "median": median_value(confidences),

        "minimum": minimum(confidences),

        "maximum": maximum(confidences),

        "stddev": standard_deviation(confidences),

    }


def uncertainty_statistics(measurements):

    values = [

        m.uncertainty

        for m in measurements

    ]

    return {

        "average": average(values),

        "median": median_value(values),

        "minimum": minimum(values),

        "maximum": maximum(values),

        "stddev": standard_deviation(values),

    }


def quality_statistics(measurements):

    values = [

        m.quality

        for m in measurements

    ]

    return {

        "average": average(values),

        "median": median_value(values),

        "minimum": minimum(values),

        "maximum": maximum(values),

        "stddev": standard_deviation(values),

    }


# =============================================================================
# Evidence Analytics
# =============================================================================


def evidence_confidence_statistics(evidence):

    values = [

        e.confidence

        for e in evidence

    ]

    return {

        "average": average(values),

        "median": median_value(values),

        "minimum": minimum(values),

        "maximum": maximum(values),

        "stddev": standard_deviation(values),

    }


def supporting_measurement_distribution(evidence):

    distribution = Counter()

    for ev in evidence:

        distribution[
            len(ev.supporting_measurements)

        ] += 1

    return distribution


# =============================================================================
# Platform Analytics
# =============================================================================


def pipeline_yield(

    observations,

    measurements,

    evidence,

):

    observation_count = len(observations)

    measurement_count = len(measurements)

    evidence_count = len(evidence)

    return {

        "measurements_per_observation":

            measurement_count / max(1, observation_count),

        "evidence_per_measurement":

            evidence_count / max(1, measurement_count),

        "evidence_per_observation":

            evidence_count / max(1, observation_count),

    }