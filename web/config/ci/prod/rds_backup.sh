#!/bin/bash -e

export PGPASSWORD="whvc.1900"

DATETIME=`date "+%Y%m%d_%H%M"`
FILE_NAME="aahodbprod_$DATETIME".sql 

#echo "$FILE_NAME"
pg_dump -d aahodb -U aaho -h 'aahodbprod.cow111xuzv8n.ap-south-1.rds.amazonaws.com' -p 5432 -f "$FILE_NAME"

aws s3 cp "$FILE_NAME" s3://aahordsbackup

rm -rf "$FILE_NAME"
