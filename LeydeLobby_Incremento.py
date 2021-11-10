
import pyodbc 
import requests
import traceback
import datetime
import html

#---------------------------------------
class SQLServer:
    _db_connection = None
    _db_cursor = None

    def __init__(self):
       self._db_connection =  pyodbc.connect('Driver={SQL Server}; Server=localhost\SQLEXPRESS;Port:1433; Database=Ley_Lobby; Trusted_Connection=yes;',autocommit=True)
       self._db_cursor = self._db_connection.cursor()

    def closeConnection(self):
       self._db_cursor.close()
       self._db_connection.close()

#---------------------------------------
def quitar_tildes(texto):
    a,b = 'áéíóúüÁÉÍÓÚÜ','aeiouuAEIOUU'
    trans = str.maketrans(a,b)
    return texto.translate(trans).strip()

def limpiar_texto(texto):      
    texto=" ".join(texto.split())    
    texto =texto.replace('--', ' ').replace(':-', ':').replace('**', ' ').replace('""', '"')#.replace('..', '.')  expresion regular
    texto=" ".join(texto.split())    
    texto=html.unescape(texto)
    texto =texto.replace(' :', ': ').replace(' ,', ', ').replace(' .', '. ').replace(' "', '" ').replace('""', '').replace('( ', ' (').replace(' )', ') ').replace(' -', '-').replace('- ', '-')         
    return quitar_tildes(texto)

def quitar_puntos(texto):    
    texto=texto.replace('.','').strip()    
    return texto
    
def total_caracteres(texto):
    return texto[:4790]

def stringafecha(fecha):
    return datetime.datetime.strptime(fecha,'%Y-%m-%d')

def stringafechatiempo(fecha):
    return datetime.datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S') 

def es_vacio_o_nulo(valor):
    if valor and type(valor) is str:
        valor=valor.strip() 
    if type(valor) is int:
        return False
    if not valor or valor is None or valor=="":
        return True
    return False    

#---------------------------------------
class Persona:
    _idperfil=None  #string
    _idsujeto=None #number    
    _nombres=None
    _apellidos=None
    _idcargoInstitucion=None
    
    def __init__(self,idsujeto,nombres,apellidos):
        self._idsujeto=idsujeto
        if es_vacio_o_nulo(nombres)is False:
            nombres=nombres.strip().upper()
            self._nombres=quitar_tildes(nombres)
        if es_vacio_o_nulo(apellidos)is False:    
            apellidos=apellidos.strip().upper()
            self._apellidos=quitar_tildes(apellidos)

class Instituciones:
    _idInstitucion=None
    _instituciones=[]

    def getCodigo(self):
        for ins in self._instituciones:
            if ins[0]==self._idInstitucion:
                return ins[1]
        return None
    
    
class Cargo:
    _idcargoInstitucion=None
    _cargo=None
    _resolucion=None
    _url_resolucion=None
    _fecha_inicio=None
    _fecha_termino=None
    _cargos = []

    def getValidarCargo(self):
        for carg in self._cargos:          
            if carg[0]==self._idcargoInstitucion and  es_vacio_o_nulo(carg[1])is False:
                return True
        return False        
    
    
    def __init__(self,idcargoInstitucion,cargo,resolucion,url_resolucion,fecha_inicio,fecha_termino):       
        self._idcargoInstitucion=idcargoInstitucion
       
        if es_vacio_o_nulo(cargo)is False:
            self._cargo=limpiar_texto(cargo).upper()
        if es_vacio_o_nulo(resolucion)is False:
            resolucion=limpiar_texto(resolucion).upper()
            self._resolucion=total_caracteres(resolucion)            
        if es_vacio_o_nulo(url_resolucion)is False:
            self._url_resolucion=url_resolucion.strip()
        if es_vacio_o_nulo(fecha_inicio)is False :
            self._fecha_inicio=stringafecha(fecha_inicio)
        if es_vacio_o_nulo(fecha_termino)is False:
            self._fecha_termino=stringafecha(fecha_termino)
            

            
