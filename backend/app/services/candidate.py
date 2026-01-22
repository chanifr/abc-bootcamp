"""Candidate service for business logic."""

from datetime import date
from dateutil.relativedelta import relativedelta


class CandidateService:
    """Business logic for candidates."""

    @staticmethod
    def calculate_years_of_experience(experiences: list) -> int:
        """
        Calculate total years of experience from experience records.

        Handles overlapping periods and current roles (end_date = None).
        """
        if not experiences:
            return 0

        # Collect all date ranges
        date_ranges = []
        today = date.today()

        for exp in experiences:
            start = exp.start_date
            end = exp.end_date if exp.end_date else today
            date_ranges.append((start, end))

        if not date_ranges:
            return 0

        # Sort by start date
        date_ranges.sort(key=lambda x: x[0])

        # Merge overlapping ranges
        merged = [date_ranges[0]]
        for current_start, current_end in date_ranges[1:]:
            last_start, last_end = merged[-1]

            if current_start <= last_end:
                # Overlapping, merge
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                # Non-overlapping, add new range
                merged.append((current_start, current_end))

        # Calculate total years from merged ranges
        total_months = 0
        for start, end in merged:
            delta = relativedelta(end, start)
            total_months += delta.years * 12 + delta.months

        # Round to nearest year
        return round(total_months / 12)
