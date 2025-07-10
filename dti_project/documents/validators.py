from django.forms import ValidationError

def validate_period(start_date, end_date, start_label='Start date', end_label='End date'):
    if start_date and end_date and start_date >= end_date:
        raise ValidationError(f"{end_label} must be after {start_label}.")