import datetime

def get_date_from_string(string):
    date_formats = [
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%m/%d/%y",
        "%b %d, %Y",
        "%b %d, %y",
        "%B %d, %Y",
        "%B %d, %y",
        "%B %d",
        "%b %d",
        ]

    for date_format in date_formats:
        try:
            dt = datetime.datetime.strptime(string, date_format).date()
            if dt.year == 1900:
                dt = dt.replace(datetime.datetime.now().year)
            return dt
        except:
            pass

    raise ValueError("Unrecognized time format")
