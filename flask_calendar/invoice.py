from flask_calendar.db import (get_db, get_dict_db)
from datetime import datetime
import json
import re
## for google spreadsheet connection:
import gspread
#Service client credential from oauth2client
from oauth2client.service_account import ServiceAccountCredentials
from flask import current_app
from apiclient import discovery #for workaround until new version of gspread
'''
    WARNING: only 100 api calls to google allowed, may be overridden soon!!
'''

'''
.schema invoice

CREATE VIEW invoice AS

WITH inv_temp AS (
   SELECT
      member.id AS member_id,
      IIF(kid_status, lastname_parent || ", " || surname_parent, lastname || ", " || surname) AS name,
      IIF(kid_status, lastname || ", " || surname, "") AS name2,
      street,
      zip_code,
      city,
      CAST(strftime("%m", date) AS INTEGER) AS inv_month,
      schedule.date AS date,
      schedule.price AS price,
      schedule.coach AS coach,
      schedule.name AS description
     FROM schedule
     JOIN lesson ON schedule.id = lesson.schedule_id
     JOIN member ON lesson.participant_id = member.id
     ),
    inv_stage AS (
    SELECT *,
    (CAST(member_id AS TEXT) || "-" || CAST(inv_month AS TEXT)) AS inv_id,
    MAX(date) OVER (PARTITION BY inv_month ORDER BY member_id ) AS last_date
    FROM inv_temp
    )
 SELECT *, DATE(last_date,"+1 months","weekday 1") AS inv_due_date
 FROM inv_stage;
'''
def deEmojify(text):
    emojis = list(current_app.config['BUTTONS_EMOJIS_LIST'])
    pattern = '"["'
    for emoji in emojis:
        pattern += 'u"' + emoji + '"'
    pattern += '"]"'
    regrex_pattern = re.compile(pattern = pattern[1:-1], flags = re.UNICODE)
    return regrex_pattern.sub(r'',text).lstrip()

def init_new_inv(creds, client, sheet, inv_id: str, name: str):
    '''
        duplicate invoice template for new customer invoice
    '''
    new = ""+ name + inv_id
    invoice_folder = current_app.config['INVOICE_FOLDER']
    #available soon:
    #client.copy(sheet.id, title=new, copy_permissions=True, folder_id=invoice_folder)
    #workaround:
    client.copy(sheet.id, title=new, copy_permissions=True)
    new_sheet_id = client.open(new).id
    drive_service = discovery.build('drive', 'v3', credentials=creds)
    file = drive_service.files().get(fileId=new_sheet_id,
                                 fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    file = drive_service.files().update(fileId=new_sheet_id,
        addParents=invoice_folder,
        removeParents=previous_parents,
        fields='id, parents').execute()
    return new
    
def fill_template(db, creds, client, sheet, member: int, month: int):
    '''
        fill invoice for given members
    '''
    cur = db.execute(
    'SELECT * FROM invoice WHERE inv_month = {} and member_id = {};'.format(month, int(member))
    )
    rows = cur.fetchall()
    inv_data = {}
    #recipient
    recipient = []
    recipient.append([rows[0]["name"]])
    recipient.append([rows[0]["name2"]])
    recipient.append([rows[0]["street"]])
    recipient.append([rows[0]["zip_code"]])
    recipient.append([rows[0]["city"]])
    #invoice
    inv_data["inv_id"] = rows[0]["inv_id"]
    inv_data["inv_date"] = str(datetime.date(datetime.now()))
    inv_data["inv_due_date"] = rows[0]["inv_due_date"]
    #invoice items
    inv_items = []
    for i in range(len(rows)):
        item = []
        item.append(rows[i]["date"])
        item.append(deEmojify(rows[i]["description"]))
        item.append(rows[i]["coach"])
        item.append(rows[i]["price"])
        inv_items.append(item)
    
    inv = init_new_inv(creds, client, sheet, inv_data["inv_id"], recipient[0][0] )
    worksheet = client.open(inv).sheet1
    # fill the cells appropietly
    worksheet.update("recipient", recipient)
    worksheet.update("receipt_id", inv_data["inv_id"])
    worksheet.update("receipt_date", inv_data["inv_date"])
    worksheet.update("receipt_due_date", inv_data["inv_due_date"])
    worksheet.update("inv_items", inv_items)

def create_all_invoices(month: int):
    '''
        return success if invoice gspreads were created
    '''
    scope = ['https://www.googleapis.com/auth/drive'] #Create scope
    #create some credential using that scope and content of keys.json
    key_path = current_app.config['GCP_KEYFILE']
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path,scope)
    #create gspread authorize using that credential
    client = gspread.authorize(creds)
    #Now will can access our google sheets we call client.open
    inv_template = current_app.config['INVOICE_TEMPLATE']
    sheet = client.open(inv_template)
    
    #get members to be billed in that month
    db = get_db()
    cur = db.execute(
    'SELECT DISTINCT member_id FROM invoice WHERE inv_month = {};'.format(month)
    )
    rows = cur.fetchall()
    members = set([row[0] for row in rows]) #returns list of unique member ids
    
    #create dict for each member and fill the template
    for member in members:
        fill_template(db, creds, client, sheet, member, month)
    cur.close()
    
    return "created all invoices for month {}".format(month), 200
    
def create_invoice(month: int, member_id: int):
    '''
        return success if invoice gspreads were created
    '''
    scope = ['https://www.googleapis.com/auth/drive'] #Create scope
    #create some credential using that scope and content of keys.json
    key_path = current_app.config['GCP_KEYFILE']
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path,scope)
    #create gspread authorize using that credential
    client = gspread.authorize(creds)
    #Now will can access our google sheets we call client.open
    inv_template = current_app.config['INVOICE_TEMPLATE']
    sheet = client.open(inv_template)
    
    #get members to be billed in that month
    db = get_db()
    fill_template(db, creds, client, sheet, member_id, month)
    
    return "created invoices for member {} in month {}".format(member_id, month), 200
        
    
