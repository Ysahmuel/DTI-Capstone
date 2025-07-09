def get_full_name_from_personal_data(obj):
    """ Combines last_name and first_name from a related `personal_data_sheet` field. """
    try:
        pds = obj.personal_data_sheet
        return f"{pds.first_name} {pds.middle_name if pds.middle_name else ''} {pds.last_name}"
    except AttributeError:
        return f"(No name)"
    
