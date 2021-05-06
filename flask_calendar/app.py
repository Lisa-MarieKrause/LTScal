#!/usr/bin/python3
import logging
logging.basicConfig(filename='/home/Lii544/Projects/LTScal/pythonanywhere.log',level=logging.DEBUG)
logging.debug(' Loaded logging module')
from datetime import datetime
import locale
logging.debug(': Loaded locale')
import os
logging.debug(': Loaded os')
import git
logging.debug('imported git')
from typing import Dict
logging.debug(': loaded typing')
#import git
import config  # noqa: F401
logging.debug( ': loaded config')
logging.debug('now trying to load flask')
import flask
logging.debug('imported flask')
#from flask import send_from_directory, render_template, request
#logging.debug( ': loaded flask1')
#from flask import Flask as myFlask
#logging.debug(': loaded myFlask')
#from flask import Response
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
)
logging.debug(': loaded flask_calendar.actions')
from flask_calendar.app_utils import task_details_for_markup
logging.debug(': loaded flask_calendar.app_utils')

logging.debug('----------')

def create_app(config_overrides: Dict = None):
    logging.debug(": function create_app running...")
    app = flask.Flask(__name__)
    app.config.from_object("config")

    logging.debug(": setting config")

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    if app.config["LOCALE"] is not None:
        try:
            locale.setlocale(locale.LC_ALL, app.config["LOCALE"])
        except locale.Error as e:
            app.logger.warning("{} ({})".format(str(e), app.config["LOCALE"]))

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    # route configuration for receiving information from GitHub
    @app.route('/update_server', methods=['POST'])
    def webhook():
        if flask.request.method == 'POST':
            repo = git.Repo('/home/Lii544/Projects/LTScal')
            origin = repo.remotes.origin
            origin.pull()
            return 'Updated PythonAnywhere successfully', 200
        else:
            return 'Wrong event type', 400

    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route("/favicon.ico")
    def favicon():
        return flask.send_from_directory(
            os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon",
        )

    app.add_url_rule("/", "index_action", index_action, methods=["GET"])
    app.add_url_rule("/login", "login_action", login_action, methods=["GET"])
    app.add_url_rule("/do_login", "do_login_action", do_login_action, methods=["POST"])
    #TODO:
    app.add_url_rule("/<calendar_id>/<view>", "calendar_view_action", calendar_view_action, methods=["GET"])


    #@app.route("/<calendar_id>/<view>")
    #def calendar_id(calendar_id=None):
        #if key doesn't exist, returns None
        #view = request.args.get("view", app.config["VIEW"])
        #app.view_functions["main_calendar_action"] = main_calendar_action
        #pass
    app.add_url_rule("/<calendar_id>/", "main_calendar_action", main_calendar_action, methods=["GET"])
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/new_task", "new_task_action", new_task_action, methods=["GET"],
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
    logging.debug(": before app.jinja_env")
    app.jinja_env.filters["task_details_for_markup"] = task_details_for_markup
    logging.debug(": before return")
    return app

logging.debug('creating app')
app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
