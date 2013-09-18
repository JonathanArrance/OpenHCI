#!/usr/bin/python

import sys


#import the pgsql class from postgres
from transcirrus.database.postgres import pgsql
import transcirrus.common.logger as logger

#connect to the database
pg = pgsql('192.168.10.16','5432','cac_system','cacsystem','cacsystem')

#print the connection object
print pg

#insert something into the unit test table
insert = {"index":"6","parameter":"yo","param_value":"test"}
pg.pg_insert("unit_test",insert)
logger.sql_info("This is an insert test.")

#get the newly inserted info
select1 = {'select':'*','from':'unit_test'}
sel = pg.pg_select(select1)
logger.sql_info("This is a select test")
print sel
logger.sql_info(sel)

#Delete a record
logger.sql_info("This is a delete test")
insert = {"index":"50","parameter":"test","param_value":"test"}
pg.pg_insert("unit_test",insert)
delete = {"table":'unit_test',"where":"parameter='test'", "and":"index='50'"}
pg.pg_delete(delete)

#update a db entry
logger.sql_info("This is a update test")
insert = {"index":"51","parameter":"tester","param_value":"teser"}
pg.pg_insert("unit_test",insert)
update = {'table':"unit_test",'set':"param_value='tester'",'where':"index='51'"}
pg.pg_update(update)
select1 = {'select':'*','from':'unit_test'}
sel = pg.pg_select(select1)

#close the connection
pg.pg_close_connection()
