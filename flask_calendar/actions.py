import logging
import platform
if platform.system() == 'Linux':
    logging.basicConfig(filename='/home/Lii544/Projects/LTScal-pythonanywhere.log',level=logging.DEBUG)
else:
        logging.basicConfig(filename='/Users/lisa-mariekrause/Documents/01_Karriere/05_Bootcamps/01_Pipeline_Academy/Project/LTScal-pythonanywhere.log',level=logging.DEBUG)
import re
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple, cast  # noqa: F401

from flask import abort, current_app, g, jsonify, make_response, redirect, render_template, request
from werkzeug.wrappers import Response

import flask_calendar.constants as constants
from flask_calendar.app_utils import (
    add_session,
    authenticated,
    authorized,
    get_session_username,
    new_session_id,
    next_month_link,
    previous_month_link,
    business_hours,
)
from flask_calendar.authentication import Authentication
from flask_calendar.calendar_data import CalendarData
from flask_calendar.gregorian_calendar import GregorianCalendar
from flask_calendar.db import get_db


def get_authentication() -> Authentication:
    logging.debug("starting get_authentication ...")
    auth = getattr(g, "_auth", None)
    if auth is None:
        auth = g._auth = Authentication(
            data_folder=current_app.config["USERS_DATA_FOLDER"],
            password_salt=current_app.config["PASSWORD_SALT"],
            failed_login_delay_base=current_app.config["FAILED_LOGIN_DELAY_BASE"],
        )
    return cast(Authentication, auth)


@authenticated
def index_action() -> Response:
    logging.debug("starting index_action ...")
    username = get_session_username(session_id=str(request.cookies.get(constants.SESSION_ID)))
    authentication = get_authentication()
    user_data = authentication.user_data(username)
    return redirect("/{}/".format(user_data["default_calendar"]))


def login_action() -> Response:
    logging.debug("starting login_action ...")
    return cast(Response, render_template("login.html"))


def do_login_action() -> Response:
    logging.debug("starting do_login_action ...")
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    authentication = get_authentication()

    if authentication.is_valid(username, password):
        session_id = new_session_id()
        add_session(session_id, username)
        response = make_response(redirect("/"))

        cookie_kwargs = {
            "key": constants.SESSION_ID,
            "value": session_id,
            # 1 month
            "max_age": 2678400,
            "secure": current_app.config["COOKIE_HTTPS_ONLY"],
            "httponly": True,
        }

        samesite_policy = current_app.config.get("COOKIE_SAMESITE_POLICY", None)
        # Certain Flask versions don't support 'samesite' param
        if samesite_policy:
            cookie_kwargs.update({"samesite": samesite_policy})

        response.set_cookie(**cookie_kwargs)
        return cast(Response, response)
    else:
        return redirect("/login")

