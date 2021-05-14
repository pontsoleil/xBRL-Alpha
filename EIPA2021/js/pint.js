/**
 * pint.js
 *
 * This is a free to use open source software and licensed under the MIT License
 * CC-SA-BY Copyright (c) 2020 - 2021, Sambuichi Professional Engineers Office
 **/
var pint2ubl_columns, pint2ubl_columnDefs,
    pint2ubl_table, ubl2pint_table,
    pint2ublMap, ubl2pintcMap, IvcNums,
    expandedRows, collapsedRows,
    PINT_UBL, UBL_CBC, UBL_CAC,
    ajaxUbl2pint,
    required_rules_columns, required_rules_columnDefs, required_rulesMap,
    suggested_rules_table, suggested_rules_table, suggested_rulesMap;
// ---
function setFrame(table_id) {
  var top_container, table_frame, child, id, match, base, table;
  // save current content to backup.
  // top
  top_container = $('#root-container');
  if ('reset' === table_id) {
    table_id = $('#tab-1 p.active')[0].classList.value.replace('tablinks','').replace('active','').trim();
  }
  else {  // backup
    if (top_container.children().length > 0) {
      child = top_container.children();
      if (child) {
        id = child.attr('id');
        match = id.match(/^(.*)-frame$/);
        id = match[1];
        base = $('#'+id+'-container');
        table_frame = $('#'+id+'-frame');
        base.append(table_frame);
      }
    }
    table_frame = $('#'+table_id+'-frame');
    top_container.append(table_frame);
    $('.tablinks').removeClass('active');
    $('.tablinks.'+table_id).addClass('active');
  }
  if ('pint2ubl' === table_id) {
    filterRoot(table_id);
    checkDetails(table_id);
    table = pint2ubl_table;
  }
  else if ('ubl2pint' === table_id) {
    ajaxUbl2pint();
    table = ubl2pint_table;
  }
  else if ('required_rules' === table_id) {
    table = required_rules_table;
  }
  else if ('suggested_rules' === table_id) {
    table = suggested_rules_table;
  }
  if (table) {
    var trs = $('#root table tr.shown'), table;
    for (var tr of trs) {
      table.row(tr).child.hide();
      $(tr).removeClass('shown');
    }
  }
}
// -----------------------------------------------------------------
// Formatting function for row details
//
function modifyTranslation(text) {
  var index, keys;
  keys = Object.keys(modify_translate);
  for (var key of keys) {
    text = text.replaceAll(key, modify_translate[key]);
  }
  text = text.trim();
  index = text.lastIndexOf('&quot;');
  if (index > 0) { text = text.substr(0, index); }
  index = text.lastIndexOf('」');
  if (index > 0) { text = text.substr(0, index); }
  index = text.lastIndexOf('"、');
  if (index > 0) { text = text.substr(0, index); }
  if ('&quot;]' === text) { text = ''; }
  if (']' === text) { text = ''; }
  return text
}
function pint2ubl_format(d) { // d is the original data object for the row
  if (!d) { return null; }
  var H1 = 30, H2 = 35, H3 = 35,
      id = d.PINT_ID,
      desc = d.PINT_Desc,
      path = d.Path,
      BIS_diff = d.BIS_diff,
      attrib = d.Attrib,
      rules = d.Rules,
      rulesArray, suggestedArray,
      pathArray,
      padding = '',
      html = '',
      wk_path = '',
      wk_desc;
  if (!rules) {
    rules = '';
    rulesArray = required_rulesMap.get(id);
    if (rulesArray && rulesArray.length > 0) {
      rules = '== Rules ==<br>';
      for (var rule of rulesArray) {
        rules += '*'+rule.Rule_ID+'* ['+rule.Severity+'] '+rule.Rule+'<br>';
      }
    }
    suggestedArray = suggested_rulesMap.get(id);
    if (suggestedArray && suggestedArray.length > 0) {
      rules = '== Suggested ==<br>';
      for (var rule of suggestedArray) {
        rules += '*'+rule.Rule_ID+'* ['+rule.Category+'] '+rule.CommonRules+'<br>';
      }
      rules = rules.substr(0, rules.length-4); // remove last <br>
    }
  }
  BIS_diff = BIS_diff.replace(/[Cc]rd/,'Cardinality');
  wk_desc = (BIS_diff? 'BIS拡張：'+BIS_diff+'<br>' : '')+(attrib ? attrib+'<br>' : '');
  if (path) {
    pathArray = path.split('/');
    wk_path = '/' + pathArray[1]+'/&nbsp;';
    if (pathArray.length > 1) {
      for (var i = 2; i < pathArray.length; i++) {
        if (i < pathArray.length -1){
          wk_path += padding + pathArray[i]+'/ <br>';
          padding += '&nbsp;&nbsp;';
        }
        else {
          wk_path += padding + pathArray[i];
        }
      }
    }
  }
  if (!desc && !rules) {
    return Promise.resolve()
    .then(function() {
      html = '<table cellpadding="4" cellspacing="0" border="0" style="width:100%;">'+
        '<colgroup>'+
          '<col style="width:'+H1+'%;">'+'<col style="width:'+H2+'%;">'+'<col style="width:'+H3+'%;">'+
        '</colgroup>'+
        '<tr>'+
          '<td valign="top">'+desc+'</td>'+
          '<td valign="top">'+wk_desc+'</td>'+
          '<td valign="top">'+wk_path+'</td>'+
        '</tr>'+
        '</table>';
      return html;
    })
    .catch(function(err) { console.log(err); });
  }
  else {
    return googleTranslate([desc, rules])
    .then(function(translations) {
      var translatedText, match, j_desc, j_rules;
      translatedText = translations[0].translatedText;

      match = translatedText.match(/.(\&quot;)(.*)(\&quot;)[^&quot;]*(\&quot;)(.*)$/);
      if (match) {
        j_desc = match[2];
        j_rules = match[5];
        j_desc = modifyTranslation(j_desc);
        j_rules = modifyTranslation(j_rules);
      }
      else {
        j_desc = translatedText;
      }
      j_desc = modifyTranslation(j_desc);
      html = '<table cellpadding="4" cellspacing="0" border="0" style="width:100%;">'+
        '<colgroup>'+
          '<col style="width:'+H1+'%;">'+
          '<col style="width:'+H2+'%;">'+
          '<col style="width:'+H3+'%;">'+
        '</colgroup>';
      html += '<tr>'+'<td valign="top">'+desc+'</td>';
      if (!rules) {
        html += '<td valign="top" rowspan="2">'+wk_desc+'</td>';
      }
      else {
        html += '<td valign="top">'+wk_desc+'</td>';
      }
      if (!j_rules) {
        html += '<td valign="top" rowspan="2">'+wk_path+'</td>';
      }
      else {
        html += '<td valign="top">'+wk_path+'</td>';
      }
      html += '</tr>';
      html += '<tr><td valign="top">'+j_desc+'</td>';
      if (rules) {
        rules = rules.replaceAll('*ibr', '<hr>*ibr');
        html += '<td valign="top">'+rules+'</td>';
      }
      if (j_rules) {
        j_rules = j_rules.replaceAll('* ibr', '<hr>* ibr');
        html += '<td valign="top">'+j_rules+'</td>';
      }
      html += '</tr></table>';
      return html;
    })
    .catch(function(err) { console.log(err); });
  }
}
// ---
function ubl2pint_format(d) { // d is the original data object for the row
  if (!d) { return null; }
  var H1 = 30, H2 = 35, H3 = 35,
      id = d.PINT_ID,
      paths = d.Paths,
      BIS_diff = d.BIS_diff,
      attrib = d.Attrib || '',
      rules = d.Rules || '',
      pint_desc = d.PINT_Desc || ' ',
      wk_desc,
      _paths, parent, child, _child,
      match, abie, bbie, base,
      parent_type, den, cardinality, definition,
      html = '';
  if (!rules) {
    rules = '';
    if (id) {
      rulesArray = required_rulesMap.get(id);
    }
    if (rulesArray && rulesArray.length > 0) {
      for (var rule of rulesArray) {
        rules += '<br>*'+rule.Rule_ID+'* ['+rule.Severity+'] '+rule.Rule;
      }
      // rules = rules.substr(0, rules.length-4); // remove last <br>
    }
    if (id) {
      suggestedArray = suggested_rulesMap.get(id);
    }
    if (suggestedArray && suggestedArray.length > 0) {
      rules = '== Suggested ==<br>';
      for (var rule of suggestedArray) {
        rules += '*'+rule.Rule_ID+'* ['+rule.Category+'] '+rule.CommonRules+'<br>';
      }
      rules = rules.substr(0, rules.length-4); // remove last <br>
    }
  }
  _paths = paths.replaceAll('&nbsp;','').split('<br>');
  parent = _paths[_paths.length - 3];
  child = _paths[_paths.length - 2];
  match = parent.match(/^cac:(.*)$/);
  if (match) {
    abie = match[1];
    parent_type = UBL_CAC.type[UBL_CAC.element[abie]['@type']];
    _child = parent_type.element.filter(function(el) {
      return child === el['@ref'];
    });
    if (_child.length > 0) {
      _child = _child[0];
    }
  }
  else if ('Invoice' === parent) {
    _child = PINT_UBL.element.filter(function(el) {
      return child === el['@ref'];
    });
    if (_child.length > 0) {
      _child = _child[0];
    }
  }
  match = child.match(/^cbc:(.*)$/);
  if (match) {
    bbie = match[1];
    base =UBL_CBC.type[UBL_CBC.element[bbie]['@type']]['@base'];
  }
  _child = _child ? _child : {};
  den = _child['DictionaryEntryName'] || '';
  den = den ? 'DEN: '+den : '';
  datatype = _child['DataType'] || '';
  base = base ? ' ( '+base+' )' : '';
  cardinality = _child['Cardinality'] || '';
  if ('1' == cardinality) { cardinality = '1..1'; }
  cardinality = cardinality ? ' [ '+cardinality+' ]' : '';
  definition =  _child['Definition'] || '';

  return googleTranslate([pint_desc, definition, rules])
  .then(function(translations) {
    var translatedText = translations[0].translatedText,
        match, j_desc, j_definition, j_rules;
    match = translatedText.match(/.(\&quot;)(.*)(\&quot;)、[^&quot;]*(\&quot;)(.*)(\&quot;)、[^&quot;]*(\&quot;)(.*)$/);
    if (match) {
      j_desc = match[2];
      j_definition = match[5];
      j_rules = match[8];
      j_desc = modifyTranslation(j_desc);
      j_definition = modifyTranslation(j_definition);
      j_rules = modifyTranslation(j_rules);
    }
    html = '<table cellpadding="4" cellspacing="0" border="0" style="width:100%;">'+
      '<colgroup>'+
        '<col style="width:'+H1+'%;">'+
        '<col style="width:'+H2+'%;">'+
        '<col style="width:'+H3+'%;">'+
      '</colgroup>' +
      '<tr>';
    paths = '/'+paths
            .replace(/(.*)<br>$/,function(match,p1,offset, string) { return p1; })
            .replaceAll('<br>','/<br>')+'<br>';
    paths += (BIS_diff ? 'BIS拡張: '+BIS_diff.replace(/[Cc]rd/,'Cardinality') : '');
    if (!j_desc && !j_definition) {
      html += '<td valign="top">'+paths+'</td>';
    }
    else {
      html += '<td valign="top" rowspan="3">'+paths+'</td>';
    }
    BIS_diff = BIS_diff.replace(/[Cc]rd/,'Cardinality');
    wk_desc = (BIS_diff? 'BIS拡張：'+BIS_diff+'<br>' : '')+
              (attrib ? 'Attributes - adjustments: '+attrib+'<br>' : '');
    html += '<td valign="top">'+'- UBL2.1定義 -<br>'+
              den+cardinality+base+'<br>'+
              definition+'</td>'+
            '<td valign="top">- PINT定義 -<br>'+
              (wk_desc ? wk_desc : '' )+
              (pint_desc ? pint_desc : '' )+
            '</td></tr>';
    // tranlation
    html += '<tr>'+
      '<td valign="top">'+j_definition+'</td>'+
      '<td valign="top">'+j_desc+'</td>'+
    '</tr>';
    rules = rules.replaceAll('*ibr', '<hr>*ibr');
    j_rules = j_rules.replaceAll('* ibr', '<hr>* ibr');
    html += '<tr>'+
      '<td valign="top">'+(rules ? '== Rules =='+rules : '')+'</td>'+
      '<td valign="top">'+(j_rules ? '== ルール =='+j_rules : '')+'</td>'+
    '</tr>';
    html += '</table>';
    return html;
  })
  .catch(function(err) { console.log(err); });
}
// ---
function required_rules_format(d) { // d is the original data object for the row
  if (!d) { return null; }
  var id = d.Rule_ID,
      severity = d.Severity,
      rule = d.Rule,
      html = '';
  if (!rule) {
    return Promise.resolve()
    .then(function() {
      html = '<table cellpadding="4" cellspacing="0" border="0" style="width:100%;">'+
        '<tr>'+
          '<td valign="top"> </td>'+
        '</tr></table>';
      return html;
    })
    .catch(function(err) { console.log(err); });
  }
  else {
    return googleTranslate(rule)
    .then(function(translations) {
      var translatedText, j_rule;
      translatedText = translations[0].translatedText;
      j_rule = translatedText;
      j_rule = modifyTranslation(j_rule);
      html = '<table cellpadding="4" cellspacing="0" border="0" style="width:100%;">'+
        '<tr>'+
          '<td valign="top">'+j_rule+'</td>'+
        '</tr></table>';
      return html;
    })
    .catch(function(err) { console.log(err); });
  }
}
// ---
function suggested_rules_format(d) { // d is the original data object for the row
  if (!d) { return null; }
  var id = d.Rule_ID,
      rule = d.CommonRules,
      html = '';
  if (!rule) {
    return Promise.resolve()
    .then(function() {
      html = '<table cellpadding="4" cellspacing="0" border="0" style="width:100%;">'+
        '<tr>'+
          '<td valign="top"> </td>'+
        '</tr></table>';
      return html;
    })
    .catch(function(err) { console.log(err); });
  }
  else {
    return googleTranslate(rule)
    .then(function(translations) {
      var translatedText, j_rule;
      translatedText = translations[0].translatedText;
      j_rule = translatedText;
      j_rule = modifyTranslation(j_rule);
      html = '<table cellpadding="4" cellspacing="0" border="0" style="width:100%;">'+
        '<tr>'+
          '<td valign="top">'+j_rule+'</td>'+
        '</tr></table>';
      return html;
    })
    .catch(function(err) { console.log(err); });
  }
}
// -----------------------------------------------------------------
function renderBT(row) {
  var term = row.PINT_BT,
      card = row.PINT_Card,
      level = row.PINT_Level,
      res = '';
  for (var i = 1; i < level; i++) {
    res += '+';
  }
  if (level > 1) {
    res += ' ';
  }
  if (card.match(/^1/)) {
    term = '<b>'+term+'</b>';
  }
  res = res += term;
  return res;
}
// ---
function renderPath(row) {
  var path, match, parent, element, res = '';
  path = row.Path;
  match = path.match(/([^\/]*)\/([^\/]*)$/);
  if (! match) {
    return path;
  }
  if (match[1]) {
    parent = match[1];
    if ('Invoice' === parent) {
      parent = '/Invoice';
    }
    else {
      parent = '... ' + parent;
    }
    res = parent+'/ ';
  }
  if (match[2]) {
    element = match[2];
    res += element;
  }
  return res;
}
// ---
function renderPath2(row) {
  var path, name = '';
  path = row.Path.split('/');
  if (path.length > 1) {
    path.shift();
    level = path.length - 1;
    for (i = 0; i < level; i++) { name += '+'; }
    if (level > 0) { name += ' '; }
    name += path[level];
  }
  return name;
}
// ---
pint2ubl_columns = [
  { 'width': '2%',
    'className': 'details-control',
    'orderable': false,
    'data': null,
    'defaultContent': '' }, // 0
  { 'width': '6%',
    'data': 'PINT_ID' }, // 1 
  { 'width': '39%',
    'data': 'PINT_BT',
    'render': function(data, type, row) {
      var term = renderBT(row);
      return term; } }, // 2
  { 'width': '7%',
    'data': 'PINT_DT'}, // 3
  { 'width': '6%',
    'data': 'PINT_Card'}, // 4
  { 'width': '7%',
    'data': 'Section' }, // 5
  { 'width': '30%',
    'data': 'Path',
    'render': function(data, type, row) {
      var path = renderPath(row);
      return path; }}, // 6
  { 'width': '3%',
    'className': 'info-control',
    'orderable': false,
    'data': null,
    'defaultContent': '' } // 7
];
// ---
pint2ubl_columnDefs = [
  { 'searchable': false, 'targets': [0, 7] }
];
// -------------------------------------------------------------------
ubl2pint_columns = [
  { 'width': '2%',
    'className': 'details-control',
    'orderable': false,
    'data': null,
    'defaultContent': '' }, // 0
  { 'data': 'num' }, // 1
  { 'width': '40%',
    'data': 'Path',
    'render': function(data, type, row) {
      var path = row.Path || '';
      if (0 === row.seq) { path = '<b>'+path+'</b>'; }
      else if (row.Card && row.Card.match(/^1/)) {
        path = path.replace(/^([\+]* )(.*)?/, "$1<b>$2</b>")
      }
    return path; }}, // 2
  { 'width': '6%',
    'data': 'PINT_ID' }, // 3
  { 'width': '4%',
    'data': 'PINT_Level' }, // 4
  { 'width': '26%',
    'data': 'PINT_BT' }, // 5
  { 'width': '10%',
    'data': 'PINT_DT'}, // 6
  { 'width': '7%',
    'data': 'PINT_Card' }, // 7
  { 'width': '7%',
    'data': 'Section' }, // 8
  { 'width': '2%',
    'className': 'info-control',
    'orderable': false,
    'data': null,
    'defaultContent': '' } // 8
];
// ---
ubl2pint_columnDefs = [
  { 'searchable': false, 'targets': [0, 8] },
  { 'visible': false, 'targets': 1 }
];
// -------------------------------------------------------------------
required_rules_columns = [
  { 'width': '20%',
    'data': 'Rule_ID' }, // 0
  { 'width': '10%',
    'data': 'Severity'}, // 1
  { 'width': '70%',
    'data': 'Rule' } // 2
];
// ---
required_rules_columnDefs = [
  { 'searchable': false, 'targets': [0, 2] }
];
// -------------------------------------------------------------------
//ID	Category	CommonRules	JapanImplementation
suggested_rules_columns = [
  { 'width': '20%',
    'data': 'Rule_ID' }, // 0
  { 'width': '16%',
    'data': 'Category'}, // 1
  { 'width': '32%',
    'data': 'CommonRules' }, // 2
  { 'width': '32%',
    'data': 'JapanImplementation' } // 3
];
// ---
suggested_rules_columnDefs = [
  { 'searchable': false, 'targets': [0, 3] }
];
// -------------------------------------------------------------------
// Utility
//
function appendByNum(items, item) {
  if (!item.num) {
    return null;
  }
  if (items instanceof Array && item) {
    for (var i = 0; i < items.length; i++) {
      if (items[i].num && item.num === items[i].num) {
        items.splice(i, 1);
        items.push(item);
        return items;
      }
    }
    items.push(item);
    return items;
  }
  return null;
}
// -------------------------------------------------------------------
function removeByNum(items, item) {
  if (!item.num) {
    return null;
  }
  if (items instanceof Array && item) {
    for (var i = 0; i < items.length; i++) {
      if (items[i].num && item.num === items[i].num) {
        items.splice(i, 1);
        return items;
      }
    }
    return items;
  }
  return null;
}
// -------------------------------------------------------------------
var compareNum = function(a, b) {
  var a_arr = a.num.split('_').map(function(v){ return +v; }),
      b_arr = b.num.split('_').map(function(v){ return +v; });
  while (a_arr.length > 0 && b_arr.length > 0) {
    var a_num = a_arr.shift(),
        b_num = b_arr.shift();
    if (a_num < b_num) { return -1; }
    if (b_num < a_num) { return  1; }
  }
  if (b_arr.length > 0) { return -1; }
  if (a_arr.length > 0) { return  1; }
  return 0;
}
// -------------------------------------------------------------------
function filterRoot(table_id) {
  var table, records, rows;
  table = $(table_id).DataTable();
  records = [];
  rows = [];
  records = table.data().toArray();
  for (var v of records) {
    if ('#ubl2pint' === table_id) {
      if (v.num.split('_').length < 3) {
        rows.push(v);
      }
    }
    else {
      if ('root' === v.PINT_Parent) {
        rows.push(v);
      }
    }
  }
  table.clear();
  table.rows
  .add(rows)
  .draw();
  if ('#ubl2pint' === table_id) {
    $(table_id +' tbody tr')[0].classList.add('expanded');
  }
}
// -------------------------------------------------------------------
function checkDetails(table_id) {
  var table = $(table_id).DataTable(),
      data = table.data(),
      tr_s, tr, // nextSibling,
      row, row_data, num, i,// nums, nextrow, nextrow_data,
      rgx;
  tr_s = $(table_id+' tbody tr');
  if (data.length > 0) {
    for (var tr of tr_s) {
      row = table.row(tr);
      row_data = row.data();
      if (row_data.PINT_ID.match(/^ibt/)) {
        tr.childNodes[0].classList = '';
      }
    }
  }
}
// -------------------------------------------------------------------
function expandCollapse(table_id, map, tr) {
  var table,
      row, row_data, rows, rows_, id, i, 
      res,
      collapse = null,
      expand = null,
      v, rgx;
  // --
  function isExpanded(rows, num) {
    var expanded = false,
        i, rgx;
    rgx = RegExp('^'+num+'_[^_]+$')
    for (i = 0; i < rows.length; i++) {
      num = rows[i].num;
      if (num.match(rgx)) {
        expanded = num;
        break;
      }
    }
    return expanded;
  }
  // --
  table = $(table_id).DataTable();
  row = table.row(tr);
  row_data = row.data();
  if (!row_data) { return; }
  rows = [];
  rows_ = table.data();
  for (i = 0; i < rows_.length; i++) {
    row = rows_[i];
    rows.push(row);
  }
  res = isExpanded(rows_, row_data.num);
  if (res) {
    collapse = row_data.num;
  }
  else {
    expand = row_data.num;
  }
  if (collapse) { // collapse
    tr.removeClass('expanded');
    removeByNum(expandedRows, row_data);
    collapsedRows = [row_data];
    rgx = RegExp('^'+collapse+'_');
    rows = rows.filter(function(row) {
      if (row.num.match(rgx)) {
        removeByNum(expandedRows, row);
        return false;
      }
      return true;
    });
  }
  else if (expand) { // expand
    tr.addClass('expanded');
    collapsedRows = [];
    expandedRows = [row_data];
    rgx = RegExp('^'+expand+'_[^_]+$');
    map.forEach(function(value, key) {
      if (value.num.match(rgx)) {
        v = JSON.parse(JSON.stringify(value));
        appendByNum(rows, v);
      }
    });
  }
  else {
    return;
  }
  rows.sort(compareNum);
  table.clear();
  table.rows
  .add(rows)
  .draw();
  var data = table.data(),
    tr_s, tr, nextSibling,
    row, row_data, nextrow, nextrow_data,
    rgx;
  if (data.length > 0) {
    var tr_s = $(table_id+' tbody tr');
    for (var tr of tr_s) {
      row = table.row(tr);
      row_data = row.data();
      nextSibling = tr.nextSibling;
      if (nextSibling) {
        nextrow = table.row(nextSibling);
        nextrow_data = nextrow.data();
        rgx = RegExp('^'+row_data.num+'_[^_]+$');
        if (nextrow_data.num.match(rgx)) {
          tr.classList.add('expanded');
        }
      }
    }
  }
}
// -------------------------------------------------------------------
// -------------------------------------------------------------------
var initModule = function () {
  // -----------------------------------------------------------------
  function tableInit(table_id, json) {
    var map,
        data, i, item, level, seq, num,
        idxLevel = [],
        numMap = new Map();
    data = json.data;
    for (i = 0; i < data.length; i++) {
      item = data[i];
      seq = item.num;
      level = item.PINT_Level - 1;
      num = ''+seq;
      if (level > 0) {
        num = (idxLevel[level - 1] || '0')+'_'+num;
      }
      while (idxLevel.length - 1 > level) {
        idxLevel.pop();
      }
      idxLevel[level] = num;
      numMap.set(seq, num);
    }
    map = new Map();
    for (i = 0; i < data.length; i++) {
      item = data[i];
      seq = item.num;
      item.seq = seq;
      num = numMap.get(seq);
      item.num = num;
      map.set(seq, item);
    }
    filterRoot(table_id);
    checkDetails(table_id);
    return map;
  }
  // ---
  function tableInit2(table_id, json) {
    var map, nums,
        data, item,
        seq, paths, padding = '', wk_path = '',
        level, num, name, term, i,
        rows = [],
        idxLevel = [];
    data = json.data;
    map = new Map();
    nums = [];
    for (i = 0; i < data.length; i++) {
      item = data[i];
      seq = i;
      item.seq = seq;
      item.PINT_Level = item.PINT_Level || '';
      item.PINT_Card = item.PINT_Card || '';
      item.PINT_DT = item.PINT_DT || '';
      item.PINT_Desc = item.PINT_Desc || '';
      num = ''+seq;
      paths = item.Path.split('/');
      if (paths.length > 1) {
        for (var i = 1; i < paths.length; i++) {
          wk_path += padding + paths[i]+'<br>';
          padding += '&nbsp;&nbsp;&nbsp;';
        }
        item.Paths = wk_path;
        padding = '';
        wk_path = '';
        paths.shift();
        level = paths.length - 1;
        name = '';
        for (i = 1; i < level; i++) { name += '+'; }
        // for (i = 0; i < level; i++) { name += '+'; }
        if (level > 0) { name += ' '; }
        term = paths[level];
        name += term;
        item.Path = name;
        if (level > 0) {
          num = (idxLevel[level - 1] || '0')+'_'+num;
        }
        while (idxLevel.length - 1 > level) {
          idxLevel.pop();
        }
        idxLevel[level] = num;
        nums.push(num);
        item.num = num;
        rows.push(item);
        map.set(seq, item);
      }
    }
    switch (table_id) {
      case '#ubl2pint':
        ubl2pintcMap = map;
        IvcNums = nums;
        break;
    }
    return rows;
  }
  // pint2ubl
  pint2ubl_table = $('#pint2ubl').DataTable({
    'ajax': 'data/pint2ubl.json',
    'columns': pint2ubl_columns,
    'columnDefs': pint2ubl_columnDefs,
    'paging': false,
    'autoWidth': false,
    'ordering': false,
    'select': true,
    'initComplete': function(settings, json) {
      pint2ublMap = tableInit('#pint2ubl', json);
    },
    'drawCallback': function(settings) {
      checkDetails('#pint2ubl');
    }  
  });
  // ubl2pint
  ajaxUbl2pint = function() {
    ajaxRequest('data/ubl2pint.json', null, 'GET', 1000)
    .then(function(res) {
      try {
        json = JSON.parse(res);
        return tableInit2('#ubl2pint', json);
      }
      catch(e) { console.log(e); }
    })
    .then(function(rows) {
      ubl2pint_table.clear();
      ubl2pint_table.rows
      .add(rows)
      .draw();
    })
    .then(function() {
      filterRoot('#ubl2pint');
    })
    .catch(function(err) { console.log(err); });
  }
  // --
  ubl2pint_table = $('#ubl2pint').DataTable({
    'columns': ubl2pint_columns,
    'columnDefs': ubl2pint_columnDefs,
    'paging': false,
    'autoWidth': false,
    'ordering': false,
    'select': true,
    'initComplete': function(settings, json) {
      ajaxUbl2pint();
    },
    'drawCallback': function(settings) {
      checkDetails('#ubl2pint');
    }  
  });
  // required_rules
  required_rules_table = $('#required_rules').DataTable({
    'ajax': 'data/required_rules.json',
    'columns': required_rules_columns,
    'columnDefs': required_rules_columnDefs,
    'paging': false,
    'autoWidth': false,
    'ordering': false,
    'select': true
  });
  // suggested_rules
  suggested_rules_table = $('#suggested_rules').DataTable({
    'ajax': 'data/suggested_rules.json',
    'columns': suggested_rules_columns,
    'columnDefs': suggested_rules_columnDefs,
    'paging': false,
    'autoWidth': false,
    'ordering': false,
    'select': true
  });
  // -----------------------------------------------------------------
  // Add event listener for opening and closing info .info-control
  // -----------------------------------------------------------------
  // pint2ubl
  $('#pint2ubl tbody').on('click', 'td:not(.details-control)', function(event) {
    event.stopPropagation();
    var tr = $(this).closest('tr'), row = pint2ubl_table.row(tr), data = row.data();
    if (row.child.isShown()) { // This row is already open - close it
      row.child.hide(); tr.removeClass('shown');
    }
    else { // Open this row
      pint2ubl_format(data)
      .then(function(html) {
        row.child(html).show(); tr.addClass('shown');
      })
      .catch(function(err) { console.log(err); });
    }
  });
  // ubl2pint
  $('#ubl2pint tbody').on('click', 'td:not(.details-control)', function(event) {
    event.stopPropagation();
    var tr = $(this).closest('tr'), row = ubl2pint_table.row(tr), data = row.data();
    if (row.child.isShown()) { // This row is already open - close it
      row.child.hide(); tr.removeClass('shown');
    }
    else { // Open this row
      ubl2pint_format(data)
      .then(function(html) {
        row.child(html).show(); tr.addClass('shown');
      })
      .catch(function(err) { console.log(err); });
    }
  });
  // required_rules
  $('#required_rules tbody').on('click', 'td', function (event) {
    event.stopPropagation();
    var tr = $(this).closest('tr'), row = required_rules_table.row(tr), data = row.data();
    if (row.child.isShown()) { // This row is already open - close it
      row.child.hide(); tr.removeClass('shown');
    }
    else { // Open this row
      required_rules_format(data)
      .then(function(html) {
        row.child(html).show(); tr.addClass('shown');
      })
      .catch(function(err) { console.log(err); });
    };      
  });
  // suggested_rules
  $('#suggested_rules tbody').on('click', 'td', function (event) {
    event.stopPropagation();
    var tr = $(this).closest('tr'), row = suggested_rules_table.row(tr), data = row.data();
    if (row.child.isShown()) { // This row is already open - close it
      row.child.hide(); tr.removeClass('shown');
    }
    else { // Open this row
      suggested_rules_format(data)
      .then(function(html) {
        row.child(html).show(); tr.addClass('shown');
      })
      .catch(function(err) { console.log(err); });
    }  
  });
  // -----------------------------------------------------------------
  // Add event listener for opening and closing detail records .details-control 
  // -----------------------------------------------------------------
  // pint2ubl
  $('#pint2ubl tbody').on('click', 'td.details-control', function (event) {
    event.stopPropagation();
    var tr = $(this).closest('tr'), row = pint2ubl_table.row(tr), data = row.data();
    if (!data) { return; }
    var id = data.PINT_ID;
    if (id.match(/^ibg/)) {
      expandCollapse('#pint2ubl', pint2ublMap, tr);      
    }
  });
  // ubl2pint
  $('#ubl2pint tbody').on('click', 'td.details-control', function (event) {
    event.stopPropagation();
    var tr = $(this).closest('tr'),
        row = ubl2pint_table.row(tr), data = row.data();
    if (!data) { return; }
    var num = data.num,
        rgx = RegExp('^'+num+'_[^_]+$'),
        i = 0;
    for (num of IvcNums) {
      if (num.match(rgx)) { i++; }
    }
    if (i > 0) {
      expandCollapse('#ubl2pint', ubl2pintcMap, tr);      
    }
  });
  // -----------------------------------------------------------------
  // Ajax 
  // -----------------------------------------------------------------
  // var ajaxCount = 0;
  // PINT_UBL 
  ajaxRequest('data/ubl2.1/ivc.json', null, 'GET', 1000)
  .then(function(res) {
    try {
      PINT_UBL = JSON.parse(res);
    }
    catch(e) { console.log(e); }
  })
  .catch(function(err) { console.log(err); });
  // UBL_CBC 
  ajaxRequest('data/ubl2.1/cbc.json', null, 'GET', 10000)
  .then(function(res) {
    try {
      var json = JSON.parse(res);
      UBL_CBC = {
        type: {},
        element: {}
      }
      json.complexType.forEach(function(v) {
        UBL_CBC.type[v['@name']] = v; 
      });
      json.element.forEach(function(v) {
        UBL_CBC.element[v['@name']] = v; 
      });
    }
    catch(e) { console.log(e); }
  })
  .catch(function(err) { console.log(err); });
  // UBL_CAC 
  ajaxRequest('data/ubl2.1/cac.json', null, 'GET', 10000)
  .then(function(res) {
    try {
      var json = JSON.parse(res);
      UBL_CAC = {
        type: {},
        element: {}
      }
      json.complexType.forEach(function(v) {
        UBL_CAC.type[v['@name']] = v; 
      });
      json.element.forEach(function(v) {
        UBL_CAC.element[v['@name']] = v; 
      });
    }
    catch(e) { console.log(e); }
  })
  .catch(function(err) { console.log(err); });
  // REQUIRED RULES
  ajaxRequest('data/required_rules.json', null, 'GET', 10000)
  .then(function(res) {
    try {
      var json = JSON.parse(res);
      required_rulesMap = new Map();
      json.data.forEach(function(v) {
        var ids = v.PINT_IDs.split(' '),
            rules;
        for (var id of ids) {
          rules = required_rulesMap.get(id);
          if (!rules) { rules = []; }
          rules.push(v);
          required_rulesMap.set(id, rules); 
        }
      });
    }
    catch(e) { console.log(e); }
  })
  .catch(function(err) { console.log(err); });
  // SUGGESTED RULES
  ajaxRequest('data/suggested_rules.json', null, 'GET', 10000)
  .then(function(res) {
    try {
      var json = JSON.parse(res);
      suggested_rulesMap = new Map();
      json.data.forEach(function(v) {
        var ids = v.PINT_IDs.split(' '),
            rules;
        for (var id of ids) {
          rules = suggested_rulesMap.get(id);
          if (!rules) { rules = []; }
          rules.push(v);
          suggested_rulesMap.set(id, rules); 
        }
      });
    }
    catch(e) { console.log(e); }
  })
  .catch(function(err) { console.log(err); });
  // setFrame('required_rules');
  setFrame('pint2ubl');
}
// pint.js