class Audiencia:
    _idAudiencia=None       
    _lugar=None
    _observacion=None
    _ubicacion=None    
    _urlInfolobby='https://www.infolobby.cl/Ficha/Audiencia/'
    _urlLeylobby='https://www.leylobby.gob.cl/instituciones/'
    _fechaInicio=None
    _fechaTermino=None
        
    def __init__(self,id_audiencia,lugar,observacion,ubicacion,fechaInicio,fechaTermino):
        self._idAudiencia=id_audiencia 
        if es_vacio_o_nulo(fechaInicio)is False:
            self._fechaInicio=stringafechatiempo(fechaInicio)
        if es_vacio_o_nulo(fechaTermino)is False:     
            self._fechaTermino=stringafechatiempo(fechaTermino)
        if es_vacio_o_nulo(ubicacion)is False:   #Comuna
            self._ubicacion=limpiar_texto(ubicacion)
        if es_vacio_o_nulo(lugar)is False :
            self._lugar=limpiar_texto(lugar)
        if es_vacio_o_nulo(observacion)is False:
            observacion=limpiar_texto(observacion)                      
            self._observacion=total_caracteres(observacion)
            

    def urlbuild(self, codigoInstitucion, idCargo):          
        self._urlInfolobby= f'{self._urlInfolobby}{codigoInstitucion}{self._idAudiencia}1'
        anio=self._fechaInicio.year#.strftime("%Y")# .split("-")[0]   
        self._urlLeylobby= f'{self._urlLeylobby}{codigoInstitucion}/audiencias/{anio}/{idCargo}/{self._idAudiencia}' 
      #https://www.infolobby.cl/Ficha/Audiencia/AE006312971
      #https://www.leylobby.gob.cl/instituciones/AE006/audiencias/2015/1723/31297  

class Entidad:
    _rut=None
    _nombre=None    
    _giro=None
    _domicilio=None
    _representante=None
    _naturaleza=None
    _directorio=None    

    def __init__(self,rut,nombre,giro,domicilio,representante,naturaleza,directorio):
        if es_vacio_o_nulo(rut)is False :
            rut=quitar_puntos(rut).upper()   
            if len(rut)>=9 and len(rut) <=10:
               self._rut=rut    
        if es_vacio_o_nulo(nombre)is False:
            self._nombre=limpiar_texto(nombre).upper()
        if es_vacio_o_nulo(giro)is False:
            self._giro=limpiar_texto(giro).upper()
        if es_vacio_o_nulo(representante)is False:
            representante=limpiar_texto(representante)
            self._representante=quitar_puntos(representante).upper()
        if es_vacio_o_nulo(naturaleza)is False:
            self._naturaleza=limpiar_texto(naturaleza).upper()
        if es_vacio_o_nulo(domicilio)is False:
            self._domicilio=limpiar_texto(domicilio).upper() 
        if es_vacio_o_nulo(directorio)is False:
            directorio=limpiar_texto(directorio)
            self._directorio=quitar_puntos(directorio).upper()
                
class Materia:
    _nombre=None
    
    def __init__(self,nombre):
        if  es_vacio_o_nulo(nombre)is False:  
            self._nombre=limpiar_texto(nombre)
      
#---------------------------------------




detail_data=[]
#payload = {}
headers= {'Api-Key':'$2y$10$aEfzqlCR9Mpw5AgNoy8jS.Ji41kjDVhjakkKjPGRnqR', 'content-type':'application/json'}

apiAP="https://www.leylobby.gob.cl/api/v1/audiencias?page="
apiA="https://www.leylobby.gob.cl/api/v1/audiencias/"
apiCP="https://www.leylobby.gob.cl/api/v1/cargos-pasivos/"
apiI="https://www.leylobby.gob.cl/api/v1/instituciones/"

cnxn =SQLServer()
crsr= cnxn._db_cursor

