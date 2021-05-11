import calendar
from datetime import date, datetime, timedelta
from typing import Iterable, List, Tuple


class GregorianCalendar:

    MONTH_NAMES = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    @staticmethod
    def setfirstweekday(weekday: int) -> None:
        calendar.setfirstweekday(weekday)

    @staticmethod
    def previous_month_and_year(year: int, month: int) -> Tuple[int, int]:
        previous_month_date = date(year, month, 1) - timedelta(days=2)
        return previous_month_date.month, previous_month_date.year

    @staticmethod
    def next_month_and_year(year: int, month: int) -> Tuple[int, int]:
        last_day_of_month = calendar.monthrange(year, month)[1]
        next_month_date = date(year, month, last_day_of_month) + timedelta(days=2)
        return next_month_date.month, next_month_date.year

    @staticmethod
    def current_date() -> Tuple[int, int, int]:
        today_date = datetime.date(datetime.now())
        return today_date.day, today_date.month, today_date.year

    @staticmethod
    def month_days(year: int, month: int) -> Iterable[date]:
        return calendar.Calendar(calendar.firstweekday()).itermonthdates(year, month)

    @staticmethod
    def month_days_with_weekday(year: int, month: int) -> List[List[int]]:
        return calendar.Calendar(calendar.firstweekday()).monthdayscalendar(year, month)
        
    @staticmethod
    def week_dates(year: int, month: int, day: int) -> Iterable[date]:
        ''' return dates of a week, starting Monday '''
        date = datetime(year, month, day)
        y, w, d = date.isocalendar()
        week_start = date + timedelta(days = -d+1)
        dates = [week_start]
        for i in range(1,7):
            day = week_start + timedelta(days = i)
            dates.append(day)
        return dates
        
    @staticmethod
    def day_of_the_week(day: int, month: int, year: int) -> str:
        '''
            return name of current week day
        '''
        date = datetime(year, month, day)
        week_day = date.weekday()
        if week_day == 0:
                return "Mo"
        if week_day == 1:
                return "Di"
        if week_day == 2:
                return "Mi"
        if week_day == 3:
                return "Do"
        if week_day == 4:
                return "Fr"
        if week_day == 5:
                return "Sa"
        if week_day == 6:
                return "So"
        
        
        
    @staticmethod
    def day_date(day: int, month: int, year: int) -> datetime.date:
        '''
            return date
        '''
        return datetime(year, month, day)
