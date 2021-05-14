#!/bin/sh
# === Initialize shell environment ===================================
set -euvx
# -e  Exit immediately if a command exits with a non-zero status.
# -u  Treat unset variables as an error when substituting.
# -v  Print shell input lines as they are read.
# -x  Print commands and their arguments as they are executed.
export LC_ALL=C
type command >/dev/null 2>&1 && type getconf >/dev/null 2>&1 &&
export PATH=".:./bin:$(command -p getconf PATH)${PATH+:}${PATH-}"
export UNIX_STD=2003  # to make HP-UX conform to POSIX
# === temporary file prefix ==========================================
Tmp=/tmp/${0##*/}.$$
# === Log ============================================================
exec 2>log/${0##*/}.$$.log
# --------------------------------------------------------------------
# Sem_Sort PINT_Parent PINT_ID PINT_Level PINT_BT PINT_Desc PINT_Card PINT_DT Section BIS_diff Synt_Sort Path Attrib Rules
# 1        2           3       4          5       6         7         8       9       10       11        12   13     14 
cat pint2ubl.txt | awk -F'\t' 'BEGIN { n=0; }
{
  if (n>0 && $1!="" && $4!="") {
    print "$.data[" n "].num",n;
    print "$.data[" n "].Sem_Sort",$1;
    print "$.data[" n "].PINT_Parent",$2;
    print "$.data[" n "].PINT_ID",$3;
    print "$.data[" n "].PINT_Level",$4;
    print "$.data[" n "].PINT_BT",$5;
    print "$.data[" n "].PINT_Desc",$6;
    print "$.data[" n "].PINT_Card",$7;
    print "$.data[" n "].PINT_DT",$8;
    sub(/[\n\r]/,"",$9);
    print "$.data[" n "].Section",$9;
    print "$.data[" n "].BIS_diff",$10;
    print "$.data[" n "].Synt_Sort",$11;
    print "$.data[" n "].Path",$12;
    sub(/[\n\r]/,"",$13);
    print "$.data[" n "].Attrib",$13;
    sub(/[\n\r]/,"",$14);
    print "$.data[" n "].Rules",$14;
  }
  n=n+1;
}' > $Tmp-data
cat $Tmp-data | makrj.sh | sed "s/^\(\"[^\":,]*\":\),/\1null,/" > pint2ubl.json
# --------------------------------------------------------------------
rm $Tmp-*
rm log/${0##*/}.$$.*
exit 0
# pint2ubl.sh
