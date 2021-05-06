from flask_calendar import app as application

app = application.create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
