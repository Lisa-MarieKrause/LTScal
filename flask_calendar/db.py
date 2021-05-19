import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

## for google spreadsheet connection:
import gspread
#Service client credential from oauth2client
from oauth2client.service_account import ServiceAccountCredentials 

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@click.command('load-members')
@with_appcontext
def load_gspread_member():
    scope = ['https://www.googleapis.com/auth/drive'] #Create scope
    #create some credential using that scope and content of keys.json
    key_path = current_app.config['GCP_KEYFILE']
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path,scope)
    #create gspread authorize using that credential
    client = gspread.authorize(creds)
    #Now will can access our google sheets we call client.open
    members = current_app.config['MEMBER_DATA']
    sheet = client.open(members).sheet1
    
    #get all entries:
    members = sheet.get_all_values()
    for member in members[1:]:
        db = get_db()
        db.execute(
        'INSERT INTO member (lastname, surname, title, active_status, gender, birthdate, kid_status, lastname_parent, surname_parent, title_parent, greeting, street, zip_code, city, tel_number1, tel_number2, email_address1, email_address2, notes, entered_at, updated_at)'
        ' VALUES (?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?,?, ?);', tuple(member)
        )
        db.commit()
    click.echo("loaded member spreadsheet into database.")

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''
        clear the existing data and create new tables.
    '''
    init_db()
    click.echo("initialized the database.")
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_gspread_member)
