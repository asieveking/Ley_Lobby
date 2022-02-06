#SQL Conection
#pip install pyodbc
import pyodbc 

class SQLServer:
    _db_connection = None
    _db_cursor = None
    _server="192.168.31.95"
    _port="1433"
    _database="Mercado_Publico"
    _user="Proyectos"
    _password="Proyectos"

    
    def __init__(self):
        try:
            #self._db_connection =  pyodbc.connect('Driver={SQL Server}; Server=localhost\SQLEXPRESS;Port:1433; Database=Mercado_Publico; Trusted_Connection=yes;',autocommit=True)
            self._db_connection =  pyodbc.connect('Driver={SQL Server}; Server='+self._server+';Port:'+self._port+'; Database='+self._database+'; UID='+self._user+'; PWD='+self._password+';',autocommit=True)
            self._db_cursor = self._db_connection.cursor()
        except:
            pass
    def __enter__(self):        
        return self._db_cursor
       
    def __exit__(self, exc_type, exc_value, traceback):
        # if exc_type or exc_value or traceback:
        #     self._db_connection.close()
        self._db_cursor.close()
        self._db_connection.close()
    
