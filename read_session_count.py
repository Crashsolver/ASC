import pandas as pd
import sqlite3
import global_var as gv
from datetime import date
import tkinter as tk
from tkinter import scrolledtext as st

def get_count(self,state):
    
    ## This function checks each line of data against the database
    ## either it inserts a new record, or it updates an existing record
    
    db_connection = sqlite3.connect(gv.asc_database)
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT * FROM settings")
    setting = db_cursor.fetchone()
    
    website = gv.arrl_url + state
    today = []
    result = []
    
    ## windows needs this
    ## works okay in Linux
    data_frame = pd.read_html(website,flavor='html5lib')
    
    ## Convert data frame into a list of lists
    result = data_frame[0].to_numpy().tolist()
    length_list = len(result)
    ## result is a list of lists
    ## read each record from list of lists
    initial_tag = '0' ## set initial update tag
    for record in result:
        ve_record = []
        call_check = []
        
        ## we now have a list 'record' with [call,county,accreditation date,count]
        ## check if callsign exist in current table
        ## Parse the record to just the callsign
        call_record = record[0]
        call_check.append(call_record)
        
        db_cursor.execute("SELECT * FROM ve_count WHERE call = ?",tuple(call_check))
        record_check = db_cursor.fetchall()
        
        ## 'record_check' is a list type set to 'None' if no record was fetched
        ## transfer over the record from the ARRL
        index = 0
        for item in gv.ve_input_list:
            ve_record.append(record[index])
            index += 1
        ## append the state
        ve_record.append(state)
        ve_record.append(initial_tag) ## set the update tag to false
        ## if a blank was returned, do an insert
        if record_check == None or record_check == []:
            index = 0
            ## Check each element in the list for missing data
            for element in ve_record:
                ## ran across an entry where the county was missing (index = 1)
                if type(element)  != str and index == 1:
                    ## substitute 'Not Available' for missing list element
                    ve_record[index] = "N-A"
                index += 1
            
            rec_cols = ', '.join(gv.ve_field_list)
            q_marks = ','.join(list('?'*len(gv.ve_field_list)))
            values = tuple(ve_record)
            sql = "INSERT INTO ve_count ("+rec_cols+") VALUES ("+q_marks+")"
            db_cursor.execute(sql,values)
            db_connection.commit()
            
        else: ## record exists, do an update
            tag_update = '1'
            values = tuple([record[3],tag_update,call_check[0]]) ## set
            sql = "UPDATE ve_count SET scount = ?, tag = ? WHERE call = ?"
            db_cursor.execute(sql,values)
            db_connection.commit()
    
    ## TODO: add to menu, a purge of entries where after an update, tag_column = '0'
    ## VE can lose accreditation or pass away. Without a purge function, they will
    ## occupy entries in database
           
    ## update the date of this action in 'settings' table
    today_date = str(date.today())
    today.append(today_date)
    sql = "UPDATE settings SET date = ?"
    db_cursor.execute(sql,tuple(today))
    db_connection.commit()
    db_connection.close()
            
            
        