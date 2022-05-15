import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))
import sample.sql_connection as sql_connection

import pandas as pd


cnxn =sql_connection.SQLServer()
crsr= cnxn.db_cursor


path=os.path.join("D:/", "Tableau/Ley_Lobby")
os.makedirs(path,exist_ok=True) 

query="SELECT * FROM [Ley_Lobby].[dbo].[Audiencias_All]"
df=pd.read_sql_query(query,cnxn.db_connection) #https://medium.com/@devartimahakalkar/connecting-sql-datasets-with-pandas-105f8eb68f1a
df = df.replace('\r\n','', regex=True)
df.to_csv('D:/Tableau/Ley_Lobby/Audiencias_All.txt',index=False,  sep=';', mode="w")

query="SELECT * FROM [Ley_Lobby].[dbo].[Perfil_Licitacion]"
df=pd.read_sql_query(query,cnxn.db_connection) #https://medium.com/@devartimahakalkar/connecting-sql-datasets-with-pandas-105f8eb68f1a
df = df.replace('\r\n','', regex=True)
df.to_csv('D:/Tableau/Ley_Lobby/Perfil_Licitacion.txt',index=False,  sep=';', mode="w")