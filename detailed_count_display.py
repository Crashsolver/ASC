import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import global_var as gv


def detailed_count_data(self):
    
    self.topwin = tk.Toplevel(self)
    self.topwin.title("Detailed Reports")
    self.topwin.configure(bg="#b7d7c7")
    
    window_height = gv.top_window_y
    window_width = gv.top_window_x
    if gv.platform_os == "Darwin":
        self.topwin.resizable(True, True)
        self.topwin.minsize(gv.top_window_x,gv.top_window_y)
        self.topwin.maxsize(gv.top_window_x,gv.top_window_y)
        
    screen_width = self.topwin.winfo_screenwidth()
    screen_height = self.topwin.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))+50
    y_cordinate = int((screen_height/2) - (window_height/2))-80
    self.topwin.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    
    self.topwin.columnconfigure(0,weight=1)
    self.topwin.columnconfigure(1,weight=10)
    
    self.topwin.rowconfigure(0,weight=1)
    self.topwin.rowconfigure(1,weight=1)
    self.topwin.rowconfigure(2,weight=1)
    self.topwin.rowconfigure(3,weight=24)
    
    self.settings_setting = []
    self.db_date = ""
    self.my_callsign = ""
    self.my_state = ""
    self.my_count = ""
    self.my_record = ""
    self.selected_detail_list = tk.StringVar()
    self.ve_detailed_list_high = []
    self.ve_detailed_list_equal = []
    self.ve_detailed_list_low = []
    self.ve_detailed_list_high_state = []
    self.ve_detailed_list_equal_state = []
    self.ve_detailed_list_low_state = []
    
    #sql_detailed_by_state = "SELECT * FROM ve_count WHERE state LIKE ?"
    #sql_detailed_by_total = "SELECT * FROM ve_count"
    sql_detailed_by_total_higher_count = "SELECT * FROM ve_count WHERE scount > ?"
    sql_detailed_by_total_lower_count = "SELECT * FROM ve_count WHERE scount < ?"
    sql_detailed_by_total_equal_count = "SELECT * FROM ve_count WHERE scount = ?"
    sql_detailed_by_state_higher_count = "SELECT * FROM ve_count WHERE scount > ? AND state LIKE ?"
    sql_detailed_by_state_lower_count = "SELECT * FROM ve_count WHERE scount < ? AND state LIKE ?"
    sql_detailed_by_state_equal_count = "SELECT * FROM ve_count WHERE scount = ? AND state LIKE ?"
    sql_by_call = "SELECT * FROM ve_count WHERE call LIKE ?"
    sql_by_call_cnt = "SELECT COUNT(*) FROM ve_count WHERE call LIKE ?"
    sql_by_defaults = "SELECT * FROM settings"
    
    ## open database and fetch info
    db_connection = sqlite3.connect(gv.asc_database)
    db_cursor = db_connection.cursor()
    db_cursor.execute(sql_by_defaults)
    self.settings_setting = db_cursor.fetchone()
    
    self.my_callsign = self.settings_setting[1] ## set up callsign
    self.my_state = self.settings_setting[3] ## set up state
    self.db_date = self.settings_setting[2] ## set up date
    
    tmp_result = []
    tmp_result.append('%'+self.my_callsign+'%')
    db_cursor.execute(sql_by_call_cnt,tuple(tmp_result)) ## Check if your callsign has multiple matches
    result = db_cursor.fetchall() ## to be used later
    match_count = result[0][0]
    
    if match_count == 1:
        tmp_result = []
        tmp_result.append('%'+self.my_callsign+'%')
        db_cursor.execute(sql_by_call,tuple(tmp_result))
        self.my_record = db_cursor.fetchone()
        self.my_count = self.my_record[4]  ## scount?
        
        tmp_result = []
        tmp_result.append(self.my_count)
        db_cursor.execute(sql_detailed_by_total_higher_count,tuple(tmp_result))
        self.ve_detailed_list_high = db_cursor.fetchall()
        
        
        db_cursor.execute(sql_detailed_by_total_equal_count,tuple(tmp_result))
        self.ve_detailed_list_equal = db_cursor.fetchall()
        
        
        db_cursor.execute(sql_detailed_by_total_lower_count,tuple(tmp_result))
        self.ve_detailed_list_low = db_cursor.fetchall()
        
        ## Let's narrow the scope to the state level
        
        tmp_result.append('%'+self.my_state+'%')
        db_cursor.execute(sql_detailed_by_state_higher_count,tuple(tmp_result))
        self.ve_detailed_list_high_state = db_cursor.fetchall()
        
        db_cursor.execute(sql_detailed_by_state_equal_count,tuple(tmp_result))
        self.ve_detailed_list_equal_state = db_cursor.fetchall()
        
        db_cursor.execute(sql_detailed_by_state_lower_count,tuple(tmp_result))
        self.ve_detailed_list_low_state = db_cursor.fetchall()
        
    else:
        pass ## will have to do something else if there is more than one match
    
    db_connection.close()
    
    ## Let's set up the GUI and populate it
    
    self.cancel_button = tk.Button(self.topwin, text="Cancel Report", command = self.topwin.destroy)
    self.cancel_button.grid(column=1, row=0, sticky='nw', padx=(20,5), pady=(5,5))
    
    self.cancel_button = tk.Button(self.topwin, text="Display Report", command = lambda: display_list(self))
    self.cancel_button.grid(column=0, row=0, sticky='nw', padx=(20,5), pady=(5,5))
    
    self.result_text2 = tk.Text(self.topwin)
    self.result_text2.grid(column=1, row=1, pady=4, padx=(20,30), sticky='nes')
    self.result_text2.configure(background="#d8f8d8", wrap="word", height=34, width=80,fg="#000000")
    self.result_text2.delete(1.0,tk.END)
    self.text_scroll = ttk.Scrollbar(self.topwin, orient=tk.VERTICAL, command=self.result_text2.yview)
    self.text_scroll.grid(column=1, row=1, sticky='nse', rowspan=20, pady=(5,5), padx=(10,10))
    self.result_text2['yscrollcommand'] = self.text_scroll.set
    
    self.select_detail = ttk.Combobox(self.topwin, width=13, textvariable=self.selected_detail_list)
    self.select_detail.grid(column=0, row=1, sticky='nw', padx=(5,5), pady=(5,5))
    self.select_detail['values'] = tuple(gv.select_report_list)
    self.select_detail['state'] = 'readonly'
    self.select_detail.set(gv.select_report_list_default)
    
    ## Make sure text window is blank
    #self.result_text2.delete(1.0,tk.END)
    see_list = mb.askquestion('See details','The chosen list can be very long. Are you sure?')
    if see_list == 'no':
        self.topwin.destroy()
    
    
