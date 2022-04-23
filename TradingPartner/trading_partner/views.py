import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import Dialog
from datetime import datetime
import re

from . import widgets as w
from .constants import FieldTypes as FT

class DataRecordForm(tk.Frame):
  """The input form for our widgets"""

  var_types = {
    FT.string: tk.StringVar,
    FT.string_list: tk.StringVar,
    FT.short_string_list: tk.StringVar,
    FT.iso_date_string: tk.StringVar,
    FT.long_string: tk.StringVar,
    FT.decimal: tk.DoubleVar,
    FT.integer: tk.IntVar,
    FT.boolean: tk.BooleanVar
  }

  _selectCustomer = None
  _selectVendor = None

  def _add_frame(self, label, cols=3):
    """Add a labelframe to the form"""

    frame = ttk.LabelFrame(self, text=label)
    frame.grid(sticky=tk.W + tk.E)
    for i in range(cols):
      frame.columnconfigure(i, weight=1)
    return frame

  def _radio_select(self):
    print('radio')

  def __init__(self, parent, model, settings, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)

    self.model= model
    self.settings = settings
    self.fields = self.model.fields
    self.identifierFields = self.model.identifierFields

    # Create a dict to keep track of input widgets
    self._vars = {
      key: self.var_types[spec['type']]()
      for key, spec in self.fields.items()
    }

    self._identifierVars = {
      key: self.var_types[spec['type']]()
      for key, spec in self.identifierFields.items()
    }

    # Build the form
    self.columnconfigure(0, weight=1)

    # variable to track current record id
    self.current_record = None

    # Label for displaying what record we're editing
    self.record_label = ttk.Label(self)
    self.record_label.grid(row=0, column=0)

    # Record info section
    self.r_info = self._add_frame("Record Information")


    # line 1
    w.LabelInput(
      self.r_info, "取引先区分",
      field_spec=self.fields['identifierType'],
      var=self._vars['identifierType'],
      input_args={
        'values':['customer','vendor']
      }
    ).grid(row=0, column=0)
    w.LabelInput(
      self.r_info, "顧客",
      field_spec=self.identifierFields['customerCodeAndName'],
      var=self._identifierVars['customerCodeAndName']
    ).grid(row=0, column=1)
    w.LabelInput(
      self.r_info, "仕入先",
      field_spec=self.identifierFields['vendorCodeAndName'],
      var=self._identifierVars['vendorCodeAndName']
    ).grid(row=0, column=2)

    # buttons
    buttons = tk.Frame(self)
    buttons.grid(sticky=tk.W + tk.E, row=5)
    self.savebutton = ttk.Button(
      buttons, text="絞込み", command=self._on_filter)
    self.savebutton.pack(side=tk.RIGHT)
    self.resetbutton = ttk.Button(
      buttons, text="リセット", command=self.reset)
    self.resetbutton.pack(side=tk.RIGHT)

    # default the form
    self.reset()

  def _on_filter(self):
    self.event_generate('<<FilterRecord>>')

  @staticmethod
  def tclerror_is_blank_value(exception):
    blank_value_errors = (
      'expected integer but got ""',
      'expected floating-point number but got ""',
      'expected boolean value but got ""'
    )
    is_bve = str(exception).strip() in blank_value_errors
    return is_bve

  def get(self):
    """Retrieve data from form as a dict"""

    # We need to retrieve the data from Tkinter variables
    # and place it in regular Python objects
    data = dict()
    for key, var in self._vars.items():
      try:
        data[key] = var.get()
      except tk.TclError as e:
        if self.tclerror_is_blank_value(e):
          data[key] = None
        else:
          raise e
    for key, var in self._identifierVars.items():
      try:
        data[key] = var.get()
      except tk.TclError as e:
        if self.tclerror_is_blank_value(e):
          data[key] = None
        else:
          raise e
    return data

  def fill_identifiers(self, parent):
    self._selectCustomer = self.model.customerName
    self._selectVendor = self.model.vendorName
    self._selectCustomer = sorted(list(set(self._selectCustomer)),key=lambda x:int(x[:x.index(' ')]))
    self._selectVendor = sorted(list(set(self._selectVendor)),key=lambda x:int(x[:x.index(' ')]))
    # kine 1
    w.LabelInput(
      self.r_info, "顧客",
      field_spec=self.identifierFields['customerCodeAndName'],
      var=self._identifierVars['customerCodeAndName'],
      input_args={
        'values':self._selectCustomer
      }
    ).grid(row=0, column=1)
    w.LabelInput(
      self.r_info, "仕入先",
      field_spec=self.identifierFields['vendorCodeAndName'],
      var=self._identifierVars['vendorCodeAndName'],
      input_args={
        'values':self._selectVendor
      }
    ).grid(row=0, column=2)

  def reset(self):
    """Resets the form entries"""

    # lab = self._vars['Lab'].get()
    # time = self._vars['Time'].get()
    # technician = self._vars['Technician'].get()
    # try:
    #   plot = self._vars['Plot'].get()
    # except tk.TclError:
    #   plot = ''
    # plot_values = self._vars['Plot'].label_widget.input.cget('values')

    # clear all values
    # for var in self._vars.values():
    #   if isinstance(var, tk.BooleanVar):
    #     var.set(False)
    #   else:
    #     var.set('')

    # Autofill Date
    # if self.settings['autofill date'].get():
    #   current_date = datetime.today().strftime('%Y-%m-%d')
    #   self._vars['Date'].set(current_date)
    #   self._vars['Time'].label_widget.input.focus()

    # check if we need to put our values back, then do it.
    # if (
    #   self.settings['autofill sheet data'].get() and
    #   plot not in ('', 0, plot_values[-1])
    # ):
    #   self._vars['Lab'].set(lab)
    #   self._vars['Time'].set(time)
    #   self._vars['Technician'].set(technician)
    #   next_plot_index = plot_values.index(plot) + 1
    #   self._vars['Plot'].set(plot_values[next_plot_index])
    #   self._vars['Seed Sample'].label_widget.input.focus()

  def get_errors(self):
    """Get a list of field errors in the form"""

    errors = dict()
    for key, var in self._vars.items():
      inp = var.label_widget.input
      error = var.label_widget.error

      if hasattr(inp, 'trigger_focusout_validation'):
        inp.trigger_focusout_validation()
      if error.get():
        errors[key] = error.get()

    return errors

  def load_record(self, rownum, data=None):
    self.current_record = rownum
    if rownum is None:
      self.reset()
      self.record_label.config(text='New Record')
    else:
      self.record_label.config(text=f'Record #{rownum}')
      for key, var in self._vars.items():
        var.set(data.get(key, ''))
        try:
          var.label_widget.input.trigger_focusout_validation()
        except AttributeError:
          pass
      for key, var in self._identifierVars.items():
        var.set(data.get(key, ''))
        try:
          var.label_widget.input.trigger_focusout_validation()
        except AttributeError:
          pass

