#SQL Conection
import os

from dotenv import load_dotenv

import pyodbc 


class SQLServer:
    db_connection = None
    db_cursor = None    
    port="1433"      
    
    def __init__(self):
        load_dotenv()      
        server = os.getenv('IP_SERVER')  
        database_name=os.getenv('DATABASE_NAME') 
        user_server=os.getenv('USER_SERVER')  
        pass_server=os.getenv('PASS_SERVER')
        try:            
            self.db_connection =  pyodbc.connect('Driver={SQL Server}; Server='+server+';Port:'+self.port+'; Database='+database_name+'; UID='+user_server+'; PWD='+pass_server+';',autocommit=True)
            self.db_cursor = self.db_connection.cursor()
        except Exception as e:
            print(e)
    def __enter__(self):        
        return self.db_cursor
       
    def __exit__(self, exc_type, exc_value, traceback):      
        self.db_cursor.close()
        self.db_connection.close()

    def get_all_rows(self,query:str,params:tuple = ()) -> list:
        return self.db_cursor.execute(query, params).fetchall()    

    def update(self,query:str, params:tuple) -> None:
        self.db_cursor.execute(query,params)