#@authenticated
#@authorized
def main_calendar_action(calendar_id: str) -> Response:
    logging.debug("starting main_calendar_action: %s", calendar_id)
    GregorianCalendar.setfirstweekday(current_app.config["WEEK_STARTING_DAY"])

    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = GregorianCalendar.MONTH_NAMES[month - 1]

    if current_app.config["HIDE_PAST_TASKS"]:
        view_past_tasks = False
    else:
        view_past_tasks = request.cookies.get("ViewPastTasks", "1") == "1"

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    try:
        data = calendar_data.load_calendar(calendar_id)
    except FileNotFoundError:
        logging.debug("failed in main_calendar_action")
        abort(404)

    tasks = calendar_data.tasks_from_calendar(year, month, data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(year, month, data, tasks)

    if not view_past_tasks:
        calendar_data.hide_past_tasks(year, month, tasks)

    if current_app.config["WEEK_STARTING_DAY"] == constants.WEEK_START_DAY_MONDAY:
        weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    else:
        weekdays_headers = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        

    return cast(
        Response,
        render_template(
            "calendar.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            month_name=month_name,
            current_year=current_year,
            current_month=current_month,
            current_day=current_day,
            month_days=GregorianCalendar.month_days(year, month),
            week_days=GregorianCalendar.week_dates(year, month, current_day),
            previous_month_link=previous_month_link(year, month),
            next_month_link=next_month_link(year, month),
            base_url=current_app.config["BASE_URL"],
            tasks=tasks,
            display_view_past_button=current_app.config["SHOW_VIEW_PAST_BUTTON"],
            weekdays_headers=weekdays_headers,
        ),
    )

#@authenticated
#@authorized
def calendar_view_action(calendar_id: str, view: str) -> Response:
    logging.debug("starting calendar_view_action ...")
    GregorianCalendar.setfirstweekday(current_app.config["WEEK_STARTING_DAY"])

    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = GregorianCalendar.MONTH_NAMES[month - 1]
    day_start = current_app.config["DAY_START"]
    day_end = current_app.config["DAY_END"]
    interval = current_app.config["INTERVAL"]
    hours = business_hours(day_start, day_end, interval)

    if current_app.config["HIDE_PAST_TASKS"]:
        view_past_tasks = False
    else:
        view_past_tasks = request.cookies.get("ViewPastTasks", "1") == "1"

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    try:
        data = calendar_data.load_calendar(calendar_id)
    except FileNotFoundError:
        logging.debug("failed here")
        abort(404)

    tasks = calendar_data.tasks_from_calendar(year, month, data)
    logging.debug(tasks)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(year, month, data, tasks)

    if not view_past_tasks:
        calendar_data.hide_past_tasks(year, month, tasks)

    if current_app.config["WEEK_STARTING_DAY"] == constants.WEEK_START_DAY_MONDAY:
        weekdays_headers = ["MO", "DI", "MI", "DO", "FR", "SA", "SO"]
    else:
        weekdays_headers = ["SO", "MO", "DI", "MI", "DO", "FR", "SA"]
    if view == "week":
        weekdays_headers.insert(0, "")
        weekdays_headers.insert(0, "")
        days=GregorianCalendar.week_dates(year, month, current_day)
        days.insert(0,"")
        days.insert(0,"")
        '''
        db = get_db()
        cur = db.execute(
            'SELECT * FROM schedule WHERE date IN {};'.format(tuple([day.strftime('%Y-%m-%d') for day in days]))
        )
        tasks = cur.fetchall()
        cur.close()
        '''
    if view == "day":
        weekdays_headers = GregorianCalendar.day_of_the_week(current_day, current_month, current_year)
        days = [GregorianCalendar.day_date(current_day, current_month, current_year)]
        db = get_db()
        cur = db.execute(
            'SELECT *, ((end_time - start_time)*2) AS duration FROM schedule WHERE date IN ("{}");'.format(days[0].strftime('%Y-%m-%d'))
        ) #*2 because of half hours intervals
        rows = cur.fetchall()
        tasks = [dict(row) for row in rows]
        logging.debug(tasks)
        for task in tasks:
            logging.debug(task["start_time"])
        #for row in rows:
         #   tasks.append(row)
        cur.close()
    else:
        days=GregorianCalendar.month_days(year, month)
    
    return cast(
        Response,
        render_template(
            "calendar.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            month_name=month_name,
            current_year=current_year,
            current_month=current_month,
            current_day=current_day,
            days=days,
            previous_month_link=previous_month_link(year, month),
            next_month_link=next_month_link(year, month),
            base_url=current_app.config["BASE_URL"],
            tasks=tasks,
            display_view_past_button=current_app.config["SHOW_VIEW_PAST_BUTTON"],
            weekdays_headers=weekdays_headers,
            view = view,
            day_start = day_start,
            day_end = day_end,
            interval = interval,
            hours = hours,
        ),
    )


def new_view_task_action(calendar_id: str, year: int, month: int, view: str) -> Response:
    GregorianCalendar.setfirstweekday(current_app.config["WEEK_STARTING_DAY"])

    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = max(min(int(year), current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = max(min(int(month), 12), 1)
    month_names = GregorianCalendar.MONTH_NAMES

    if current_month == month and current_year == year:
        day = current_day
    else:
        day = 1
    day = int(request.args.get("day", day))
    start = request.args.get("start", "10:00", type=str)
    task = {
        "date": CalendarData.date_for_frontend(year, month, day),
        "start_time": start,
        "end_time": current_app.config["DAY_END"], #TODO: maybe start_time + 1hrs
        "repetition_id": 0,
        "court_count": 1,
        "name": "",
        "coach": "",
        "max_participants": "",
        "act_participants": "",
        "color": ""
    }
    
    emojis_enabled = current_app.config.get("EMOJIS_ENABLED", False)
    
    return cast(
        Response,
        render_template(
            "new_task.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            view=view,
            min_year=current_app.config["MIN_YEAR"],
            max_year=current_app.config["MAX_YEAR"],
            month_names=month_names,
            task=task,
            base_url=current_app.config["BASE_URL"],
            editing=False,
            emojis_enabled=emojis_enabled,
            button_default_color_value=current_app.config["BUTTON_CUSTOM_COLOR_VALUE"],
            buttons_colors=current_app.config["BUTTONS_COLORS_LIST"],
            buttons_emojis=current_app.config["BUTTONS_EMOJIS_LIST"] if emojis_enabled else tuple(),
        ),
    )
    
@authenticated
@authorized
def new_task_action(calendar_id: str, year: int, month: int) -> Response:
    GregorianCalendar.setfirstweekday(current_app.config["WEEK_STARTING_DAY"])

    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = max(min(int(year), current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = max(min(int(month), 12), 1)
    month_names = GregorianCalendar.MONTH_NAMES

    if current_month == month and current_year == year:
        day = current_day
    else:
        day = 1
    day = int(request.args.get("day", day))

    task = {
        "date": CalendarData.date_for_frontend(year, month, day),
        "is_all_day": True,
        "repeats": False,
        "details": "",
    }

    emojis_enabled = current_app.config.get("EMOJIS_ENABLED", False)
    
    return cast(
        Response,
        render_template(
            "task.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            min_year=current_app.config["MIN_YEAR"],
            max_year=current_app.config["MAX_YEAR"],
            month_names=month_names,
            task=task,
            base_url=current_app.config["BASE_URL"],
            editing=False,
            emojis_enabled=emojis_enabled,
            button_default_color_value=current_app.config["BUTTON_CUSTOM_COLOR_VALUE"],
            buttons_colors=current_app.config["BUTTONS_COLORS_LIST"],
            buttons_emojis=current_app.config["BUTTONS_EMOJIS_LIST"] if emojis_enabled else tuple(),
        ),
    )


@authenticated
@authorized
def edit_task_action(calendar_id: str, year: int, month: int, day: int, task_id: int) -> Response:
    month_names = GregorianCalendar.MONTH_NAMES
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])

    repeats = request.args.get("repeats") == "1"
    try:
        if repeats:
            task = calendar_data.repetitive_task_from_calendar(
                calendar_id=calendar_id, year=year, month=month, task_id=int(task_id)
            )
        else:
            task = calendar_data.task_from_calendar(
                calendar_id=calendar_id,
                year=year,
                month=month,
                day=day,
                task_id=int(task_id),
            )
    except (FileNotFoundError, IndexError):
        abort(404)

    if task["details"] == "&nbsp;":
        task["details"] = ""

    emojis_enabled = current_app.config.get("EMOJIS_ENABLED", False)

    return cast(
        Response,
        render_template(
            "task.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            day=day,
            min_year=current_app.config["MIN_YEAR"],
            max_year=current_app.config["MAX_YEAR"],
            month_names=month_names,
            task=task,
            base_url=current_app.config["BASE_URL"],
            editing=True,
            emojis_enabled=emojis_enabled,
            button_default_color_value=current_app.config["BUTTON_CUSTOM_COLOR_VALUE"],
            buttons_colors=current_app.config["BUTTONS_COLORS_LIST"],
            buttons_emojis=current_app.config["BUTTONS_EMOJIS_LIST"] if emojis_enabled else tuple(),
        ),
    )


@authenticated
@authorized
def update_task_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    # Logic is same as save + delete, could refactor but can wait until need to change any save/delete logic

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])

    # For creation of "updated" task use only form data
    title = request.form["title"].strip()
    start_date = request.form.get("date", "")
    if len(start_date) > 0:
        fragments = re.split("-", start_date)
        updated_year = int(fragments[0])  # type: Optional[int]
        updated_month = int(fragments[1])  # type: Optional[int]
        updated_day = int(fragments[2])  # type: Optional[int]
    else:
        updated_year = updated_month = updated_day = None
    is_all_day = request.form.get("is_all_day", "0") == "1"
    start_time = request.form["start_time"]
    end_time = request.form.get("end_time", None)
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    color = request.form["color"]
    has_repetition = request.form.get("repeats", "0") == "1"
    repetition_type = request.form.get("repetition_type", "")
    repetition_subtype = request.form.get("repetition_subtype", "")
    repetition_value = int(request.form["repetition_value"])  # type: int
    

    calendar_data.create_task(
        calendar_id=calendar_id,
        year=updated_year,
        month=updated_month,
        day=updated_day,
        title=title,
        is_all_day=is_all_day,
        start_time=start_time,
        end_time=end_time,
        details=details,
        color=color,
        has_repetition=has_repetition,
        repetition_type=repetition_type,
        repetition_subtype=repetition_subtype,
        repetition_value=repetition_value,
    )
    # For deletion of old task data use only url data
    calendar_data.delete_task(
        calendar_id=calendar_id,
        year_str=year,
        month_str=month,
        day_str=day,
        task_id=int(task_id),
    )

    if updated_year is None:
        return redirect("{}/{}/".format(current_app.config["BASE_URL"], calendar_id), code=302)
    else:
        return redirect(
            "{}/{}/?y={}&m={}".format(current_app.config["BASE_URL"], calendar_id, updated_year, updated_month),
            code=302,
        )

def save_new_task_action(calendar_id: str, view: str) -> Response:
    '''
        TODO: hier connection to sqlite aufbauen und mit request form befüllen
    '''
    name = request.form['title']
    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    TC1 = request.form.get('TC1', 0)
    TC2 = request.form.get('TC2', 0)
    TC3 = request.form.get('TC3', 0)
    TC4 = request.form.get('TC4', 0)
    coach = request.form.get('coach', "")
    max_participants = request.form.get('max_participants')
    act_participants = request.form.get('act_participants')
    price = request.form.get('price')
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    color = request.form['color']
    
    repetition_id = request.form.get("repeats", "")
    week = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    for weekday in week:
        repetition_id += str(request.form.get(weekday, ""))
    if repetition_id != "0":
        enddate = request.form.get('repetition_end_date', date)
    
    # create repetion entries
    if len(date) > 0:
        date_fragments = re.split("-", date)
        year = int(date_fragments[0])  # type: Optional[int]
        month = int(date_fragments[1])  # type: Optional[int]
        day = int(date_fragments[2])  # type: Optional[int]
    else:
        year = month = day = None
    dt_date = datetime(year, month, day)
    if enddate:
        dt_enddate = datetime.strptime(enddate, "%Y-%m-%d")
    dates_to_create = [dt_date]
    for rep_day in range(1,8):
        if str(rep_day) in repetition_id:
            rest = (7 % rep_day) - (7 % (dt_date.weekday()+1)) #
            i = 1
            next_date = dt_date + timedelta(days=((i*7) + rest))
            while next_date <= dt_enddate:
                dates_to_create.append(next_date)
                i += 1
                next_date = dt_date + timedelta(days=((i*7) + rest))
    dates_to_create = [datetime.strftime(dat, "%Y-%m-%d") for dat in dates_to_create]
    
    for dat in dates_to_create:
        db = get_db()
        db.execute(
            'INSERT INTO schedule (date, start_time, end_time, repetition_id, repetition_end_date, TC1, TC2, TC3, TC4, name, coach, max_participants, act_participants, price, details, color)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (dat, start_time, end_time, repetition_id, enddate, TC1, TC2, TC3, TC4, name, coach, max_participants, act_participants, price, details, color)
        )
        db.commit()
    return redirect("{}/{}/{}?y={}&m={}".format(current_app.config["BASE_URL"], calendar_id, view, year, month))

#@authenticated
#@authorized
def save_task_action(calendar_id: str) -> Response:
    title = request.form["title"].strip()
    startdate = request.form.get("date", "")
    enddate = request.form.get("enddate", "")

    if len(startdate) > 0:
        date_fragments = re.split("-", startdate)
        year = int(date_fragments[0])  # type: Optional[int]
        month = int(date_fragments[1])  # type: Optional[int]
        day = int(date_fragments[2])  # type: Optional[int]
    else:
        year = month = day = None
    is_all_day = request.form.get("is_all_day", "0") == "1"
    start_time = request.form["start_time"]
    end_time = request.form.get("end_time", None)
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    color = request.form["color"]
    has_repetition = request.form.get("repeats", "0") == "1"
    repetition_type = request.form.get("repetition_type")
    repetition_subtype = request.form.get("repetition_subtype")
    repetition_value = int(request.form["repetition_value"])

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])

    dates_to_create = []  # type: List[Tuple[Optional[int], Optional[int], Optional[int]]]

    # repetitive tasks not supported
    if startdate != enddate and not has_repetition:
        startdate_fragments = re.split("-", startdate)
        enddate_fragments = re.split("-", enddate)
        sdate = date(int(startdate_fragments[0]), int(startdate_fragments[1]), int(startdate_fragments[2]))
        edate = date(int(enddate_fragments[0]), int(enddate_fragments[1]), int(enddate_fragments[2]))
        delta = edate - sdate
        for i in range(delta.days + 1):
            currentdate = re.split("-", str(sdate + timedelta(days=i)))

            year = int(currentdate[0])
            month = int(currentdate[1])
            day = int(currentdate[2])

            dates_to_create.append((year, month, day))
    else:
        dates_to_create.append((year, month, day))

    for date_tuple in dates_to_create:
        year, month, day = date_tuple
        calendar_data.create_task(
            calendar_id=calendar_id,
            year=year,
            month=month,
            day=day,
            title=title,
            is_all_day=is_all_day,
            start_time=start_time,
            end_time=end_time,
            details=details,
            color=color,
            has_repetition=has_repetition,
            repetition_type=repetition_type,
            repetition_subtype=repetition_subtype,
            repetition_value=repetition_value,
        )

    if year is None:
        return redirect("{}/{}/".format(current_app.config["BASE_URL"], calendar_id), code=302)
    else:
        return redirect(
            "{}/{}/?y={}&m={}".format(current_app.config["BASE_URL"], calendar_id, year, month),
            code=302,
        )


@authenticated
@authorized
def delete_task_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    calendar_data.delete_task(
        calendar_id=calendar_id,
        year_str=year,
        month_str=month,
        day_str=day,
        task_id=int(task_id),
    )

    return cast(Response, jsonify({}))

def delete_new_task_action(calendar_id: str, view: str, year: str, month: str, day: str, task_id: str) -> Response:
    '''
        delete task from DB
    '''
    db = get_db()
    db.execute(
        'DELETE FROM schedule WHERE id = {}'.format(int(task_id))
        )
    db.commit()

    return cast(Response, jsonify({}))

@authenticated
@authorized
def update_task_day_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    new_day = request.data.decode("utf-8")

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    calendar_data.update_task_day(
        calendar_id=calendar_id,
        year_str=year,
        month_str=month,
        day_str=day,
        task_id=int(task_id),
        new_day_str=new_day,
    )

    return cast(Response, jsonify({}))


@authenticated
@authorized
def hide_repetition_task_instance_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    calendar_data.hide_repetition_task_instance(
        calendar_id=calendar_id,
        year_str=year,
        month_str=month,
        day_str=day,
        task_id_str=task_id,
    )

    return cast(Response, jsonify({}))
