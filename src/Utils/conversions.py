import datetime as dt

# String in HH:MM:SS format
def stringToDatetime(str_time: str) -> dt.datetime:
    if not str_time:
        return None
    return dt.datetime.combine(dt.date.today(), dt.datetime.strptime(str_time, '%H:%M:%S').time())

def datetimeToString(dt_time: dt.time) -> str:
    if not dt_time:
        return None
    return str(dt_time.strftime('%H:%M:%S'))