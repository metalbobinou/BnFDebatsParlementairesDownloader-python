#! /bin/sh

LIST="list_*"
RESOLVED="resolved_*"
COMPLEX="complex_*"
UNRESOLVED="unresolved_*"

cat ${RESOLVED} ${COMPLEX} ${UNRESOLVED} > v_res-com-unr_1.txt
cat v_res-com-unr_1.txt | awk -F " " '{ print $1}' > v_res-com-unr_2.txt
cat v_res-com-unr_2.txt | sort > v_res-com-unr_3.txt
# Remove lines beginning with '#'
cat v_res-com-unr_3.txt | sed -n '/^\#/!p' > v_res-com-unr_3.txt

cat ${LIST} > v_liste_1.txt
cat v_liste_1.txt | awk -F " " '{ print $1}' > v_liste_2.txt
cat v_liste_2.txt | sort > v_liste_3.txt
# Remove lines beginning with '#'
cat v_liste_3.txt | sed -n '/^\#/!p' > v_liste_4.txt

diff v_liste_4.txt v_res-com-unr_4.txt
