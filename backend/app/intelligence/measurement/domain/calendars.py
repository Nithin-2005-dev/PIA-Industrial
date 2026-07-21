import datetime
from typing import Protocol, Optional

class ICalendarProvider(Protocol):
    """Protocol for determining working days, allowing for company/region-specific overrides."""
    
    def is_working_day(self, date: datetime.date, entity_id: Optional[str] = None) -> bool:
        """
        Returns True if the date is a valid working day.
        If entity_id is provided, checks for specific employee PTO/Leaves via internal records.
        """
        ...

class StandardBusinessCalendar:
    """Default fallback: Assumes Mon-Fri work week, no public holidays."""
    
    def is_working_day(self, date: datetime.date, entity_id: Optional[str] = None) -> bool:
        # 0 = Monday, 4 = Friday. 5, 6 are Saturday/Sunday.
        return date.weekday() < 5
