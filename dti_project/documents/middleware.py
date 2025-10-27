from django.utils import timezone
from django.contrib import messages
from .models.collection_models import CollectionReport
from django.utils import timezone
from django.contrib import messages
from documents.models.collection_models import CollectionReport
from django.contrib import messages
from django.utils import timezone
from .models import CollectionReport  # assuming the CollectionReport model is imported

class DailyCollectionReportMiddleware:
    """
    Automatically creates a daily collection report when a collection agent logs in.
    Creates only one report per day.
    Report number format: YY-DDD (e.g., 25-001 for Jan 1, 2025)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        created_report = None

        # Only run for authenticated collection agents
        if request.user.is_authenticated and self.is_collection_agent(request.user):
            created_report = self.ensure_daily_report_exists(request.user)

        response = self.get_response(request)

        # ✅ Show success message only if a new report was created
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
        """Create today's collection report if it doesn't exist, return existing report if it does."""
        today = timezone.localdate()
        year_short = today.strftime("%y")
        day_of_year = today.timetuple().tm_yday  # 1–365 or 366

        # 🔢 Report number format: YY-DDD (zero-padded to 3 digits)
        report_no = f"{year_short}-{day_of_year:03d}"

        # Check if report already exists for this user today
        existing_report = CollectionReport.objects.filter(
            report_collection_date=today,
            name_of_collection_officer=user
        ).first()

        # If report exists, return it without creating a new one
        if existing_report:
            return None  # No new report created

        # If no report exists, create one
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
        """Default certification text."""
        return (
            "I hereby certify that the above is a true and correct report of "
            "collections made by me during the period covered."
        )
