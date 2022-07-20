#!/usr/bin/env python3
#coding: utf-8
#
# generate Open Peoopl e-Invoice (xBRL) fron CSV file
#
# designed by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)
# written by SAMBUICHI, Nobuyuki (Sambuichi Professional Engineers Office)
#
# MIT License
#
# (c) 2022 SAMBUICHI Nobuyuki (Sambuichi Professional Engineers Office)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import xml.etree.ElementTree as ET
import datetime
from collections import defaultdict
import csv
import re
import json
import sys
import os
import argparse
import math

# DEBUG = None
SEP = os.sep

datatypeMap = {
    'Unit Price Amount': 'amount',
    'Code': 'string',
    'issue_date': 'string',
    'Binary object': 'string',
    'Date': 'string',
    'Time': 'string',
    'Identifier': 'string',
    'Quantity': 'numeric',
    'Amount': 'amount',
    'Document Reference': 'string',
    'Text': 'string',
    'Percentage': 'numeric',
    'ー': ''
}

dimensionMap = {
    'ibg-16': 'paymentInstruction',
    'ibg-20': 'invoiceAllowance',
    'ibg-21': 'invoiceCharge',
    'ibg-23': 'taxBreakdown',
    'ibg-24': 'additionalSupportingDocument',
    'ibg-25': 'invoiceLine',
    'ibg-27': 'lineAllowance',
    'ibg-28': 'lineCharge',
    'ibg-32': 'itemAttribute',
    'ibg-33': 'invoiceTerms',
    'ibg-35': 'paidAmount'
}

taxDimension = ['ibg-20', 'ibg-21', 'ibg-23', 'ibg-25']
taxCategoryCode = ['ibt-118', 'ibt-192', 'ibt-151']
taxRates = ['ibt-119', 'ibt-193', 'ibt-152']
lineTermGroups = ['ibg-25', 'ibg-27', 'ibg-28', 'ibg-32']

invoice_number = ''
issue_date = ''
invoice_currency = ''
tax_currency = ''
payment_means_type_code = ''
seller_id = ''
line_id = ''
context_id = ''
invoicedItemTaxCategoryCode = None
invoicedItemTaxRate = None
lines = []

def file_path(pathname):
    if '/' == pathname[0:1]:
        return pathname
    else:
        dir = os.path.dirname(__file__)
        new_path = os.path.join(dir, pathname)
        return new_path

def to_iso_date_format(dt_string):
    format = None
    if re.match(r'[\d]{2,4}/[\d]{1,2}/[\d]{1,2}', dt_string):
        format = '%Y/%m/%d'
    elif re.match(r'[\d]{2,4}-[\d]{1,2}-[\d]{1,2}', dt_string):
        format = '%Y-%m-%d'
    if format:
        dt_object = datetime.datetime.strptime(dt_string, format)
        dt_formatted = dt_object.isoformat()[:10]
    else:
        dt_formatted = dt_string
    return dt_formatted

def set_context_entity_date():
    global lines
    global context_id
    global seller_id
    global issue_date
    lines.append(f'  <xbrli:context id="{context_id}">\n')
    lines.append(f'    <xbrli:entity>\n')
    lines.append(
        f'      <xbrli:identifier scheme="http://www.xbrl.jp/eipa/test/invoice">{seller_id}</xbrli:identifier>\n')
    lines.append(f'    </xbrli:entity>\n')
    lines.append(f'    <xbrli:period>\n')
    lines.append(f'      <xbrli:instant>{issue_date}</xbrli:instant>\n')
    lines.append(f'    </xbrli:period>\n')

def setup_record(record):
    global invoice_number
    global line_id
    global issue_date
    global invoice_currency
    global tax_currency
    global seller_id
    global lines
    global context_id
    for i in range(len(record)):
        data = record[i]
        if not data:
            continue
        id = header[i].lower()
        if 'ibt-001' == id:
            invoice_number = data
        elif 'ibt-002' == id:
            issue_date = to_iso_date_format(data)
        elif 'ibt-005' == id:
            invoice_currency = data
        elif 'ibt-006' == id:
            tax_currency = data
        elif 'ibt-031' == id:
            seller_id = data

