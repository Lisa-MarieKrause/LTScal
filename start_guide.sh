#start virtualenvironment
source $HOME/flask-calendar/bin/activate

#start application
uwsgi --http 127.0.0.1:5000 \
  --module flask_calendar.uwsgi \
  --callable app \
  --virtualenv $HOME/flask-calendar
