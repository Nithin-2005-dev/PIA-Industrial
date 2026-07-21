from abc import ABC, abstractmethod

from app.intelligence.expertise_profile import (
    ExpertiseProfile,
)


class ExpertiseMappingPolicy(
    ABC
):

    @abstractmethod
    def build_profiles(
        self,
        expertise_estimates,
    ) -> list[ExpertiseProfile]:
        pass