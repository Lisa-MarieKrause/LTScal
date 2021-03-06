import flask_calendar.constants as constants
import os
import platform

SECRET_TOKEN = os.getenv("SECRET_TOKEN")
DEBUG = True
DATA_FOLDER = "data"
USERS_DATA_FOLDER = "users"

# path of gcp key json file
GCP_KEYFILE = os.getenv("GCP_KEYFILE")
MEMBER_DATA = 'LTS_Mitglieder' #file name of google spreadsheet (Kundenkartei)
INVOICE_TEMPLATE = 'LTS_Rechnungsvorlage' #template for invoices
INVOICE_FOLDER = '11IRdU324nu_hqwcGGk8ORWifRmRLB6ao' #folder_id where to save invoices

if platform.system() == 'Linux':
    BASE_URL = "http://lii544.pythonanywhere.com"
else:
    BASE_URL = "http://0.0.0.0:5000"
MIN_YEAR = 2017
MAX_YEAR = 2200
PASSWORD_SALT = "something random and full of non-standard characters"
HOST_IP = "0.0.0.0"  # set to None for production
LOCALE = "es_ES.UTF-8"
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "Europe/Madrid"

WEEK_STARTING_DAY = constants.WEEK_START_DAY_MONDAY

MONTHS_TO_EXPORT = 6  # currently only used for ICS export

FEATURE_FLAG_ICAL_EXPORT = False

# (base ^ attempts ) second delays between failed logins
FAILED_LOGIN_DELAY_BASE = 2

# If true, will automatically decorate hyperlinks with <a> tags upon rendering them
AUTO_DECORATE_TASK_DETAILS_HYPERLINK = True

SHOW_VIEW_PAST_BUTTON = True

# Of use if SHOW_VIEW_PAST_BUTTON is False
HIDE_PAST_TASKS = False

# Default view (possible: 'day', 'week', 'month') 
VIEW = 'month'

# Default start end end of businessday (for week and day view)
DAY_START = "08:00"
DAY_END = "22:00"
INTERVAL = 30 # in minutes

# days past to keep hidden tasks (future ones always kept) counting all months as 31 days long
DAYS_PAST_TO_KEEP_HIDDEN_TASKS = 62

# don't store cache for static files
SEND_FILE_MAX_AGE_DEFAULT = 0

# Cookies config
COOKIE_HTTPS_ONLY = False
COOKIE_SAMESITE_POLICY = "Lax"

# If to render emoji buttons at the task create/edit page
EMOJIS_ENABLED = True

# Colors for new task buttons
BUTTON_CUSTOM_COLOR_VALUE = "#3EB34F"
BUTTONS_COLORS_LIST = (
    ("#FF4848", "Red"),
    ("#3EB34F", "Green"),
    ("#2966B8", "Blue"),
    ("#808080", "Grey"),
    ("#B05F3C", "Brown"),
    ("#9588EC", "Purple"),
    ("#F2981A", "Orange"),
    ("#3D3D3D", "Black"),
)
# Emojis for new task buttons
BUTTONS_EMOJIS_LIST = (
    "????",
    "????",
    "????",
    "????",
    "????",
    "???????",
    "????",
    "????",
    "????",
    "????",
    "????",
    "???",
    "????"
)

# percent of chance to do a GC-like sweep on save and clean empty and/or past hidden entries.
# values [0, 100] -> Note that 0 disables it, 100 makes it run every time
GC_ON_SAVE_CHANCE = 30
