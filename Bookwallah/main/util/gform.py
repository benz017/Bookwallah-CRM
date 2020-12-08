
from time import sleep
import logging
from celery.contrib import rdb
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from django.conf import settings
from django.apps import apps
import pandas as pd
Config = apps.get_model('main', 'Config')
Recruitment_Form_Config = apps.get_model('main', 'Recruitment_Form_Config')
Recruit = apps.get_model('main', 'Recruit')
now = datetime.now()
SCOPE = ['https://spreadsheets.google.com/feeds',
         "https://www.googleapis.com/auth/spreadsheets.readonly",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.readonly",
         "https://www.googleapis.com/auth/drive.file",
       "https://www.googleapis.com/auth/drive"]
rec_config = Recruitment_Form_Config.objects.all()
config= Config.objects.all()
SECRETS_FILE = settings.MEDIA_ROOT + config.values_list('secret_file', flat=True)[0]
SPREADSHEET = rec_config.values_list('sheet_name', flat=True)[0]
credentials = ServiceAccountCredentials.from_json_keyfile_name(SECRETS_FILE, scopes=SCOPE)
gc = gspread.authorize(credentials)
workbook = gc.open(SPREADSHEET)
sheet = workbook.sheet1
logger = logging.getLogger(__name__)


def fetch_data():
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    data = pd.DataFrame(sheet.get_all_records())
    if not data.empty:
        column_names = {'Timestamp': 'timestamp',
                        rec_config.values_list('username_field', flat=True)[0]: 'username',
                        rec_config.values_list('email_field', flat=True)[0]: 'email',
                        rec_config.values_list('name_field', flat=True)[0]: 'rec_name',
                        rec_config.values_list('address_field', flat=True)[0]: 'address',
                        rec_config.values_list('contact_field', flat=True)[0]: 'contact',
                        rec_config.values_list('tenure_field', flat=True)[0]: 'tenure',
                        rec_config.values_list('role_field', flat=True)[0]: 'role',
                        rec_config.values_list('prior_experience_field', flat=True)[0]: 'prior_exp',
                        rec_config.values_list('library_field', flat=True)[0]: 'library',

                        }
        print(column_names)
        data.rename(columns=column_names, inplace=True)
        data.timestamp = pd.to_datetime(data.timestamp)
        for index, row in data.iterrows():
            if not Recruit.objects.filter(email=row.email):
                Recruit.objects.create(timestamp=row.timestamp, username=row.username, email=row.email,
                                       name=row.rec_name, address=row.address, contact=row.contact, tenure=row.tenure,
                                       role=row.role, prior_exp=row.prior_exp, library=row.library)
            print(row.username, row.rec_name)
        logger.debug(f"{column_names}")
        return True
    else:
        return False