def display_list(self):    
    list_selection = self.select_detail.get()
    self.result_text2.delete(1.0,tk.END)
    
    if list_selection == 'State Higher':
        operation = '>'
        sorted_list = massage_data(self.ve_detailed_list_high_state,operation,self.my_count)
    elif list_selection == 'State Equal':
        operation = '='
        sorted_list = massage_data(self.ve_detailed_list_equal_state,operation,self.my_count)
    elif list_selection == 'State Lower':
        operation = '<'
        sorted_list = massage_data(self.ve_detailed_list_low_state,operation,self.my_count)
    elif list_selection == 'Total Higher':
        line = 'Building listing, please wait...'
        self.result_text2.insert(tk.END,line+'\n')
        self.update_idletasks()
        operation = '>'
        sorted_list = massage_data(self.ve_detailed_list_high,operation,self.my_count)
    elif list_selection == 'Total Equal':
        line = 'Building listing, please wait...'
        self.result_text2.insert(tk.END,line+'\n')
        self.update_idletasks()
        operation = '='
        sorted_list = massage_data(self.ve_detailed_list_equal,operation,self.my_count)
    elif list_selection == 'Total Lower':
        line = 'Building listing, please wait...'
        self.result_text2.insert(tk.END,line+'\n')
        self.update_idletasks()
        operation = '<'
        sorted_list = massage_data(self.ve_detailed_list_low,operation,self.my_count)
        
    self.result_text2.delete(1.0,tk.END)
    self.update_idletasks()
    for line in sorted_list:
        self.result_text2.insert(tk.END,line+'\n')
            
    
    text_text = "End of report\n"
    self.result_text2.insert(tk.END,text_text)
    
def massage_data(data,operation,count):
    sorted_data = sort_list_of_tuples(data)
    new_list = []
    for record in sorted_data:
        if operation == '>':
            if int(record[4]) > int(count):
                text_line = "Count:{}, Call:{}, County:{}, State:{}".format(record[4],record[1],record[2],record[5])
                new_list.append(text_line)
        elif operation == '=':
            if int(record[4]) == int(count):
                text_line = "Count:{}, Call:{}, County:{}, State:{}".format(record[4],record[1],record[2],record[5])
                new_list.append(text_line)
        elif operation == '<':
            if int(record[4]) < int(count):
                text_line = "Count:{}, Call:{}, County:{}, State:{}".format(record[4],record[1],record[2],record[5])
                new_list.append(text_line)
    return new_list
 
   
def sort_list_of_tuples(lt):
        ## bubble sort a list of tuples with highest count at the top
        list_length = len(lt)
        ## subtle reference to a JK flipflop circuit
        for j in range(0, list_length):
            for k in range(0, list_length-j-1):
                if (int(lt[k][4]) < int(lt[k + 1][4])):
                    temp_tuple = lt[k]
                    lt[k] = lt[k + 1]
                    lt[k + 1] = temp_tuple
        return lt