class LoginDialog(Dialog):
  """A dialog that asks for username and password"""

  def __init__(self, parent, title, error=''):

    self._pw = tk.StringVar()
    self._user = tk.StringVar()
    self._error = tk.StringVar(value=error)
    super().__init__(parent, title=title)

  def body(self, frame):
    """Construct the interface and return the widget for initial focus

    Overridden from Dialog
    """
    ttk.Label(frame, text='Login to ABQ').grid(row=0)

    if self._error.get():
      ttk.Label(frame, textvariable=self._error).grid(row=1)
    user_inp = w.LabelInput(
      frame, 'User name:', input_class=w.RequiredEntry,
      var=self._user
    )
    user_inp.grid()
    w.LabelInput(
      frame, 'Password:', input_class=w.RequiredEntry,
      input_args={'show': '*'}, var=self._pw
    ).grid()
    return user_inp.input

  def buttonbox(self):
    box = ttk.Frame(self)
    ttk.Button(
      box, text="Login", command=self.ok, default=tk.ACTIVE
    ).grid(padx=5, pady=5)
    ttk.Button(
      box, text="Cancel", command=self.cancel
    ).grid(row=0, column=1, padx=5, pady=5)
    self.bind("<Return>", self.ok)
    self.bind("<Escape>", self.cancel)
    box.pack()

  def apply(self):
    self.result = (self._user.get(), self._pw.get())

