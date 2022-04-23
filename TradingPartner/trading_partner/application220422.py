"""The application/controller class for ABQ Data Entry"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import re
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

    def checkAccountsBalance(accountsBalance, identifier,postingDate,accountMainID):
      if not identifier in accountsBalance:
        accountsBalance[identifier] = {}
      if not postingDate in accountsBalance[identifier]:
        accountsBalance[identifier][postingDate] = {}
      if not accountMainID in accountsBalance[identifier][postingDate]:
        accountsBalance[identifier][postingDate][accountMainID] = {'debit':0,'credit':0}
      return accountsBalance
    
    def _parse_rows(rows):
      rows = sorted(rows,key=lambda x:f"{x['enteredDate']} {x['entryID']}")
      checkedJournal = {}
      for data in rows:
        journal_id = data['entryID']
        # seq = data['s0']
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

      tradingAccounts = ['111','121','131','150','152','191','301','312','335','511','521','541','551','733','741','821']
      purchaseAccounts = ['541','551']
      payableAccount = '312'
      salesAccounts = ['511','521']
      receivableAccount = '152'
      otherAccounts = ['322','711','712','713','721','723','724','726','727','728','731','732','734','736','737','738','739',
                        '740','742','744','746','747','752','753','754','763','791']
      repurchaseAccount = '551'
      repurchaseRelated = ['312','191']
      salesreturnAccount = '523'
      salesreturnRelated = ['152','335']
      postingDate = ''
      accountMainID = ''
      # countAccountSub = 0
      identifierType = ''
      identifierCode = ''
      repurchase = False
      salesreturn = False
      prev_journal_id = ''
      prev_identifier = ''
      identifier = ''
      lists = []
      accountsBalance = {}
      n = 0
      for data in  self.model.journals:
        # if data['accountSubID']:
        #   countAccountSub += 1
        #   data['accountMainID'] = '-'# accountMainID
        #   data['postingDate'] = '-'# postingDate
        #   data['identifierType'] =  '-'#identifierType
        #   data['identifierCode'] = '-'# identifierCode
        #   lists.append(data)
        #   n = len(lists)-1
        # el
        if data['accountMainID']:
          journal_id = data['entryID']
          # countAccountSub = 0
          if prev_journal_id!=journal_id or prev_identifier!=identifier:
            postingDate = ''
            accountMainID = ''
            identifierType = ''
            identifierCode = ''
            repurchase = False
            salesreturn = False
          # if DEBUG:
          #   print(f's0:{data["s0"]} s1:{data["s1"]} accountMainID:{data["accountMainID"]} prev:{accountMainID}\t{data["debitCreditCode"]}\t{data["amount"]}\t{identifierType} {identifierCode}\tjournal_id:{journal_id}')
          if data['detailComment']:
            if data['identifierType']:
              identifierType = data['identifierType']
              identifierCode = data['identifierCode']
            else:
              comment = data['detailComment']
              comment = mojimoji.han_to_zen(comment)
              for x in self.model.vendorName:
                identifierType = 'vendor'
                identifierName = x[x.index(' ')+1:]
                if identifierName in comment:
                  identifierCode = x[:x.index(' ')]
                  if not journal_id in checkedJournal:
                    checkedJournal[journal_id] = set()
                  checkedJournal[journal_id].add(f'vendor {identifierCode}')
                  data['identifierType'] = identifierType
                  data['identifierCode'] = identifierCode
                  continue
              for x in self.model.customerName:
                identifierType = 'customer'
                identifierName = x[x.index(' ')+1:]
                if identifierName in comment:
                  identifierCode = x[:x.index(' ')]
                  if not journal_id in checkedJournal:
                    checkedJournal[journal_id] = set()
                  checkedJournal[journal_id].add(f'customer {identifierCode}')
                  data['identifierType'] = identifierType
                  data['identifierCode'] = identifierCode
                  continue
          if not data['identifierCode']:
            if data['accountMainID'] in otherAccounts or accountMainID in otherAccounts:
              identifierCode = ''
            elif identifierCode and \
                 data['accountMainID'] in tradingAccounts and \
                 (accountMainID and not accountMainID in otherAccounts):
              data['identifierType'] = identifierType
              data['identifierCode'] = identifierCode
          lists.append(data)
          n = len(lists)-1
          # if DEBUG:
          #   print(f's0:{data["s0"]} s1:{data["s1"]} accountMainID:{data["accountMainID"]}\t{data["debitCreditCode"]}\t{data["amount"]}\t{data["identifierType"]} {data["identifierCode"]}\tjournal_id:{journal_id}')
          prev_journal_id = journal_id
          accountMainID = data['accountMainID']
          postingDate = data['postingDate']
          if data['identifierType']:
            identifier = f"{data['identifierType']}_{data['identifierCode']}"
          else:
            identifier = ''
          prev_identifier = identifier

          # if n > countAccountSub+2:
          #   i = n - 1
          #   while not lists[i]['amount']:
          #     i -= 1
          #   data1 = lists[i]
          #   i -= 1
          #   while not lists[i]['amount']:
          #     i -= 1
          #   data0 = lists[i]
          if n > 2:
            data0 = lists[n-2]
            data1 = lists[n-1]
            if payableAccount==accountMainID and \
                data0['accountMainID'] in purchaseAccounts and \
                int(data['amount'])==int(data0['amount'])+int(data1['amount']):
              data0['identifierType'] = identifierType
              data0['identifierCode'] = identifierCode
              data1['identifierType'] = identifierType
              data1['identifierCode'] = identifierCode
            elif receivableAccount==accountMainID and \
                data0['accountMainID'] in salesAccounts and \
                int(data['amount'])==int(data0['amount'])+int(data1['amount']):
              data0['identifierType'] = identifierType
              data0['identifierCode'] = identifierCode
              data1['identifierType'] = identifierType
              data1['identifierCode'] = identifierCode
          # check repurchase or salesreturn
          data = lists[n]
          # postingDate = data['postingDate']
          if not accountMainID in repurchaseRelated:
            repurchase = False
          if not accountMainID in salesreturnRelated:
            salesreturn = False
          #
          # repurchase
          #
          if repurchaseAccount==accountMainID or repurchase:
            repurchase = True
            debitCreditCode = data['debitCreditCode']
            accountMainID = data["accountMainID"]
            correctData = {}
            for k,v in data.items():
              correctData[k] = v
            if 'debit'==debitCreditCode:
              correctData['debitCreditCode'] = 'credit'
              correctData['accountMainID'] = f'*{accountMainID}'
            elif 'credit'==debitCreditCode:
              correctData['debitCreditCode'] = 'debit'
              correctData['accountMainID'] = f'*{accountMainID}'
            data['accountMainID'] = f'x{data["accountMainID"]}'
            if ''==correctData['amount']:
              amount = None
            else:
              amount = int(correctData['amount'])
            accountsBalance = checkAccountsBalance(accountsBalance,identifier,postingDate,accountMainID)
            accountsBalance[identifier][postingDate][accountMainID][correctData['debitCreditCode']] = amount
            lists.append(correctData)
            n = len(lists)-1
            # if DEBUG:
            #   print(f'data  s0:{data["s0"]} s1:{data["s1"]} accountMainID:{data["accountMainID"]}\t{data["debitCreditCode"]}\t{data["amount"]}\t{data["identifierType"]} {data["identifierCode"]}')
            #   print(f'crrct s0:{correctData["s0"]} s1:{correctData["s1"]} accountMainID:{correctData["accountMainID"]}\t{correctData["debitCreditCode"]}\t{correctData["amount"]}\t{correctData["identifierType"]} {correctData["identifierCode"]}')
            if repurchaseAccount==accountMainID:
              i = n - 1
              while not lists[i]['amount']:
                i -= 1
              data1 = lists[i]
              i -= 1
              while not lists[i]['amount']:
                i -= 1
              data0 = lists[i]
              debitCreditCode0 = data0['debitCreditCode']
              accountMainID0 = data0["accountMainID"]
              correctData = {}
              for k,v in data0.items():
                correctData[k] = v
              if 'debit'==debitCreditCode0:
                correctData['debitCreditCode'] = 'credit'
                correctData['accountMainID'] = f'*{accountMainID0}'
              elif 'credit'==debitCreditCode0:
                correctData['debitCreditCode'] = 'debit'
                correctData['accountMainID'] = f'*{accountMainID0}'
              data0['accountMainID'] = f'x{data0["accountMainID"]}'
              if ''==correctData['amount']:
                amount = None
              else:
                amount = int(correctData['amount'])
              accountsBalance = checkAccountsBalance(accountsBalance,identifier,postingDate,accountMainID0)
              accountsBalance[identifier][postingDate][accountMainID0][correctData['debitCreditCode']] = amount
              lists.append(correctData)
              n = len(lists)-1
              # if DEBUG:
              #   print(f'data0 s0:{data0["s0"]} s1:{data0["s1"]} accountMainID:{data0["accountMainID"]}\t{data0["debitCreditCode"]}\t{data0["amount"]}\t{data0["identifierType"]} {data0["identifierCode"]}')
              #   print(f'crrct s0:{correctData["s0"]} s1:{correctData["s1"]} accountMainID:{correctData["accountMainID"]}\t{correctData["debitCreditCode"]}\t{correctData["amount"]}\t{correctData["identifierType"]} {correctData["identifierCode"]}')
          #
          # salesreturn
          #
          elif salesreturnAccount==accountMainID or salesreturn:
            salesreturn = True
            debitCreditCode = data['debitCreditCode']
            accountMainID = data["accountMainID"]
            correctData = {}
            for k,v in data.items():
              correctData[k] = v
            if 'debit'==data['debitCreditCode']:
              correctData['debitCreditCode'] = 'credit'
              correctData['accountMainID'] = f'*{accountMainID}'
            elif 'credit'==data['debitCreditCode']:
              correctData['debitCreditCode'] = 'debit'
              correctData['accountMainID'] = f'*{accountMainID}'
            data['accountMainID'] = f'x{data["accountMainID"]}'
            if ''==correctData['amount']:
              amount = None
            else:
              amount = int(correctData['amount'])
            accountsBalance = checkAccountsBalance(accountsBalance,identifier,postingDate,accountMainID)
            accountsBalance[identifier][postingDate][accountMainID][correctData['debitCreditCode']] = amount
            lists.append(correctData)
            n = len(lists)-1
            # if DEBUG:
            #   print(f'data  s0:{data["s0"]} s1:{data["s1"]} accountMainID:{data["accountMainID"]}\t{data["debitCreditCode"]}\t{data["amount"]}\t{data["identifierType"]} {data["identifierCode"]}')
            #   print(f'crrct s0:{correctData["s0"]} s1:{correctData["s1"]} accountMainID:{correctData["accountMainID"]}\t{correctData["debitCreditCode"]}\t{correctData["amount"]}\t{correctData["identifierType"]} {correctData["identifierCode"]}')

      if DEBUG:
        print(accountsBalance)

      for data in lists:
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

      return lists

    try:
      rows = self.model.get_all_records()
    except Exception as e:
      messagebox.showerror(
        title='Error',
        message='Problem reading file',
        detail=str(e)
      )
    else:
      rows = _parse_rows(rows)
      self.recordlist.populate(rows)

  def _save_accounts(self, *_):
    """save AR/AP"""

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