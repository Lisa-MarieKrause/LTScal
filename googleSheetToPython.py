#import library
import gspread

#Service client credential from oauth2client
from oauth2client.service_account import ServiceAccountCredentials

# Print nicely
import pprint

#Create scope
scope = ['https://www.googleapis.com/auth/drive']

#create some credential using that scope and content of keys.json
creds = ServiceAccountCredentials.from_json_keyfile_name('keys.json',scope)

#create gspread authorize using that credential
client = gspread.authorize(creds)

#Now will can access our google sheets we call client.open on StartupName
sheet = client.open('LTS_Mitglieder').sheet1
pp = pprint.PrettyPrinter()

#Access all of the record inside that
result = sheet.get_all_values()
pp.pprint(result[0:10])
result = sheet.row_values(5) #See individual row
result = tuple(result)
print(result)
result_col = sheet.col_values(5) #See individual column
result_cell = sheet.cell(5,2) # See particular cell
pp = pprint.PrettyPrinter()

