#SQL Conection

import os

# To work with the .env file
from dotenv import load_dotenv
#pip install pyodbc
import pyodbc 


class SQLServer:
    _db_connection = None
    _db_cursor = None    
    _port="1433"      
    
    def __init__(self):
        load_dotenv()      
        server = os.getenv('IP_SERVER')  
        database_name=os.getenv('DATABASE_NAME') 
        user_server=os.getenv('USER_SERVER')  
        pass_server=os.getenv('PASS_SERVER')
        try:            
            self._db_connection =  pyodbc.connect('Driver={SQL Server}; Server='+server+';Port:'+self._port+'; Database='+database_name+'; UID='+user_server+'; PWD='+pass_server+';',autocommit=True)
            self._db_cursor = self._db_connection.cursor()
        except Exception as e:
            print(e)
    def __enter__(self):        
        return self._db_cursor
       
    def __exit__(self, exc_type, exc_value, traceback):
        # if exc_type or exc_value or traceback:
        #     self._db_connection.close()
        self._db_cursor.close()
        self._db_connection.close()
    
