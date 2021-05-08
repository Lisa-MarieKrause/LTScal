import re
import uuid
from functools import wraps
from typing import Any, Callable
import logging
logging.basicConfig(filename='/home/Lii544/Projects/LTScal-pythonanywhere.log',level=logging.DEBUG)
logging.debug(' Loaded logging module in app_utils')
from cachelib.simple import SimpleCache
from flask import abort, current_app, redirect, request
from flask_calendar.authorization import Authorization
from flask_calendar.calendar_data import CalendarData
from flask_calendar.constants import SESSION_ID
from flask_calendar.gregorian_calendar import GregorianCalendar
from datetime import datetime, timedelta

cache = SimpleCache()

# see `app_utils` tests for details, but TL;DR is that urls must start with `http://` or `https://` to match
URLS_REGEX_PATTERN = r"(https?\:\/\/[\w/\-?=%.]+\.[\w/\+\-?=%.~&\[\]\#]+)"
DECORATED_URL_FORMAT = '<a href="{}" target="_blank">{}</a>'


def authenticated(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        session_id = request.cookies.get(SESSION_ID)
        if session_id is None or not is_session_valid(str(session_id)):
            if request.headers.get("Content-Type", "") == "application/json":
                abort(401)
            return redirect("/login")
        return decorated_function(*args, **kwargs)

    return wrapper


def authorized(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        username = get_session_username(str(request.cookies.get(SESSION_ID)))
        authorization = Authorization(calendar_data=CalendarData(data_folder=current_app.config["DATA_FOLDER"]))
        if "calendar_id" not in kwargs:
            raise ValueError("calendar_id")
        calendar_id = str(kwargs["calendar_id"])
        if not authorization.can_access(username=username, calendar_id=calendar_id):
            abort(403)
        return decorated_function(*args, **kwargs)

    return wrapper


def previous_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.previous_month_and_year(year=year, month=month)
    return (
        ""
        if year < current_app.config["MIN_YEAR"] or year > current_app.config["MAX_YEAR"]
        else "?y={}&m={}".format(year, month)
    )


def next_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.next_month_and_year(year=year, month=month)
    return (
        ""
        if year < current_app.config["MIN_YEAR"] or year > current_app.config["MAX_YEAR"]
        else "?y={}&m={}".format(year, month)
    )


def new_session_id() -> str:
    return str(uuid.uuid4())


def is_session_valid(session_id: str) -> bool:
    return cache.get(session_id) is not None


def add_session(session_id: str, username: str) -> None:
    cache.set(session_id, username, timeout=2678400)  # 1 month


def get_session_username(session_id: str) -> str:
    return str(cache.get(session_id))


def task_details_for_markup(details: str) -> str:
    if not current_app.config["AUTO_DECORATE_TASK_DETAILS_HYPERLINK"]:
        return details
        
def calendar_row(start_time: str) -> int:
    '''
        return row number to situate the event
        depends on:
        DAY_START, INTERVAL
    '''
    day_start = current_app.config["DAY_START"]
    interval = current_app.config["INTERVAL"] #in mins
    day_start = datetime.strptime(day_start, '%H:%M')
    start_time = datetime.strptime(start_time, '%H:%M')
    diff = (start_time - day_start).seconds / 60 #mins
    # +1 because there is no rownumber 0
    # +1 because hour labels are written on buttom border
    return int(diff / interval)+2
    
def calendar_span(end_time: str, start_time: str) -> int:
    '''
        return how many rows an event spans
        depends on: INTERVAL
    '''
    start_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')
    interval = current_app.config["INTERVAL"] #in mins
    diff = (end_time - start_time).seconds / 60 #mins
    if diff == 0:
        return -1
    else:
        return int(diff/interval)
    
    
def business_hours(day_start: str, day_end: str, mins: int):
    '''
        return string array of day times
        array begins at day_start o' clock
        array ends at day_end o' clock
        array intervals given in minutes
    '''
    hour = datetime.strptime(day_start, '%H:%M')
    day_end = datetime.strptime(day_end, '%H:%M')
    interval = (day_end - hour).seconds / 60 # total count of minutes
    interval = interval/mins # gives the length of the array
    business_hours = [datetime.strftime(hour, '%H:%M')]
    for i in range(int(interval)):
        hour += timedelta(minutes = mins)
        business_hours.append((datetime.strftime(hour, '%H:%M')))
    return business_hours

    decorated_fragments = []

    fragments = re.split(URLS_REGEX_PATTERN, details)
    for index, fragment in enumerate(fragments):
        if index % 2 == 1:
            decorated_fragments.append(DECORATED_URL_FORMAT.format(fragment, fragment))
        else:
            decorated_fragments.append(fragment)

    return "".join(decorated_fragments)
