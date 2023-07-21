#! /bin/sh

RESOLVED="2-resolved_*"
COMPLEX="2-complex_*"
EXTERNAL="2-external_*"
UNRESOLVED="2-unresolved_*"

LIST="1-list_*"

cat ${RESOLVED} ${COMPLEX} ${EXTERNAL} ${UNRESOLVED} > v_RCEU_1.txt
cat v_RCEU_1.txt | awk -F " " '{ print $1}' > v_RCEU_2.txt
cat v_RCEU_2.txt | sort > v_RCEU_3.txt
# Remove lines beginning with '#'
cat v_RCEU_3.txt | sed -n '/^\#/!p' > v_RCEU_4.txt

cat ${LIST} > v_liste_1.txt
cat v_liste_1.txt | awk -F " " '{ print $1}' > v_liste_2.txt
cat v_liste_2.txt | sort > v_liste_3.txt
# Remove lines beginning with '#'
cat v_liste_3.txt | sed -n '/^\#/!p' > v_liste_4.txt

diff v_liste_4.txt v_RCEU_4.txt
