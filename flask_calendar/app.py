#!/usr/bin/python3
import logging
import platform
if platform.system() == 'Linux':
    logging.basicConfig(filename='/home/Lii544/Projects/LTScal-pythonanywhere.log',level=logging.DEBUG)
else:
        logging.basicConfig(filename='/Users/lisa-mariekrause/Documents/01_Karriere/05_Bootcamps/01_Pipeline_Academy/Project/LTScal-pythonanywhere.log',level=logging.DEBUG)
from datetime import datetime
import locale
import os
import git # CD/CI with GitHub
import hmac # Securing the webhook
import hashlib # Securing the webhook
from typing import Dict
import config  # noqa: F401
logging.debug( ': loaded config')
logging.debug('now trying to load flask')
import flask
logging.debug('imported flask')
from flask_calendar.actions import (
    delete_task_action,
    do_login_action,
    edit_task_action,
    hide_repetition_task_instance_action,
    index_action,
    login_action,
    main_calendar_action,
    new_task_action,
    save_task_action,
    update_task_action,
    update_task_day_action,
    calendar_view_action,
    new_view_task_action,
    save_new_task_action
)
from flask_calendar.app_utils import (
    task_details_for_markup,
    calendar_row,
    calendar_span
)

# define instance path (containing sqlite DB) relative to operating system
if platform.system() == 'Linux':
    instace_path="/home/Lii544/Projects/LTScal/instance"
else:
    instance_path="/Users/lisa-mariekrause/Documents/01_Karriere/05_Bootcamps/01_Pipeline_Academy/Project/LTScal/instance"

def create_app(config_overrides: Dict = None):
    logging.debug(": function create_app running...")
    
    app = flask.Flask(__name__, instance_path=instance_path)
    app.config.from_object("config")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    if app.config["LOCALE"] is not None:
        try:
            locale.setlocale(locale.LC_ALL, app.config["LOCALE"])
        except locale.Error as e:
            app.logger.warning("{} ({})".format(str(e), app.config["LOCALE"]))

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['DATABASE']=os.path.join(app.instance_path, 'LTS.sqlite')

    # route configuration for receiving information from GitHub
    def is_valid_signature(x_hub_signature, data, private_key):
        # x_hub_signature and data are from the webhook payload
        # private key is your webhook secret
        hash_algorithm, github_signature = x_hub_signature.split('=', 1)
        algorithm = hashlib.__dict__.get(hash_algorithm)
        encoded_key = bytes(private_key, 'latin-1')
        mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
        return hmac.compare_digest(mac.hexdigest(), github_signature)
    
    #TODO: add more checks (see W10 Github Actions)
    def webhook():
        logging.debug("starting webhook()")
        abort_code = 418
        if flask.request.method in ['POST', 'GET']:
            logging.debug("webhook method = POST")
            repo = git.Repo('/home/Lii544/Projects/LTScal')
            
            x_hub_signature = flask.request.headers.get('X-Hub-Signature')
            w_secret = os.environ['SECRET_TOKEN']
            if not is_valid_signature(x_hub_signature, flask.request.data, w_secret):
                print('Deploy signature failed:{sig}'.format(sig=x_hub_signature))
                flask.abort(abort_code)
            
            origin = repo.remotes.origin
            origin.pull()
            return 'Updated PythonAnywhere successfully by POST', 200
        else:
            logging.debug("webhook method <> POST")
            return 'Wrong event type', 400
            
    # TODO: think about a solution how to split between public and coach
    def index():
        return flask.redirect("/sample/week")
    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route("/favicon.ico")
    def favicon():
        return flask.send_from_directory(
            os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon",
        )
    app.add_url_rule("/server/update", "webhook", webhook, methods=["POST", "GET"])
    app.add_url_rule("/", "index", index, methods=["GET"])
    #app.add_url_rule("/", "index_action", index_action, methods=["GET"])
    app.add_url_rule("/login", "login_action", login_action, methods=["GET"])
    app.add_url_rule("/do_login", "do_login_action", do_login_action, methods=["POST"])
    app.add_url_rule("/<calendar_id>/<view>", "calendar_view_action", calendar_view_action, methods=["GET"])

    app.add_url_rule("/<calendar_id>/", "main_calendar_action", main_calendar_action, methods=["GET"])
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/new_task", "new_task_action", new_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<view>/new_task", "new_view_task_action", new_view_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "edit_task_action", edit_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/task/<task_id>",
        "update_task_action",
        update_task_action,
        methods=["POST"],
    )
    #this is the new one which will save in sqlite db
    app.add_url_rule(
        "/<calendar_id>/<view>/new_task", "save_new_task_action", save_new_task_action, methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/new_task", "save_task_action", save_task_action, methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "delete_task_action", delete_task_action, methods=["DELETE"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/",
        "update_task_day_action",
        update_task_day_action,
        methods=["PUT"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/hide/",
        "hide_repetition_task_instance_action",
        hide_repetition_task_instance_action,
        methods=["POST"],
    )
    
    # setting jinja filters for in-html-usage
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.filters["task_details_for_markup"] = task_details_for_markup
    app.jinja_env.filters["calendar_row"] = calendar_row
    app.jinja_env.filters["calendar_span"] = calendar_span
    
    from . import db
    db.init_app(app)
    
    return app

logging.debug('creating app')
app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
