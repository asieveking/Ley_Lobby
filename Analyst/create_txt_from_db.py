import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0])))
import SQL_Conection
#!pip install pandas
import pandas as pd

cnxn =SQL_Conection.SQLServer()
crsr= cnxn._db_cursor

query="SELECT * FROM [Ley_Lobby].[dbo].[Audiencias_All]"
df=pd.read_sql_query(query,cnxn._db_connection) #https://medium.com/@devartimahakalkar/connecting-sql-datasets-with-pandas-105f8eb68f1a
df = df.replace('\r\n','', regex=True)
path=os.path.join("D:/", "Tableau/Ley_Lobby")
os.makedirs(path,exist_ok=True) 
df.to_csv('D:/Tableau/Ley_Lobby/Audiencias_All.txt',index=False,  sep=';', mode="w")