def set_context(record):
    global invoice_number
    global issue_date
    global invoice_currency
    global tax_currency
    global seller_id
    global payment_means_type_code
    global line_id
    global context_id
    global invoicedItemTaxCategoryCode
    global invoicedItemTaxRate
    global lines
    head = record[:3*boughLvl]
    tail = record[3*boughLvl:]
    context_id = ''
    taxCategory = ''
    taxRate = ''
    start = 3*boughLvl
    dimensions = []

    context_id = f'_380_{invoice_number}'
    for i in range(boughLvl):
        if not head[3*i]:
            continue
        if head[3*i] in dimensionMap:
            id = head[3*i]
            if head[3*i+2]:
                if 'ibg-23' == id:
                    continue
                else:
                    val = head[3*i+2]
                if id in dimensionMap.keys():
                    term = f'G{id[4:6]}'
                    if 'G16'==term: # PaymentInstruction
                        for idx in range(start, len(header)):
                            id = header[idx]
                            data = record[idx]
                            if data and 'ibt-081' == id:
                                payment_means_type_code = data
                                val = payment_means_type_code
                                break
                    elif 'G25'==term: # InvoiceLine
                        for idx in range(start, len(header)):
                            id = header[idx]
                            data = record[idx]
                            if data and 'ibt-126' == id:
                                line_id = data
                                break
                else:
                    term = f'G{id[4:6]}'
                if re.match('.*G25_[^_]*$', context_id):
                    context_id = re.sub(
                        r'(.*)G25_(.*)', r'\1G25_'+line_id, context_id)
                context_id += f'_{term}_{val}'
            else:
                val = ''
                context_id += f'_{id}'
            d = {'id': id, 'term': term, 'val': val}
            dimensions.append(d)
            if re.match('.*G25_[^_]*$', context_id):
                context_id = re.sub(r'(.*)G25_(.*)',r'\1G25_'+line_id, context_id)

    for i in range(start, len(header)):
        id = header[i]
        data = record[i]
        if data and id in taxCategoryCode:
            taxCategory = data
            if 'ibt-151' == id:
                invoicedItemTaxCategoryCode = taxCategory
                break
    if invoicedItemTaxCategoryCode:
        taxCategory = invoicedItemTaxCategoryCode
    # i = 3*boughLvl
    for i in range(start, len(header)):
        id = header[i]
        data = record[i]
        if data and id in taxRates:
            taxRate = data
            if 'ibt-152' == id:
                invoicedItemTaxRate = taxRate
                break
    if invoicedItemTaxRate:
        taxRate = invoicedItemTaxRate
    taxCategoryEffective = False
    if taxCategory:
        if not 'G25' in context_id or not 'G32' in context_id:
            context_id += f'_G23_{taxCategory}{taxRate}'
            taxCategoryEffective = True

    set_context_entity_date()

    lines.append(f'    <xbrli:scenario>\n')
    lines.append(
        f'      <xbrldi:typedMember dimension="pint:_380"><pint:_v>{invoice_number}</pint:_v></xbrldi:typedMember>\n')
    if len(dimensions) > 0:
        for data in dimensions:
            term = data['term']
            term = f'{term[0].upper()}{term[1:]}'
            val = data['val']
            if 'PaymentInstruction' == term:
                html = f'      <xbrldi:typedMember dimension="pint:G16"><pint:_uncl4461>{val}</pint:_uncl4461></xbrldi:typedMember>\n'
            else:
                html = f'      <xbrldi:typedMember dimension="pint:{term}"><pint:_v>{val}</pint:_v></xbrldi:typedMember>\n'
            lines.append(html)
    if taxCategoryEffective:
        html = f'      <xbrldi:explicitMember dimension="pint:G234">pint:G23_{taxCategory}{taxRate}</xbrldi:explicitMember>\n'
        lines.append(html)

    lines.append(f'    </xbrli:scenario>\n')

    lines.append(f'  </xbrli:context>\n')

