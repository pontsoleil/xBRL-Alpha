# CSV2INVOICE概要 Arelle OIM-CSV
Windows 10にArelleをGitHubからCloneして、そのディレクトリで次のコマンドを実行するとOIM-CSV1を読み込み、xBRLインスタンス(XML)を出力する。  
タクソノミも同一ディレクトリに配置している。  
`python arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f 「メタデータJSONファイル」 --saveOIMinstance 「出力XMLインスタンス文書」`  
実行例  
```
ドキュメント\GitHub\Arelle> python arelleCmdLine.py --plugins 'loadFromOIM|saveLoadableOIM' -f ../e-invoice/xBRL/CSV2INVOICE/data/example_1-metadata.json --saveOIMinstance ../e-invoice/xBRL/CSV2INVOICE/data/example_1.xml
>>
[info] Activation of plug-in Load From OIM successful, version 1.2. - loadFromOIM
[info] Activation of plug-in Save Loadable OIM successful, version 1.2. - saveLoadableOIM
[info] loaded in 0.72 secs at 2022-07-11T13:38:39 - C:\Users\nobuy\OneDrive\ドキュメント\GitHub\e-invoice\xBRL\CSV2INVOICE\data\example_1-metadata.json
```

## タクソノミをJP PINT定義ファイル(CSV)から生成 (前提作業１)
xBRL/pint2xBRL-taxonomy.pyを実行  
JP PINT定義ファイル(CSV)は、xBRL/CSV2INVOICEdata/common/jp_pint.csv  
core.xsdファイルの先頭部分は、xBRL/source/head/core-head.txtを転記している。  
`"args": ["CSV2INVOICE/data/common/jp_pint.csv","-o taxonomy/pint/cor.xsd","-e utf-8", "-v", "-d"] // pint2xBRL-taxonomy.py`
taxonomy/pint/cor.xsdと同じディレクトリに cor-pre.xml cor-def.xml cor-lbl-en.xml cor-lbl-ja.xml1を作成する。


## OIM-CSVをデジタルインボイスから変換 (前提作業２)
xBRL/CSV2INVOICEディレクトリで実行  
JP PINT定義ファイル(CSV)はxBRL/CSV2INVOICEdata/common/jp_pint.csv  
xBRL/CSV2INVOICE/invoice2oim.pyを実行  
`"args": ["examples/example_1.xml","-s data/common/jp_pint.csv","-o data/example_1.csv","-e utf-8","-d","-v"] // invoice2oim`

## 注
従来は、0..nでOccurrence定義されたComplexTypeの要素は、繰り返し回数が１回でもOIM-CSVでは別の行に定義していた。  
定義リンクのディメンション定義で@targetRoleを指定することで繰り返し回数が１回のときにはOIM-CSVで別の行に定義しなくてもよくした。  

更新 2022-07-11