class RecordList(tk.Frame):
  """Display for CSV file contents"""

  column_defs = {
    '#0': {'label': '#', 'width': 60},
    'postingDate':{'label': '記帳日', 'width': 100, 'anchor': tk.W},
    'debitAccountDescription':{'label': '借方科目名', 'width': 100, 'anchor': tk.W},
    'debitAmount':{'label': '借方金額', 'width': 80, 'anchor': tk.E},
    'creditAccountDescription':{'label': '貸方科目名', 'width': 100, 'anchor': tk.W},
    'creditAmount':{'label': '貸方金額', 'width': 80, 'anchor': tk.E},
    'accountSubDescription':{'label': '補助科目', 'width': 80, 'anchor': tk.W},
    'detailComment':{'label': '摘要', 'width': 300, 'anchor': tk.W},
    'identifierDescription':{'label': '取引先', 'width': 180, 'anchor': tk.W},
    'identifierCode':{'label': 'コード', 'width': 40, 'anchor': tk.E},
    'identifierType':{'label': '区分', 'width': 80},
    'accountMainID':{'label': '科目', 'width': 40},
    'entryID':{'label': '登録番号', 'width': 240, 'anchor': tk.W}
  }
  default_width = 100
  default_minwidth = 10
  default_anchor = tk.CENTER

  def __init__(self, parent, *args, **kwargs):
    super().__init__(parent, *args, **kwargs)
    self.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)

    # create treeview
    self.treeview = ttk.Treeview(
      self,
      columns=list(self.column_defs.keys())[1:],
      height=40,
      selectmode='browse'
    )
    self.treeview.grid(row=0, column=0, sticky='NSEW')
    # tag options https://docs.python.org/3/library/tkinter.ttk.html#tag-options
    self.treeview.tag_configure('monospace', font='TkFixedFont') 

    # Configure treeview columns
    for name, definition in self.column_defs.items():
      label = definition.get('label', '')
      anchor = definition.get('anchor', self.default_anchor)
      minwidth = definition.get('minwidth', self.default_minwidth)
      width = definition.get('width', self.default_width)
      stretch = definition.get('stretch', False)
      self.treeview.heading(name, text=label, anchor=anchor)
      self.treeview.column(
        name, anchor=anchor, minwidth=minwidth,
        width=width, stretch=stretch
      )

    self.treeview.bind('<Double-1>', self._on_open_record)
    self.treeview.bind('<Return>', self._on_open_record)

    # configure scrollbar for the treeview
    self.scrollbar = ttk.Scrollbar(
      self,
      orient=tk.VERTICAL,
      command=self.treeview.yview
    )
    self.treeview.configure(yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid(row=0, column=1, sticky='NSW')

  def populate(self, rows):
    """Clear the treeview and write the supplied data rows to it."""
    for row in self.treeview.get_children():
      self.treeview.delete(row)

    cids = self.treeview.cget('columns')
    for rownum, rowdata in enumerate(rows):
      accountMainDescription = rowdata['accountMainDescription']
      amount = rowdata['amount']
      if amount and re.match(r'^[-+]?[0-9]*$',amount):
        amount = int(amount)
        amount = '¥{:,}'.format(amount)
      if re.match(r'^[x\*][0-9]+',rowdata['accountMainID']):
        mark = rowdata['accountMainID'][:1]
      else:
        mark = ''
      rowdata['debitAccountDescription'] = ''
      rowdata['debitAmount'] = ''
      rowdata['creditAccountDescription'] = ''
      rowdata['creditAmount'] = ''
      if 'debit'==rowdata['debitCreditCode']:
        rowdata['debitAccountDescription'] = f'{mark}{accountMainDescription}'
        rowdata['debitAmount'] = amount
      elif 'credit'==rowdata['debitCreditCode']:
        rowdata['creditAccountDescription'] = f'{mark}{accountMainDescription}'
        rowdata['creditAmount'] = amount
      values = [rowdata[cid] for cid in cids]
      if values[list(cids).index('accountMainID')]:
        self.treeview.insert('', 'end', iid=str(rownum), text=str(rownum), values=values)

    if len(rows) > 0:
      self.treeview.focus_set()
      # self.treeview.selection_set('0') # '0' not found
      # self.treeview.focus('0')

  def _on_open_record(self, *args):
    self.event_generate('<<OpenRecord>>')

  @property
  def selected_id(self):
    selection = self.treeview.selection()
    return int(selection[0]) if selection else None