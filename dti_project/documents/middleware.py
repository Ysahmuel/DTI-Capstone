from django.utils import timezone
from django.contrib import messages
from .models.collection_models import CollectionReport
from django.utils import timezone
from django.contrib import messages
from documents.models.collection_models import CollectionReport
from django.contrib import messages
from django.utils import timezone
from .models import CollectionReport  
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, date

class DailyCollectionReportMiddleware:
    """
    Automatically creates a daily collection report for collection agents.
    Skips weekends (Sat–Sun) and public holidays.
    Report number format: YY-NNN (e.g., 25-001 for the first working day of the year).
    """

    HOLIDAYS = {
        # Static Philippine holidays (MM-DD)
        "01-01",  # New Year’s Day
        "04-09",  # Araw ng Kagitingan
        "05-01",  # Labor Day
        "06-12",  # Independence Day
        "08-26",  # National Heroes Day 
        "11-01",  # All Saints’ Day
        "11-30",  # Bonifacio Day
        "12-25",  # Christmas Day
        "12-30",  # Rizal Day
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        created_report = None

        if request.user.is_authenticated and self.is_collection_agent(request.user):
            created_report = self.ensure_daily_report_exists(request.user)

        response = self.get_response(request)

        if created_report and hasattr(request, "_messages") and not getattr(request, "_messages_added", False):
            messages.success(
                request,
                f"A daily collection report ({created_report.report_no}) has been automatically created for today."
            )
            request._messages_added = True

        return response

    def is_collection_agent(self, user):
        """Check if the user is a collection agent."""
        return hasattr(user, "role") and user.role == "collection_agent"

    def ensure_daily_report_exists(self, user):
        today = timezone.localdate()

        # ⛔ Skip weekends
        if today.weekday() >= 5:
            return None

        # ⛔ Skip holidays
        if today.strftime("%m-%d") in self.HOLIDAYS:
            return None

        # Already has a report for today
        existing_report = CollectionReport.objects.filter(
            report_collection_date=today,
            name_of_collection_officer=user
        ).first()
        if existing_report:
            return None

        # Count all working days (Mon–Fri, not holiday) since Jan 1
        year_short = today.strftime("%y")
        first_day = date(today.year, 1, 1)
        working_days = 0
        current = first_day

        while current <= today:
            if current.weekday() < 5 and current.strftime("%m-%d") not in self.HOLIDAYS:
                working_days += 1
            current += timedelta(days=1)

        report_no = f"{year_short}-{working_days:03d}"

        report = CollectionReport.objects.create(
            report_collection_date=today,
            name_of_collection_officer=user,
            report_no=report_no,
            dti_office=user.dti_office or "DTI Albay Provincial Office",
            official_designation=user.official_designation or "Special Collecting Officer",
            certification=self.get_default_certification(),
        )
        return report

    def get_default_certification(self):
        return (
            "I hereby certify that the above is a true and correct report of "
            "collections made by me during the period covered."
        )