#List instituciones
crsr.execute('SELECT Id_Institucion, Id_Codigo FROM Ley_Lobby.dbo.Institucion')
objInstitucion =Instituciones()
objInstitucion._instituciones = crsr.fetchall()

#Num_page INCREMENTO
statement ='SELECT Page_Incremento FROM Ley_Lobby.dbo.Num_Page where Area_Num_Page=?'
crsr.execute(statement,["Audiencia"])
num_page =crsr.fetchall()[0][0]-2


while True:    
    url= f'{apiAP}{num_page}'
#     print(num_page)
    try:
        response=requests.request("GET", url, headers=headers, verify=False)             
        data=response.json()   
#         detail_data+=data["data"]

        #Loop audiencias por page
        for aud in data["data"]:

            #Load Audiencia
            objAud=Audiencia(aud["id_audiencia"],aud['lugar'],aud['referencia'],aud['comuna'],aud['fecha_inicio'],aud['fecha_termino'])   #(self,id_audiencia,lugar,observacion,ubicacion,id_cargo):
            
            #Load Institucion
            objInstitucion._idInstitucion=aud['id_institucion']
            codInst = objInstitucion.getCodigo()

            #Si institucion no existe entonces Insert Institucion
            if codInst is None:
                urlI= f'{apiI}{objInstitucion._idInstitucion}'
                response=requests.request("GET", urlI, headers=headers, verify=False)             
                insti=response.json() 
                codInst = insti["codigo"]
                #Load a lista instituciones
                objInstitucion._instituciones.append([objInstitucion._idInstitucion,insti["codigo"]])
                #Insert data
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Institucion_sp] ?,?,?;"
                params= (objInstitucion._idInstitucion,insti["codigo"],insti["nombre"])   
                crsr.execute(storeProcedure,params)            

            #Load Cargo Pasivo            
            objPersPasi=Persona(aud["id_sujeto_pasivo"],aud['nombres'],aud['apellidos'])    #(self,perfil,nombres,apellidos):   
            objPersPasi._idcargoInstitucion=aud['id_cargo']
            

            #Insert Persona Pasiva            
            storeProcedure=" EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?;"
            params= (objPersPasi._idsujeto,'Pasivo',objPersPasi._nombres,objPersPasi._apellidos)
            crsr.execute(storeProcedure,params)
            objPersPasi._idperfil=crsr.fetchval()

            objPersPasi._idperfilcargoInstitucion=f'{objPersPasi._idperfil}-{objPersPasi._idcargoInstitucion}' 
           
            #Search and Insert todos los cargos de Persona Pasiva
            urlP=f'{apiCP}{objPersPasi._idsujeto}'
            responseP=requests.request("GET",urlP, headers=headers, verify=False)
            for pas in responseP.json():    
                objCargo=Cargo(pas["id_cargo_pasivo"],pas["cargo"],pas["resolucion"],pas["resolucion_url"],pas["fecha_inicio"],pas["fecha_termino"])   
                #List Cargoinstituciones --------------------------------------------------
                if len(objCargo._cargos) == 0:
                    statement='SELECT IHC.Id_Institucion_Cargo,PHC.Id_Perfil_Cargo FROM Ley_Lobby.dbo.Institucion_Has_Cargo IHC left join Ley_Lobby.dbo.Perfil_Has_Cargo PHC on IHC.Id_Institucion_Cargo= PHC.Id_Institucion_Cargo where PHC.Id_Perfil =?'
                    crsr.execute(statement,[objPersPasi._idperfil])
                    objCargo._cargos = crsr.fetchall()
                if objCargo.getValidarCargo() is False:
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Institucion_Has_Cargo_sp] ?,?,?,?,?,?,?;"
                    crsr.execute(storeProcedure,[objCargo._idcargoInstitucion,pas["id_institucion"],objCargo._fecha_inicio,objCargo._fecha_termino,objCargo._cargo,objCargo._resolucion,objCargo._url_resolucion])
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Cargo_sp] ?,?;"
                    #objPersPasi._idperfilcargoInstitucion  Internamente, en el Store Procedure, se crea el _idperfilcargoInstitucion
                    crsr.execute(storeProcedure,[objPersPasi._idperfil,objCargo._idcargoInstitucion])  
                

            #Create url's infoLobby & LeyLobby     
            objAud.urlbuild(codInst,objPersPasi._idcargoInstitucion)                   
            
            
            #Detalle de Audiencia e Insert
            urlA=f'{apiA}{objAud._idAudiencia}'
            responseA=requests.request("GET",urlA, headers=headers,  verify=False)
            detalle=responseA.json()
            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_sp] ?,?,?,?,?,?,?,?,?;"
            crsr.execute(storeProcedure,[objAud._idAudiencia,objAud._fechaInicio,objAud._fechaTermino,objAud._lugar,detalle['forma'],objAud._observacion,objAud._ubicacion,objAud._urlInfolobby,objAud._urlLeylobby])             
            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?;"
            crsr.execute(storeProcedure,[objAud._idAudiencia,objPersPasi._idperfilcargoInstitucion,'Principal']) 

            #Insert Materias
            for mat in detalle['materias']:
                objMateria=Materia(mat['nombre'])
                if es_vacio_o_nulo(objMateria._nombre )is False:
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_Has_Materia_sp] ?,?;"
                    crsr.execute(storeProcedure,[objAud._idAudiencia,objMateria._nombre]) 
            
            #Insert Cargos Activos,
            for act in detalle['asistentes']:
                objPersAct= Persona(act['id_cargo_activo'],act['nombres'],act['apellidos'])                  
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?"                
                crsr.execute(storeProcedure,[objPersAct._idsujeto,'Activo',objPersAct._nombres,objPersAct._apellidos])                
                objPersAct._idperfil=crsr.fetchval()                
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Cargo_sp] ?,?;"
                crsr.execute(storeProcedure,[objPersAct._idperfil,None])  
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?;"
                crsr.execute(storeProcedure,[objAud._idAudiencia,objPersAct._idperfil,None])

                #Insert Empresa/Entidad del Persona Activo
                if 'rut_representado' in act['representa']:
                    representa=act['representa']
                    objEntidad=Entidad(representa['rut_representado'],representa['nombre'],representa['giro'],representa['domicilio'],representa['representante_legal'],representa['naturaleza'],representa['directorio'])  #(self,rut,nombre,giro,domicilio,representante,naturaleza,directorio):                                        
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Entidad_sp] ?,?,?,?,?,?,?,?;"                    
                    crsr.execute(storeProcedure,[objEntidad._rut,objEntidad._nombre,objEntidad._giro,objEntidad._representante,objEntidad._directorio,representa['pais'],objEntidad._domicilio,objEntidad._naturaleza])
                    objEntidad._id_Entidad= crsr.fetchval() 
                    if  objEntidad._id_Entidad!=0:
                        storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Entidad_sp] ?,?;"
                        crsr.execute(storeProcedure,[objPersAct._idperfil,objEntidad._id_Entidad])                          
            
                #insert_perfil_institucion('369-P',259, '2014-11-26',null,'Integrante de Comisión Evaluadora formada en el marco de la Ley N° 19886','','http://documentos.minvu.cl/min_vivienda/resoluciones_exentas/Documents/res%20ex%20electronica%20783.pdf');          
    except Exception as exception:
        print(exception) 
        traceback.print_exc()    
        print(f'idAudiencia:{objAud._idAudiencia}   N° pag: {num_page}')
        #crsr.rollback()
        break;      
    else:
        num_page += 1   
        if num_page>data["last_page"]:  
            print('todo ok')      
            break       
        statement = 'UPDATE Ley_Lobby.dbo.Num_Page set PAGE_INCREMENTO=?  WHERE Area_Num_Page=?'
        crsr.execute(statement,[num_page,"AUDIENCIA"])
        
        
cnxn.closeConnection()    


#Validar largo del RUT en PYTHON