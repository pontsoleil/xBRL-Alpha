import csv
from pathlib import Path
import os
import json
from decimal import Decimal
from datetime import datetime

from . import views as v
from .constants import FieldTypes as FT

class CSVModel:
  """CSV file storage"""

  fields = {
    "entryID":{
      'req': True, 'type': FT.string
    },
    "g0":{
      'req': False, 'type': FT.string
    },
    "s0":{
      'req': False, 'type': FT.string
    },
    "g1":{
      'req': False, 'type': FT.string
    },
    "s1":{
      'req': False, 'type': FT.string
    },
    "entriesType":{
      'req': False, 'type': FT.string
    },
    "uniqueID":{
      'req': False, 'type': FT.string
    },
    "sourceApplication":{
      'req': False, 'type': FT.string
    },
    "language":{
      'req': False, 'type': FT.string
    },
    "creationDate":{
      'req': False, 'type': FT.iso_date_string
    },
    "creator":{
      'req': False, 'type': FT.string
    },
    "organizationIdentifier":{
      'req': False, 'type': FT.string
    },
    "organizationDescription":{
      'req': False, 'type': FT.string
    },
    "organizationAddressName":{
      'req': False, 'type': FT.string
    },
    "organizationAddressStreet":{
      'req': False, 'type': FT.string
    },
    "organizationAddressZipOrPostalCode":{
      'req': False, 'type': FT.string
    },
    "organizationAddressCountry":{
      'req': False, 'type': FT.string
    },
    "enteredDate":{
      'req': False, 'type': FT.iso_date_string
    },
    "entryOrigin":{
      'req': False, 'type': FT.string
    },
    "sourceJournalID":{
      'req': False, 'type': FT.string
    },
    "sourceJournalDescription":{
      'req': False, 'type': FT.string
    },
    "entryNumber":{
      'req': False, 'type': FT.string
    },
    "entryType":{
      'req': False, 'type': FT.string
    },
    "phoneNumberDescription":{
      'req': False, 'type': FT.string
    },
    "phoneNumber":{
      'req': False, 'type': FT.string
    },
    "accountMainID":{
      'req': False, 'type': FT.string
    },
    "accountMainDescription":{
      'req': False, 'type': FT.string
    },
    "accountType":{
      'req': False, 'type': FT.string
    },
    "accountSubDescription":{
      'req': False, 'type': FT.string
    },
    "accountSubID":{
      'req': False, 'type': FT.string
    },
    "accountSubType":{
      'req': False, 'type': FT.string
    },
    "debitCreditCode":{
      'req': False, 'type': FT.short_string_list,
      'values': ['debit', 'credit']
    },
    "amount":{
      'req': False, 'type': FT.decimal
    },
    "amountCurrency":{
      'req': False, 'type': FT.string
    },
    "postingDate":{
      'req': False, 'type': FT.iso_date_string
    },
    "postingStatus":{
      'req': False, 'type': FT.string
    },
    "xbrlElement":{
      'req': False, 'type': FT.string
    },
    "detailComment":{
      'req': False, 'type': FT.string
    },
    "identifierCode":{
      'req': False, 'type': FT.string_list,
      'values': ['0 すべての取引先']
    },
    "identifierDescription":{
      'req': False, 'type': FT.string
    },
    "identifierType":{
      'req': False, 'type': FT.short_string_list,
      'values': ['customer', 'vendor', 'both']
    }
  }

  identifierFields = {
    "vendorCodeAndName":{
      'req': False, 'type': FT.string_list,
      'values': ['0 すべての仕入先']
    },
    "customerCodeAndName":{
      'req': False, 'type': FT.string_list,
      'values': ['0 すべての販売先']
    }
  }

  accountsFields = {
    'postingDate':{
      'req': False, 'type': FT.string
    },
    'debitAccountDescription':{
      'req': False, 'type': FT.string
    },
    'debitAmount':{
      'req': False, 'type': FT.string
    },
    'creditAccountDescription':{
      'req': False, 'type': FT.string
    },
    'creditAmount':{
      'req': False, 'type': FT.string
    },
    'detailComment':{
      'req': False, 'type': FT.string
    },
    'identifierDescription':{
      'req': False, 'type': FT.string
    },
    'identifierCode':{
      'req': False, 'type': FT.string
    },
    'identifierType':{
      'req': False, 'type': FT.string
    },
    'accountMainID':{
      'req': False, 'type': FT.string
    },
    'entryID':{
      'req': False, 'type': FT.string
    }
  }
  
  CoA = {
    '111':'現金',
    '121':'当座預金',
    '131':'普通預金',
    '143':'定期預金',
    '148':'定期積金',
    '150':'受取手形',
    '152':'売掛金',
    '171':'商品',
    '183':'短期貸付金',
    '191':'仮払消費税等',
    '213':'構築物',
    '216':'工具器具備品',
    '248':'保険積立金',
    '301':'支払手形',
    '312':'買掛金',
    '321':'短期借入金',
    '322':'未払金',
    '326':'預り金',
    '327':'未払事業税等',
    '328':'未払法人税等',
    '335':'仮受消費税等',
    '336':'未払消費税等',
    '341':'長期借入金',
    '511':'売上高',
    '521':'売上値引戻り高',
    '523':'売上割戻し高',
    '531':'期首商品棚卸高',
    '541':'商品仕入高',
    '551':'仕入値引戻し高',
    '561':'期末商品棚卸高',
    '711':'役員報酬',
    '712':'給与手当',
    '713':'賞与',
    '721':'雑給',
    '723':'法定福利費',
    '724':'福利厚生費',
    '726':'旅費交通費',
    '727':'通信費',
    '728':'業務委託費',
    '731':'運賃',
    '732':'広告宣伝費',
    '733':'交際接待費',
    '734':'会議費',
    '736':'水道光熱費',
    '737':'消耗品費',
    '738':'租税公課',
    '739':'新聞図書費',
    '740':'車両費',
    '741':'支払手数料',
    '742':'諸会費',
    '744':'リース料',
    '746':'支払報酬',
    '747':'地代家賃',
    '752':'保険料',
    '753':'修繕維持費',
    '754':'事務用消耗品費',
    '763':'減価償却費',
    '791':'雑費',
    '821':'支払利息',
  }
  
  vendorName = []
  customerName = []
  checkedJournal = {}
  entries = {}
  journals = []
  AP = {}
  AR = {}
  identifierType = None
  identifierCode = None
  qAP = '312'
  qAR = '152'

  def __init__(self, filename=None):

    if not filename:       # datestring = datetime.today().strftime("%Y-%m-%d")
      filename = "TradingPartner/xbrl-instancesUTF16LE.tsv"      # .format(datestring)
    self.file = Path(filename)

    pre, ext = os.path.splitext(filename)
    filename = pre+'_AR.tsv' 
    self.ARfile = Path(filename)
    filename = pre+'_AP.tsv' 
    self.APfile = Path(filename)
    filename = pre+'_Adj.tsv' 
    self.AdjustmentsFfile = Path(filename)
    
    # Check for append permissions:
    file_exists = os.access(self.file, os.F_OK)
    parent_writeable = os.access(self.file.parent, os.W_OK)
    file_writeable = os.access(self.file, os.W_OK)
    if (
      (not file_exists and not parent_writeable) or
      (file_exists and not file_writeable)
    ):
      msg = f'Permission denied accessing file: {filename}'
      raise PermissionError(msg)

  def file_path(pathname):
    if '/' == pathname[0:1]:
      return pathname
    else:
      dir = os.path.dirname(__file__)
      new_path = os.path.join(dir, pathname)
      return new_path

  def save_record(self, data, rownum=None):
    """Save a dict of data to the CSV file"""

    if rownum is None:
      # This is a new record
      newfile = not self.file.exists()
      with open(self.file, 'a', newline='') as fh:
        csvwriter = csv.DictWriter(fh, fieldnames=self.fields.keys())
        if newfile:
          csvwriter.writeheader()
        csvwriter.writerow(data)
    else:
      # This is an update
      records = self.get_all_records()
      records[rownum] = data
      with open(self.file, 'w', encoding='utf-16', newline='') as fh:
        csvwriter = csv.DictWriter(fh, fieldnames=self.fields.keys())
        csvwriter.writeheader()
        csvwriter.writerows(records)

  def save_accounts(self):
    """Save a AR/AP to the CSV file"""
    # AR
    records = []
    for code,data in self.AR.items():
      for d in data:
        record = list(d.values())
        records.append(record)
    fields = list(d.keys())
    with open(self.ARfile, 'w', encoding='utf-16', newline='') as fh:
      csvwriter = csv.writer(fh, delimiter='\t')
      csvwriter.writerow(fields)
      for record in records:
        csvwriter.writerow(record)
    # AP
    records = []
    for code,data in self.AP.items():
      for d in data:
        record = list(d.values())
        records.append(record)
    fields = list(d.keys())
    with open(self.APfile, 'w', encoding='utf-16', newline='') as fh:
      csvwriter = csv.writer(fh, delimiter='\t')
      csvwriter.writerow(fields)
      for record in records:
        csvwriter.writerow(record)

  def save_adjustments(self):
    """Save Adhustments record to the CSV file"""
    records = []
    for code,data in self.adjustments.items():
      for d in data:
        record = list(d.values())
        records.append(record)
    fields = list(d.keys())
    with open(self.AdjustmentsFfile, 'w', encoding='utf-16', newline='') as fh:
      csvwriter = csv.writer(fh, delimiter='\t')
      csvwriter.writerow(fields)
      for record in records:
        csvwriter.writerow(record)

  def get_all_records(self):
    """Read in all records from the CSV and return a list"""
    if not self.file.exists():
      return []

    with open(self.file, 'r', encoding='utf-16') as fh:
      csvreader = csv.DictReader(fh.readlines(), delimiter='\t')
      missing_fields = set(self.fields.keys()) - set(csvreader.fieldnames)
      if len(missing_fields) > 0:
        fields_string = ', '.join(missing_fields)
        raise Exception(
          f"File is missing fields: {fields_string}"
        )
      csv_records = list(csvreader)
      lists = []
      for record in csv_records:
        data = {}
        for k,v in record.items():
          if k:
            data[k]=v
        lists.append(data)
      records = sorted(lists,key=lambda x:f"{x['enteredDate']} {x['entryID']}")
    # Correct issue with boolean fields
    trues = ('true', 'yes', '1')
    bool_fields = [
      key for key, meta
      in self.fields.items()
      if meta['type'] == FT.boolean
    ]
    for record in records:
      for key in bool_fields:
        record[key] = record[key].lower() in trues
    return records

  def get_record(self, rownum):
    """Get a single record by row number

    Callling code should catch IndexError
      in case of a bad rownum.
    """

    return self.get_all_records()[rownum]

  def filter_records(self, conditions):
    """Filter records with conditions from the CSV and return a list"""
    if not self.file.exists():
      return []

    with open(self.file, 'r', encoding='utf-16') as fh:
      csvreader = csv.DictReader(fh.readlines(), delimiter='\t')
      missing_fields = set(self.fields.keys()) - set(csvreader.fieldnames)
      if len(missing_fields) > 0:
        fields_string = ', '.join(missing_fields)
        raise Exception(
          f"File is missing fields: {fields_string}"
        )
      records = list(csvreader)
      records = sorted(records,key=lambda x:f"{x['enteredDate']} {x['entryID']}")
    # Correct issue with boolean fields
    trues = ('true', 'yes', '1')
    bool_fields = [
      key for key, meta
      in self.fields.items()
      if meta['type'] == FT.boolean
    ]
    for record in records:
      for key in bool_fields:
        record[key] = record[key].lower() in trues

    if 'identifierType' in conditions and conditions['identifierType']:
      self.identifierType = conditions['identifierType']
      if 'vendor'==self.identifierType:
        self.identifierCode = conditions['vendorCodeAndName']
      elif 'customer'==self.identifierType:
        self.identifierCode = conditions['customerCodeAndName']
      code = self.identifierCode
      code = code[:code.index(' ')]
    if 'customer'==self.identifierType:
      return self.AR[code]
    elif 'vendor'==self.identifierType:
      return self.AP[code]

class SettingsModel:
  """A model for saving settings"""

  fields = {
    'autofill date': {'type': 'bool', 'value': True},
    'autofill sheet data': {'type': 'bool', 'value': True}
  }

  def __init__(self):
    # determine the file path
    filename = 'abq_settings.json'
    self.filepath = Path.home() / filename

    # load in saved values
    self.load()

  def set(self, key, value):
    """Set a variable value"""
    if (
      key in self.fields and
      type(value).__name__ == self.fields[key]['type']
    ):
      self.fields[key]['value'] = value
    else:
      raise ValueError("Bad key or wrong variable type")

  def save(self):
    """Save the current settings to the file"""
    json_string = json.dumps(self.fields)
    with open(self.filepath, 'w') as fh:
      fh.write(json_string)

  def load(self):
    """Load the settings from the file"""

    # if the file doesn't exist, return
    if not self.filepath.exists():
      return

    # open the file and read in the raw values
    with open(self.filepath, 'r') as fh:
      raw_values = json.loads(fh.read())

    # don't implicitly trust the raw values, but only get known keys
    for key in self.fields:
      if key in raw_values and 'value' in raw_values[key]:
        raw_value = raw_values[key]['value']
        self.fields[key]['value'] = raw_value