def set_record(record):
    global invoice_number
    global issue_date
    global invoice_currency
    global tax_currency
    global seller_id
    global lines
    global context_id
    head = record[:3*boughLvl]
    tail = record[3*boughLvl:]

    for i in range(len(record)):
        data = record[i]
        if not data:
            continue
        id = header[i].lower()
        if not id:
            continue
        dict = pintDict[id]
        datatype = dict['datatype']
        type = ''
        if datatype:
            type = datatypeMap[datatype]
        data = record[i]
        if data:
            if 'amount' == type:
                lines.append(
                    f'  <pint:{id} contextRef="{context_id}" decimals="0" unitRef="{invoice_currency}">{data}</pint:{id}>\n')
            elif 'numeric' == type:
                lines.append(
                    f'  <pint:{id} contextRef="{context_id}" decimals="0" unitRef="pure">{data}</pint:{id}>\n')
            else:
                lines.append(
                    f'  <pint:{id} contextRef="{context_id}">{data}</pint:{id}>\n')

if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser(prog='csv2xbrl',
                                     usage='%(prog)s infile -s sourcefile -o outfile [options] ',
                                     description='CSVファイルから電子インボイスxBRLを作成')
    # Add the arguments
    parser.add_argument('inFile', metavar='infile', type=str, help='入力ファイル')
    parser.add_argument('-s', '--source')
    parser.add_argument('-o', '--out')
    parser.add_argument('-e', '--encoding')  # 'Shift_JIS' 'cp932'
    parser.add_argument('-t', '--transpose', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()
    in_file = args.inFile.strip()
    in_file = in_file.replace('/',SEP)
    in_file = file_path(in_file)
    # Check if infile exists
    if not os.path.isfile(in_file):
        print('入力ファイルがありません')
        sys.exit()
    pre, ext = os.path.splitext(in_file)
    if args.source:
        pint_file = args.source.lstrip()
        pint_file = pint_file.replace('/',SEP)
        pint_file = file_path(pint_file)
    if args.out:
        out_file = args.out.lstrip()
        out_file = out_file.replace('/',SEP)
        out_file = file_path(out_file)
    else:
        out_file = pre+'.xbrl'
    ncdng = args.encoding.lstrip()
    if not ncdng:
        ncdng = 'UTF-8'
    TRANSPOSE = args.verbose
    VERBOSE = args.verbose
    DEBUG = args.debug

    if VERBOSE:
        print('** START ** ', __file__)

    # # initialize globals
    pintDict = {}
    semDict = {}
    header_id = None
    header_count = 0
    DocumentCurrencyCode = None
    TaxCurrencyCode = None
    CurrencyCode = None
    Dic = defaultdict(type(''))
    Dic['Invoice'] = {}
    sortedDic = defaultdict(type(''))
    sortedDic['Invoice'] = {}
    pintDict = defaultdict(type(''))
    pintL1 = []
    multipleBG = []

    pint_file = pint_file.replace('/', SEP)
    pint_file = file_path(pint_file)
    # SemSort,ID,Section,PINTCard,Aligned,AlignedCard,Level,BT,BT_ja,DT,Desc,Desc_ja,Expl,Expl2,Example,SyntSort,element,UBLdatatype,XPath,selectors,Codelist,SyntaxCard,UBLOccurrence,CAR,AlignedRule,SharedRule,CodelistRule,PooledRule
    # 0       1  2       3        4       5           6     7  8     9  10   11      12   13    14      15       16      17          18    19        20       21         22            23  24          25         26           27
    COL_SemanticSort = 0
    COL_ID = 1
    COL_level = 6
    COL_BT = 7
    COL_card = 5
    COL_datatype = 9
    COL_SyntaxSort = 15
    COL_xpath = 18
    if VERBOSE:
        print(f'-- PINT file {pint_file}')
    with open(pint_file, encoding='utf-8', newline='') as f0:
        reader = csv.reader(f0) #, delimiter='\t')
        header = next(reader)
        for v in reader:
            id = v[COL_ID].strip()
            if id:
                semSort = v[COL_SemanticSort]
                xpath = v[COL_xpath]
                syntaxSort = v[COL_SyntaxSort]
                if not syntaxSort:
                    syntaxSort = '9999'
                if not xpath:
                    xpath = '/'+id
                if len(v) > COL_xpath and '/' in xpath:
                    if v[COL_BT]:
                        BT = v[COL_BT]
                    else:
                        BT = None
                    level = v[COL_level]
                    card = ''+v[COL_card].strip()
                    datatype = ''+v[COL_datatype].strip()
                    data = {'syntaxSort': syntaxSort, 'id': id, 'level': level,
                            'BT': BT, 'card': card, 'datatype': datatype, 'xpath': xpath}
                    pintDict[id] = data
                    semDict[semSort] = {'id': id, 'level': int(level)}

    sorted_semDict = sorted(semDict.items(), key=lambda x: x[0])

    level = 0
    parent = ['ibg-00']
    for k, v in dict(sorted_semDict).items():
        if v['level'] == level:
            semDict[k]['parent'] = parent[level-1]
            parent[level] = v['id']
        elif v['level'] == level+1:
            semDict[k]['parent'] = parent[level]
            level = v['level']
            if level == len(parent):
                parent.append(None)
            parent[level] = v['id']
        else:
            level = v['level']
            semDict[k]['parent'] = parent[level-1]
            parent[level] = v['id']
            for i in range(len(parent)):
                if i > level:
                    parent[i] = None

    in_file = in_file.replace('/', SEP)
    if VERBOSE:
        print(f'-- Input file {in_file}')
    with open(in_file, encoding='utf-16', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = []
        for record in reader:
            id = record[0]
            if id and id in pintDict:  # \ufeff
                data = pintDict[id]
                syntaxSort = data['syntaxSort']
            else:
                syntaxSort = '000'+str(i)
                if '\ufeff' == id:
                    id = ''
                i += 1
            if data:
                row = [syntaxSort, id]+record[4:]
                rows.append(row)

    # https://www.geeksforgeeks.org/ways-sort-list-dictionaries-values-python-using-itemgetter/
    # https://www.delftstack.com/ja/howto/python/sort-list-of-lists-in-python/
    sorted_rows = sorted(rows, key=lambda x: x[0])
    sorted_rows = [d[1:] for d in sorted_rows]

    row_count = len(sorted_rows)
    col_count = len(sorted_rows[0])
    transposed_rows = []
    while len(transposed_rows) < col_count:
        transposed_rows.append([])
        while len(transposed_rows[-1]) < row_count:
            transposed_rows[-1].append(0)
    for i in range(row_count):
        for j in range(col_count):
            transposed_rows[j][i] = sorted_rows[i][j]

    header = transposed_rows[0]
    for i in range(len(header)):
        if len(header[i]) > 0:
            break
    boughLvl = math.ceil(i/3)
    transposed_rows = transposed_rows[1:]

    for record in transposed_rows:
        setup_record(record)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<!-- Generated by csv2xbrl provided by Nobuyuki SAMBUICHI -->\n'
        '<xbrli:xbrl xmlns:pint="http://www.xbrl.jp/eipa/peppol/0.9"\n',
        '  xmlns:link="http://www.xbrl.org/2003/linkbase"\n',
        '  xmlns:iso4217="http://www.xbrl.org/2003/iso4217"\n',
        '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n',
        '  xmlns:xbrli="http://www.xbrl.org/2003/instance"\n',
        '  xmlns:xbrldi="http://xbrl.org/2006/xbrldi"\n',
        '  xmlns:xlink="http://www.w3.org/1999/xlink">\n',
        '  <link:schemaRef xlink:type="simple" xlink:href="core.xsd"/>\n',
        '  <!--  <link:schemaRef xlink:type="simple" xlink:href="https://www.wuwei.space/xbrl/e-invoice/peppol-xbrl/eipa/peppol/0.9/core.xsd"/> -->\n',
        '  <xbrli:unit id="pure">\n',
        '    <xbrli:measure>xbrli:pure</xbrli:measure>\n',
        '  </xbrli:unit>\n',
        f'  <xbrli:unit id="{invoice_currency}">\n',
        f'    <xbrli:measure>iso4217:{invoice_currency}</xbrli:measure>\n',
        '  </xbrli:unit>\n'
    ]
    if tax_currency:
        lines.append(f'  <xbrli:unit id="{tax_currency}">\n')
        lines.append(
            f'    <xbrli:measure>iso4217:{tax_currency}</xbrli:measure>\n')
        lines.append(f'  </xbrli:unit>\n')

    i = 0
    for record in transposed_rows:
        set_context(record)
        set_record(record)

    lines.append('</xbrli:xbrl>')

    with open(f'{out_file}', 'w', encoding='utf_8', newline='') as f:
        f.writelines(lines)

    if VERBOSE:
        print(f'-- Output file {out_file}')
        print(f'** END **')
