"""The application/controller class for ABQ Data Entry"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import re
# from xmlrpc.server import _DispatchArity1
import mojimoji

from . import views as v
from . import models as m
from .mainmenu import MainMenu

DEBUG = True

class Application(tk.Tk):
  """Application root window"""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Hide window while GUI is built
    self.withdraw()

    # Authenticate
    if not self._show_login():
      self.destroy()
      return

    # show the window
    self.deiconify()

    # Create model
    self.model = m.CSVModel()

    # Load settings
    self.settings = {
      'autofill date': tk.BooleanVar(),
      'autofill sheet data': tk.BooleanVar()
    }
    self.settings_model = m.SettingsModel()
    self._load_settings()

    # Begin building GUI
    self.title("取引先管理")
    self.columnconfigure(0, weight=1)

    # Create the menu
    menu = MainMenu(self, self.settings)
    self.config(menu=menu)
    event_callbacks = {
      '<<FileSelect>>': self._on_file_select,
      '<<FileQuit>>': lambda _: self.quit(),
      '<<ShowRecordlist>>': self._show_recordlist,
      '<<NewRecord>>': self._new_record,
      '<<SaveAccounts>>': self._save_accounts,
      '<<SaveAdjustments>>': self._save_adjustments,
    }
    for sequence, callback in event_callbacks.items():
      self.bind(sequence, callback)
    ttk.Label(
      self,
      text="仕訳データ",
      font=("TkDefaultFont", 16)
    ).grid(row=0)

    # The notebook
    self.notebook = ttk.Notebook(self)
    self.notebook.enable_traversal()
    self.notebook.grid(row=1, padx=10, sticky='NSEW')

    # The data record form
    self.recordform = v.DataRecordForm(self, self.model, self.settings)
    self.recordform.bind('<<FilterRecord>>', self._filter_recordlist)
    self.notebook.add(self.recordform, text='表示条件')

    # The data record list
    self.recordlist = v.RecordList(self)
    self.notebook.insert(0, self.recordlist, text='一覧表示')
    self._populate_recordlist()
    self.recordlist.bind('<<OpenRecord>>', self._open_record)

    self._show_recordlist()

    # status bar
    self.status = tk.StringVar()
    self.statusbar = ttk.Label(self, textvariable=self.status)
    self.statusbar.grid(sticky=(tk.W + tk.E), row=3, padx=10)

    self.records_saved = 0

  def _on_save(self, *_):
    """Handles file-save requests"""

    # Check for errors first
    errors = self.recordform.get_errors()
    if errors:
      self.status.set(
        "Cannot save, error in fields: {}"
        .format(', '.join(errors.keys()))
      )
      message = "Cannot save record"
      detail = "The following fields have errors: \n  * {}".format(
        '\n  * '.join(errors.keys())
      )
      messagebox.showerror(
        title='Error',
        message=message,
        detail=detail
      )
      return False

    data = self.recordform.get()
    rownum = self.recordform.current_record
    self.model.save_record(data, rownum)
    self.records_saved += 1
    self.status.set(
      "{} records saved this session".format(self.records_saved)
    )
    self.recordform.reset()
    self._populate_recordlist()

  def _on_file_select(self, *_):
    """Handle the file->select action"""

    filename = filedialog.asksaveasfilename(
      title='Select the target file for saving records',
      defaultextension='.csv',
      filetypes=[('CSV', '*.csv *.CSV')]
    )
    if filename:
      self.model = m.CSVModel(filename=filename)
      self._populate_recordlist()

  @staticmethod
  def _simple_login(username, password):
    """A basic authentication backend with a hardcoded user and password"""
    return username == 'test' and password == 'pass'

  def _show_login(self):
    """Show login dialog and attempt to login"""
    error = ''
    title = "Login to ABQ Data Entry"
    while True:
      login = v.LoginDialog(self, title, error)
      if not login.result:  # User canceled
        return False
      username, password = login.result
      if self._simple_login(username, password):
        return True
      error = 'Login Failed' # loop and redisplay

  def _load_settings(self):
    """Load settings into our self.settings dict."""

    vartypes = {
      'bool': tk.BooleanVar,
      'str': tk.StringVar,
      'int': tk.IntVar,
      'float': tk.DoubleVar
    }

    # create our dict of settings variables from the model's settings.
    self.settings = dict()
    for key, data in self.settings_model.fields.items():
      vartype = vartypes.get(data['type'], tk.StringVar)
      self.settings[key] = vartype(value=data['value'])

    # put a trace on the variables so they get stored when changed.
    for var in self.settings.values():
      var.trace_add('write', self._save_settings)

  def _save_settings(self, *_):
    """Save the current settings to a preferences file"""

    for key, variable in self.settings.items():
      self.settings_model.set(key, variable.get())
    self.settings_model.save()

  def _show_recordlist(self, *_):
    """Show the recordform"""
    self.notebook.select(self.recordlist)

  def _populate_recordlist(self):
    """Parse rows and populate table in the recordform"""

    def __parseAmount(amount):
      if re.match(r'-?[0-9]+(\.[0-9]+)?',amount):
        amount = int(amount)
      else:
        amount = 0
      return amount

    def __setDrCrAmount(record,entry):
      data = {
        'debitCreditCode':None,
        'accountMainID':None,
        'amount':None,
        'accountMainDescription':None,
        'identifierType':None,
        'identifierCode':None,
        'detailComment':None,
        'entryID':None,
        'g0':None,
        's0':None
      }
      for key in entry.keys():
        if key in [
            'entryID','g0','s0',
            'debitCreditCode','accountMainID','accountMainDescription',
            'identifierType','identifierCode',
            'detailComment'
          ]:
          data[key] = entry[key]
      data['amount'] =  __parseAmount(entry['amount'])
      record[data['debitCreditCode']].append(data)
      return record

    def __switch_correctedEntry(correctedEntry,correctingList,n):
      data = correctingList[n]
      postingDate = data['postingDate']
      accountMainID = data['accountMainID']
      debitCreditCode = data['debitCreditCode']
      identifier = f'{data["identifierType"]}_{data["identifierCode"]}'

      correctingList[n]['accountMainID'] = f'x{accountMainID}'

      correctedData = {}
      for k,v in data.items():
        correctedData[k] = v
      if 'debit'==debitCreditCode:
        debitCreditCode = 'credit'
        correctedData['debitCreditCode'] = debitCreditCode
        correctedData['accountMainID'] = f'*{accountMainID}'
      elif 'credit'==debitCreditCode:
        debitCreditCode = 'debit'
        correctedData['debitCreditCode'] = debitCreditCode
        correctedData['accountMainID'] = f'*{accountMainID}'
      correctingList.append(correctedData)

      if not identifier in correctedEntry:
        correctedEntry[identifier] = {}
      if not postingDate in correctedEntry[identifier]:
        correctedEntry[identifier][postingDate] = {
          'debit':[],
          'credit':[]
        }
      record =  correctedEntry[identifier][postingDate]
      record = __setDrCrAmount(record,correctedData)
      correctedEntry[identifier][postingDate] = record

    # def markRecord(data,accountMainID,mark):
    #   if data['accountMainID']:
    #     data['accountMainID'] += mark
    #   if 'debit'==data['debitCreditCode']:
    #     data['debitAccountDescription'] = f'{mark}{data["accountMainDescription"]}'
    #   elif 'credit'==data['debitCreditCode']:
    #     data['creditAccountDescription'] = f'{mark}{data["accountMainDescription"]}'
    #   data['accountMainID'] = f'{mark}{accountMainID}'
    #   return data

    def __parse_rows(rows):
      rows = sorted(rows,key=lambda x:f"{x['enteredDate']} {x['entryID']}")
      checkedJournal = {}
      for data in rows:
        journal_id = data['entryID']
        if not journal_id in self.model.entries:
          self.model.entries[journal_id] = []
        self.model.entries[journal_id].append(data)
        self.model.journals.append(data)
        if data['identifierCode']:
          identifierCode = data['identifierCode']
          identifierName = data['identifierDescription']
          identifierName = re.sub('㈱','',identifierName)
          identifierName = re.sub(r'\(.*\)','',identifierName)
          identifierName = mojimoji.han_to_zen(identifierName)
          identifierType = data['identifierType']
          # check vendor
          if 'vendor'==identifierType:
            codeAndName = f'{identifierCode} {identifierName}'
            if not codeAndName in self.model.vendorName:
              self.model.vendorName.append(codeAndName)
            if not identifierCode in self.model.AP:
              self.model.AP[identifierCode] = []
            if not journal_id in checkedJournal:
               checkedJournal[journal_id] = set()
            checkedJournal[journal_id].add(f'vendor {identifierCode}')
          # check customer
          elif 'customer'==identifierType:
            codeAndName = f'{identifierCode} {identifierName}'
            if not codeAndName in self.model.customerName:
              self.model.customerName.append(codeAndName)
            if not identifierCode in self.model.AR:
              self.model.AR[identifierCode] = []
            if not journal_id in checkedJournal:
               checkedJournal[journal_id] = set()
            checkedJournal[journal_id].add(f'customer {identifierCode}')

      self.recordform.fill_identifiers(self)

      # self.model.CoA Chart of Accounts
      # '111':'現金',
      # '121':'当座預金',
      # '131':'普通預金',
      # '150':'受取手形',
      # '152':'売掛金',
      # '171':'商品',
      # '191':'仮払消費税等',
      # '301':'支払手形',
      # '312':'買掛金',
      # '335':'仮受消費税等',
      # '511':'売上高',
      # '521':'売上値引戻り高',
      # '523':'売上割戻し高',
      # '541':'商品仕入高',
      # '551':'仕入値引戻し高',
      # '733':'交際接待費',
      # '741':'支払手数料',
      # '821':'支払利息',
      tradingAccounts = ['111','121','131','150','152','191','301','312','335','511','521','523','541','551','733','741','821']
      payableAccount = '312'
      # '312':'買掛金',
      purchaseAccounts = ['111','121','312','541','551','191']
      # '111':'現金'.'121':'当座預金','312':'買掛金','541':'商品仕入高','551':'仕入値引戻し高','191':'仮払消費税等',
      receivableAccount = '152'
      # '152':'売掛金',
      salesAccounts = ['111','121','152','511','521','523','335']
      # '111':'現金','121':'当座預金','152':'売掛金',,'511':'売上高','521':'売上値引戻り高','523':'売上割戻し高','335':'仮受消費税等',
      taxAccounts = ['191','335']
      # '191':'仮払消費税等','335':'仮受消費税等',
      otherAccounts = ['143','148','183','213','216','248','321','322','326','327','328','341','531','561','711','712','713','721','723','724','726','727','728','731','732','734','736','737','738','739','740','742','744','746','747','752','753','754','763','791']
      #
      repurchaseAccounts = ['551']                   # '551':'仕入値引戻し高',
      repurchaseRelated = ['312','551','191']        # '312':'買掛金','551':'仕入値引戻し高','191':'仮払消費税等',
      salesreturnAccounts = ['521','523']            # '521':'売上値引戻り高','523':'売上割戻し高',
      salesreturnRelated = ['152','521','523','335'] # '152':'売掛金','521':'売上値引戻り高','523':'売上割戻し高','335':'仮受消費税等',
      #
      cashAccounts = ['111','121','131','150','152','191','301','312','335','741','821']
      postingDate = ''
      accountMainID = ''
      identifierType = ''
      identifierCode = ''
      repurchase = False
      salesreturn = False
      prev_journal_id = ''
      prev_identifier = ''
      identifier = ''
      correctingList = []
      correctedEntry = {}

      for n in range(len(self.model.journals)):
        data = self.model.journals[n]
        if not data['accountMainID']:
          continue
        if data['detailComment']:
          if data['identifierType']:
            identifierType = data['identifierType']
            identifierCode = data['identifierCode']
          else:
            comment = data['detailComment']
            comment = mojimoji.han_to_zen(comment)
            for x in self.model.vendorName:
              identifierType = 'vendor'
              identifierCode = x[:x.index(' ')]
              identifierName = x[x.index(' ')+1:]
              if identifierName in comment:
                if not journal_id in checkedJournal:
                  checkedJournal[journal_id] = set()
                checkedJournal[journal_id].add(f'vendor {identifierCode}')
                data['identifierType'] = identifierType
                data['identifierCode'] = identifierCode
                break
            for x in self.model.customerName:
              identifierType = 'customer'
              identifierCode = x[:x.index(' ')]
              identifierName = x[x.index(' ')+1:]
              if identifierName in comment:
                if not journal_id in checkedJournal:
                  checkedJournal[journal_id] = set()
                checkedJournal[journal_id].add(f'customer {identifierCode}')
                data['identifierType'] = identifierType
                data['identifierCode'] = identifierCode
                break
        correctingList.append(data)

      for n in range(len(correctingList)):
        data = correctingList[n]
        journal_id = data['entryID']
        accountMainID = data['accountMainID']
        amount = __parseAmount(data['amount'])
        if data['identifierType']:
          identifierType = data['identifierType']
          identifierCode = data['identifierCode']
          identifier = f'{identifierType}_{identifierCode}'
        else:
          identifier = ''
        if prev_journal_id!=journal_id: # or prev_identifier!=identifier:
          identifierType = None
          identifierCode = None
          data_2 = None
          data_1 = None
        if prev_journal_id==journal_id:
          if n > 0: # n - 1
            data_1 = correctingList[n-1]
            accountMainID_1 = data_1['accountMainID']
            amount_1 = data_1['amount']
            if accountMainID_1 in tradingAccounts and \
                accountMainID in tradingAccounts and \
                int(amount_1)==int(amount):
              if data_1['identifierType']:
                identifierType = data_1['identifierType']
                identifierCode = data_1['identifierCode']
                identifier = f'{identifierType}_{identifierCode}'
              elif data['identifierType']:
                identifierType = data['identifierType']
                identifierCode = data['identifierCode']
                identifier = f'{identifierType}_{identifierCode}'
              else:
                continue
              #
              if not data_1['identifierType']:
                data_1['identifierType'] = identifierType
                data_1['identifierCode'] = identifierCode
              if not data['identifierType']:
                data['identifierType'] = identifierType
                data['identifierCode'] = identifierCode

          if n > 1: # n - 2
            data_2 = correctingList[n-2]
            accountMainID_2 = data_2['accountMainID']
            amount_2 = __parseAmount(data_2['amount'])
            if accountMainID_2 in tradingAccounts and \
                accountMainID_1 in tradingAccounts and \
                accountMainID in tradingAccounts and \
                ( \
                  int(amount)==int(amount_2)+int(amount_1) or \
                  int(amount_2)==int(amount_1)+int(amount) or \
                  int(amount_1)==int(amount)+int(amount_2) \
                ):
              if data_2['identifierType']:
                identifierType = data_2['identifierType']
                identifierCode = data_2['identifierCode']
                identifier = f'{identifierType}_{identifierCode}'
              elif data_1['identifierType']:
                identifierType = data_1['identifierType']
                identifierCode = data_1['identifierCode']
                identifier = f'{identifierType}_{identifierCode}'
              elif data['identifierType']:
                identifierType = data['identifierType']
                identifierCode = data['identifierCode']
                identifier = f'{identifierType}_{identifierCode}'
              else:
                continue
              #
              if not data_2['identifierType']:
                data_2['identifierType'] = identifierType
                data_2['identifierCode'] = identifierCode
              if not data_1['identifierType']:
                data_1['identifierType'] = identifierType
                data_1['identifierCode'] = identifierCode
              if not data['identifierType']:
                data['identifierType'] = identifierType
                data['identifierCode'] = identifierCode
        prev_journal_id = journal_id

      for n in range(len(correctingList)):
        data = correctingList[n]
        journal_id = data['entryID']
        accountMainID = data['accountMainID']
        amount = __parseAmount(data['amount'])
        if data['identifierType']:
          identifierType = data['identifierType']
          identifierCode = data['identifierCode']
          identifier = f'{identifierType}_{identifierCode}'
        else:
          identifier = ''
        if prev_journal_id!=journal_id or prev_identifier!=identifier:
          data_2 = None
          data_1 = None
        if prev_journal_id==journal_id and prev_identifier==identifier:
          if n > 0: # n - 1
            data_1 = correctingList[n-1]
            accountMainID_1 = data_1['accountMainID']
            amount_1 = __parseAmount(data_1['amount'])
            if accountMainID_1 in repurchaseRelated and \
                accountMainID in repurchaseRelated and \
                int(amount_1)==int(amount):
              repurchase = False
              if accountMainID_1 in repurchaseAccounts:
                repurchase = True
              elif accountMainID in repurchaseAccounts:
                repurchase = True
              if repurchase:
                __switch_correctedEntry(correctedEntry,correctingList,n-1)
                __switch_correctedEntry(correctedEntry,correctingList,n)
            elif accountMainID_1 in salesreturnRelated and \
                accountMainID in salesreturnRelated and \
                int(amount_1)==int(amount):
              salesreturn = False
              if accountMainID_1 in salesreturnAccounts:
                salesreturn = True
              elif accountMainID in salesreturnAccounts:
                salesreturn = True
              if salesreturn:
                __switch_correctedEntry(correctedEntry,correctingList,n-1)
                __switch_correctedEntry(correctedEntry,correctingList,n)
          if n > 1: # n - 2
            data_2 = correctingList[n-2]
            accountMainID_2 = data_2['accountMainID']
            amount_2 = __parseAmount(data_2['amount'])
            if accountMainID_2 in repurchaseRelated and \
                accountMainID_1 in repurchaseRelated and \
                accountMainID in repurchaseRelated and \
                ( \
                  int(amount)==int(amount_2)+int(amount_1) or \
                  int(amount_2)==int(amount_1)+int(amount) or \
                  int(amount_1)==int(amount)+int(amount_2) \
                ):
              repurchase = False
              if accountMainID_2 in repurchaseAccounts:
                repurchase = True
              elif accountMainID_1 in repurchaseAccounts:
                repurchase = True
              elif accountMainID in repurchaseAccounts:
                repurchase = True
              if repurchase:
                __switch_correctedEntry(correctedEntry,correctingList,n-2)
                __switch_correctedEntry(correctedEntry,correctingList,n-1)
                __switch_correctedEntry(correctedEntry,correctingList,n)
            elif accountMainID_2 in salesreturnRelated and \
                accountMainID_1 in salesreturnRelated and \
                accountMainID in salesreturnRelated and \
                ( \
                  int(amount)==int(amount_2)+int(amount_1) or \
                  int(amount_2)==int(amount_1)+int(amount) or \
                  int(amount_1)==int(amount)+int(amount_2) \
                ):
              salesreturn = False
              if accountMainID_2 in salesreturnAccounts:
                salesreturn = True
              elif accountMainID_1 in salesreturnAccounts:
                salesreturn = True
              elif accountMainID in salesreturnAccounts:
                salesreturn = True
              if salesreturn:
                __switch_correctedEntry(correctedEntry,correctingList,n-2)
                __switch_correctedEntry(correctedEntry,correctingList,n-1)
                __switch_correctedEntry(correctedEntry,correctingList,n)
        prev_journal_id = journal_id
        prev_identifier = identifier

      correctingList = sorted(correctingList,key=lambda x:f"{x['entryID']}_{x['identifierCode']}_{x['s0']}")

      for data in correctingList:
        if data['identifierCode']:
          identifierCode = data['identifierCode']
          identifierType = data['identifierType']
          if 'vendor'==identifierType:
            if identifierCode and not identifierCode in self.model.AP:
              self.model.AP[identifierCode] = []
            self.model.AP[identifierCode].append(data)
          elif 'customer'==identifierType:
            if not identifierCode in self.model.AR:
              self.model.AR[identifierCode] = []
            self.model.AR[identifierCode].append(data)

      cashApplication = {}
      current_date = None
      current_identifier = None
      record = None
      date = None
      for identifier,data in correctedEntry.items():
        identifierType = identifier[:identifier.index('_')]
        identifierCode = identifier[identifier.index('_')+1:]
        current_date = None
        if 'vendor'==identifierType:
          for x in self.model.AP[identifierCode]:
            # if x['accountMainID'] in cashAccounts:
            date = x['postingDate']
            if current_identifier:
              if not current_identifier in cashApplication:
                cashApplication[current_identifier] = {}
              if not current_date in cashApplication[current_identifier]:
                cashApplication[current_identifier][current_date] = []
            if current_date and current_date!=date:
              cashApplication[current_identifier][current_date] = record
              # cashApplication[current_identifier][current_date].append(record)
              record = None
            if not record:
              record = {'postingDate':date,'debit':[],'credit':[]}
            record = __setDrCrAmount(record,x)
            current_date = date
            current_identifier = identifier
        if 'customer'==identifierType:
          for x in self.model.AR[identifierCode]:
            # if x['accountMainID'] in cashAccounts:
            date = x['postingDate']
            if current_identifier:
              if not current_identifier in cashApplication:
                cashApplication[current_identifier] = {}
              if not current_date in cashApplication[current_identifier]:
                cashApplication[current_identifier][current_date] = []
            if current_date and current_date!=date:
              cashApplication[current_identifier][current_date].append(record)
              record = None
            if not record:
              record= {'postingDate':date,'debit':[],'credit':[]}
            record = __setDrCrAmount(record,x)
            current_date = date
            current_identifier = identifier
      # after loop
      if record:
        if not current_identifier in cashApplication:
          cashApplication[current_identifier] = {}
        cashApplication[current_identifier][current_date] = record

      current_date = None
      debitAmounts = None
      creditAmounts = None
      debitAmount = None
      creditAmount = None
      self.model.adjustments = {}
      for identifier,data in correctedEntry.items():
        if identifier not in self.model.adjustments:
          self.model.adjustments[identifier] = []
        identifierType = identifier[:identifier.index('_')]
        identifierCode = identifier[identifier.index('_')+1:]
        for date,v in data.items():
          debitList = v['debit']
          creditList = v['credit']
          identifierCashApp = cashApplication[identifier]
          next_date =list(identifierCashApp.keys())[
            list(identifierCashApp.keys()).index(date)+1:
          ]
          if 'customer'==identifierType:
            cashAppNext = identifierCashApp[next_date[0]][0]
            debitListNext = cashAppNext['debit']
            creditListNext = cashAppNext['credit']
            debitAmounts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in debitList 
              if receivableAccount in x['accountMainID']
            ]
            if len(debitAmounts) > 0:
              debitAmount = debitAmounts[0]['amount']
            creditAmounts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in creditList 
              if receivableAccount in x['accountMainID']
            ]
            if len(creditAmounts) > 0:
              creditAmount = creditAmounts[0]['amount']
            debitAmountsNexts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in debitListNext 
              if receivableAccount in x['accountMainID']
            ]
            if len(debitAmountsNexts) > 0:
              debitAmountsNext = debitAmountsNexts[0]
              correctingEntry = [
                x for x in correctingList 
                if x['entryID']==debitAmountsNext['entryID'] and x['g0']==debitAmountsNext['g0'] and x['s0']==debitAmountsNext['s0']
              ][0]
              correctingEntry['accountMainID'] += '*'
              amount = __parseAmount(correctingEntry['amount'])
              if debitAmount:
                correctingEntry['amount'] = str(amount - 2*debitAmount)
              if creditAmount:
                correctingEntry['amount'] = str(amount + 2*creditAmount)
              self.model.adjustments[identifier].append(correctingEntry)
            creditAmountsNexts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in creditListNext 
              if receivableAccount in x['accountMainID']
            ]
            if len(creditAmountsNexts) > 0:
              creditAmountsNext = creditAmountsNexts[0]
              correctingEntry = [
                x for x in correctingList 
                if x['entryID']==creditAmountsNext['entryID'] and x['g0']==creditAmountsNext['g0'] and x['s0']==creditAmountsNext['s0']
              ][0]
              correctingEntry['accountMainID'] += '*'
              amount = __parseAmount(correctingEntry['amount'])
              if debitAmount:
                correctingEntry['amount'] = str(amount + 2*debitAmount)
              if creditAmount:
                correctingEntry['amount'] = str(amount - 2*creditAmount)
              self.model.adjustments[identifier].append(correctingEntry)
          elif 'customer'==identifierType:
            debitAmounts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in debitList 
              if payableAccount in x['accountMainID']
            ]
            if len(debitAmounts) > 0:
              debitAmount = debitAmounts[0]['amount']
            creditAmounts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in creditList 
              if payableAccount in x['accountMainID']
            ]
            if len(creditAmounts) > 0:
              creditAmount = creditAmounts[0]['amount']
            debitAmountsNexts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in debitListNext 
              if payableAccount in x['accountMainID']
            ]
            if len(debitAmountsNexts) > 0:
              debitAmountsNext = debitAmountsNexts[0]
              correctingEntry = [
                x for x in correctingList 
                if x['entryID']==debitAmountsNext['entryID'] and x['g0']==debitAmountsNext['g0'] and x['s0']==debitAmountsNext['s0']
              ][0]
              correctingEntry['accountMainID'] += '*'
              if debitAmount:
                correctingEntry['amount'] -= str(debitAmount*2)
              if creditAmount:
                correctingEntry['amount'] += str(creditAmount*2)
              self.model.adjustments[identifier].append(correctingEntry)
            creditAmountsNexts = [
              {
                'date':date,
                'amount':x['amount'],'accountMainID':x['accountMainID'],'accountMainDescription':x['accountMainDescription'],
                'entryID':x['entryID'],'g0':x['g0'],'s0':x['s0']
              }
              for x in creditListNext 
              if payableAccount in x['accountMainID']
            ]
            if len(creditAmountsNexts) > 0:
              creditAmountsNext = creditAmountsNexts[0]
              correctingEntry = [
                x for x in correctingList 
                if x['entryID']==creditAmountsNext['entryID'] and x['g0']==creditAmountsNext['g0'] and x['s0']==creditAmountsNext['s0']
              ][0]
              correctingEntry['accountMainID'] += '*'
              if debitAmount:
                correctingEntry['amount'] += str(debitAmount*2)
              if creditAmount:
                correctingEntry['amount'] += str(creditAmount*2)
              self.model.adjustments[identifier].append(correctingEntry)

      # for identifier,records in self.model.adjustments.items():
      #   records = sorted(records.items())
      #   self.model.adjustments[identifier] = records

      if DEBUG:
        print(self.model.adjustments)
        print(self.model.adjustments['customer_13'])

      return correctingList

    try:
      rows = self.model.get_all_records()
    except Exception as e:
      messagebox.showerror(
        title='Error',
        message='Problem reading file',
        detail=str(e)
      )
    else:
      rows = __parse_rows(rows)
      self.recordlist.populate(rows)

  def _save_accounts(self, *_):
    """Save AR/AP"""
    try:
      self.model.save_accounts()
    except Exception as e:
      messagebox.showerror(
        title='Error',
        message='Problem reading file',
        detail=str(e)
      )
    else:
      pass

  def _save_adjustments(self, *_):
    """Save Adjustments"""
    try:
      self.model.save_adjustments()
    except Exception as e:
      messagebox.showerror(
        title='Error',
        message='Problem reading file',
        detail=str(e)
      )
    else:
      pass

  def _new_record(self, *_):
    """Open the record form with a blank record"""
    self.recordform.load_record(None)
    self.notebook.select(self.recordform)

  def _open_record(self, *_):
    """Open the selected id from recordlist in the recordform"""
    rowkey = self.recordlist.selected_id
    try:
      record = self.model.get_record(rowkey)
    except Exception as e:
      messagebox.showerror(
        title='Error', message='Problem reading file', detail=str(e)
      )
    else:
      self.recordform.load_record(rowkey, record)
      self.notebook.select(self.recordform)

  def _filter_recordlist(self, *_):
    """Filter the recordlist and open the recordform"""
    conditions = self.recordform.get()
    try:
      rows = self.model.filter_records(conditions)
    except Exception as e:
      messagebox.showerror(
        title='Error',
        message='Problem reading file',
        detail=str(e)
      )
    else:
      self.recordlist.populate(rows)
      self._show_recordlist()