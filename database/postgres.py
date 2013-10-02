import os
import sys
import psycopg2
import psycopg2.extras
import exceptions
import time
import pprint

import transcirrus.common.logger as logger

class pgsql:
    def __init__(self,host,port,dbname,user,password):
        self.conn = psycopg2.connect("host=%s port=%s dbname=%s user=%s password=%s" %(host,port,dbname,user,password))
        #logger.sql("Connecting to %s with user %s" %(dbname,user))
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #name: pg_close_connection
    #desc: disconnect from sql server
    #ex: database.pg_close_connection(cur,con)
    #
    #output: void output, only disconnects from database server.
    def pg_close_connection(self):
        self.cur.close()
        self.conn.close()

    #######simple common db function insert - select - update - delete#######

    #name: pg_insert
    #desc: does a simple sql insert operation
    #input: self object
    #       table - table to insert new data into
    #       options - new values to insert into table
    #
    #ex: options
    #
    #output: success or fail
    def pg_insert(self,table,options):
        logger.sql_info("Performing simple INSERT operation pg_insert")

        #arrays used in in the insert operation
        keys = []
        values = []

        #strings and stuff
        keystring = ""
        valstring = ""

        #check if a table was passed in
        if table == " ":
            logger.sql_error("Table value not passed in pg_insert")
            logger.sql_error(exceptions.SystemError)

        if options:
            #iterate over the keys and get the values
            for key,value in options.items():
                keystring += ("%s," %key)
                valstring += ("'%s'," %value)
        else:
            logger.sql_error("Insert options were not passed")
            logger.sql_error(exceptions.SystemError)

        #strip of the junk commas
        stripkeys = keystring.rstrip('\,')
        stripvals = valstring.rstrip('\,')

        logger.sql_info("Inserting %s into db table %s" %(stripvals,table))
        self.cur.execute("""INSERT INTO %s(%s) VALUES (%s);""" %(table,stripkeys,stripvals))
        self.conn.commit()

    #name: pg_select
    #desc: does the standard simple sql select
    #input: pgsql cur object
    #       options dictionary
    #
    # ex:   options dicts {'select':"middle",'from':"test",'where':"first='jon'"}
    #                     {'select':"*",'from':'jon_test'}
    #
    #output: array containg simple select values
    def pg_select(self,options):
        logger.sql_info("Performing simple SELECT operation pg_select")
        #initalize everything
        selopt = ""
        fromopt = ""
        whereopt = ""
        andopt = ""
        oropt = ""
    
        #the strings
        SQL = ""
    
        #build out select
        if 'select' in options:
            selopt = options['select']
            if selopt != '' or selopt != '*':
                SQL += 'SELECT %s ' %selopt
            elif selopt == ' ':
                SQL += 'SELECT * '
        else:
            logger.sql_error("No SELECT statement given in pg_select")
            logger.sql_error(exceptions.SystemError)
    
        #build out from
        if 'from' in options:
            fromopt = options['from']
            SQL += 'FROM %s ' %fromopt
        else:
            logger.sql_error("No FROM statement given in pg_select")
            logger.sql_error(exceptions.SystemError)
    
        if 'where' in options:
            #add check for more than one where option
            whereopt = options['where']
            SQL += 'WHERE %s ' %whereopt
    
        if 'and' in options:
            andopt = options['and']
            SQL += 'AND %s' % andopt

        if 'or' in options:
            oropt = options['or']
            SQL += 'OR %s' % oropt

        # execute the built up simple select statement
        logger.sql_info(SQL)
        self.cur.execute(SQL)
    
        x = []
        for e in self.cur:
            # strip off white spaces on values and build array to return
            x.append(e)
        logger.sql_info("Returning values of simple select")
        return x
    
    #name: pg_delete
    #desc: delete a single entry from the table
    #input: options - the values to search the db on
    #
    #ex: database.pg_delete('options')
    #
    #output: returns a void and deletes the value from the table
    def pg_delete(self,options):
        logger.sql_info("Performing simple delete operation pg_delete")
    
        #initialize values
        whereopt = ""
        andopt = ""
        tableopt = ""
    
        #the sql string
        SQL = "DELETE FROM "
    
        if 'table' in options:
            tableopt = options['table']
            SQL += '%s ' %tableopt
        else:
            logger.sql_error("No table specified in simple sql delete operation.")
            logger.sql_error(exceptions.SystemError)

        if 'where' in options:
            #add check for more than one where option
            whereopt = options['where']
            SQL += 'WHERE %s ' %whereopt

        if 'and' in options:
            andopt = options['and']
            SQL += 'AND %s' % andopt

        if self.cur == "" or self.conn == "":
            logger.sql_error("Cursor or Connection object not passed in")

        #DELETE FROM products WHERE price = 10
        logger.sql_info("Deleting entry(s) where %s from table %s" %(options['where'],options['table']))
        self.cur.execute("""DELETE FROM %s WHERE (%s);""" %(options['table'],options['where']))
        self.cur.execute(SQL)
        self.conn.commit()

    #name: pg_update
    #desc: Update the database table
    #input: 
    #output:
    def pg_update(self,options):
        logger.sql_info(options)
        logger.sql_info("Performing simple UPDATE operation pg_update")

        #initialize values
        whereopt = ""
        andopt = ""
        tableopt = ""
        setopt = ""

        #the sql string
        SQL = "UPDATE "
        logger.sql_info(SQL)
        if 'table' in options:
            tableopt = options['table']
            SQL += '%s ' %tableopt
            logger.sql_info(SQL)
        else:
            logger.sql_error("No table specified in simple sql update operation.")
            logger.sql_error(exceptions.SystemError)

        if 'set' in options:
            setopt = options['set']
            SQL += 'SET %s ' %setopt
            logger.sql_info(SQL)
        else:
            logger.sql_error("No set options specified in simple sql update operation.")
            logger.sql_error(exceptions.SystemError) 

        if 'where' in options:
            #add check for more than one where option
            whereopt = options['where']
            SQL += 'WHERE %s ' %whereopt
            logger.sql_info(SQL)

        if 'and' in options:
            andopt = options['and']
            SQL += 'AND %s' % andopt
            logger.sql_info(SQL)

        logger.sql_info(SQL)
        self.cur.execute(SQL)
        self.conn.commit()

    def pg_transaction_begin(self):
        self.cur.execute("BEGIN")
        
    def pg_transaction_commit(self):
        self.cur.execute("COMMIT")
        
    def pg_transaction_rollback(self):
        self.cur.execute("ROLLBACK")

    #Count the elements that match query
    #options = {'table':'tablename','where':element,'and':element}
    def count_elements(self,options):
        logger.sql_info("Counting up elements")
        SQL = "SELECT count(*) FROM"

        if 'table' in options:
            tableopt = options['table']
            SQL += ' %s ' %tableopt
        else:
            logger.sql_error("No table specified in simple sql update operation.")
            logger.sql_error(exceptions.SystemError)
        
        if 'where' in options:
            whereopt = options['where']
            SQL += 'WHERE %s ' %whereopt

        if 'and' in options:
            andopt = options['and']
            SQL += 'AND %s' %andopt
        logger.sql_info(SQL)

        self.cur.execute(SQL)
        #self.conn.commit()
        out = None
        for e in self.cur:
            out = e[0]
        return out
'''
    def pg_inner_join(self,options):
        logger.sql_info("Performing an inner join on tables %s %s" %(options['table1'],options['table2']))
        #build out select
        if 'select' in options:
            selopt = options['select']
            if selopt != '' or selopt != '*':
                SQL += 'SELECT %s ' %selopt
            elif selopt == ' ':
                SQL += 'SELECT * '
        else:
            logger.sql_error("No SELECT statement given in pg_select")
            logger.sql_error(exceptions.SystemError)
    
        #build out from
        if 'from' in options:
            fromopt = options['from']
            SQL += 'FROM %s ' %fromopt
        else:
            logger.sql_error("No FROM statement given in pg_select")
            logger.sql_error(exceptions.SystemError)
'''

