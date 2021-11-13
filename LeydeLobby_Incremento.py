
import pyodbc 
import requests
import traceback
import datetime, time

import Funciones
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
    
def total_caracteres(texto):
    return texto[:4790]

#---------------------------------------
class Persona:
    _id_perfil=None  #string
    _idsujeto=None #number    
    _nombres=None
    _apellidos=None
    _id_cargoInstitucion=None
    
    def __init__(self,idsujeto,nombres,apellidos):
        self._idsujeto=idsujeto
        if Funciones.es_vacio_o_nulo(nombres)is False:
            nombres=" ".join(nombres.title().split())
            self._nombres=Funciones.quitar_tildes(nombres)
        if Funciones.es_vacio_o_nulo(apellidos)is False:    
            apellidos=" ".join(apellidos.title().split())
            self._apellidos=Funciones.quitar_tildes(apellidos)

class Instituciones:
    _id_institucion=None
    _instituciones=[]

    def getCodigo(self):
        cod=[ id[1] for id in self._instituciones if id[0]==self._id_institucion ]       
        return cod[0] if len(cod)>0 else None
    
class Cargo:
    _id_cargoInstitucion=None
    _cargo=None
    _resolucion=None
    _url_resolucion=None
    _fecha_inicio=None
    _fecha_termino=None
    _list_cargos = []

    def getValidarCargo(self):
        for carg in self._list_cargos:          
            if carg[0]==self._id_cargoInstitucion and Funciones.es_vacio_o_nulo(carg[1])is False:
                return True
        return False      
    
    def __init__(self,id_cargo_institucion,cargo,resolucion,url_resolucion,fecha_inicio,fecha_termino):       
        self._id_cargoInstitucion=id_cargo_institucion
       
        if Funciones.es_vacio_o_nulo(cargo)is False:
            self._cargo=Funciones.limpiar_texto(cargo).title()
        if Funciones.es_vacio_o_nulo(resolucion)is False:
            resolucion=Funciones.limpiar_texto(resolucion).capitalize()
            self._resolucion=total_caracteres(resolucion)            
        if Funciones.es_vacio_o_nulo(url_resolucion)is False:
            self._url_resolucion=url_resolucion.strip()
        if Funciones.es_vacio_o_nulo(fecha_inicio)is False :
            self._fecha_inicio=Funciones.stringafecha(fecha_inicio)
        if Funciones.es_vacio_o_nulo(fecha_termino)is False:
            self._fecha_termino=Funciones.stringafecha(fecha_termino)
            
            
class Audiencia:
    _id_audiencia=None       
    _lugar=None
    _observacion=None
    _ubicacion=None    
    _url_info_lobby='https://www.infolobby.cl/Ficha/Audiencia/'
    _url_ley_lobby='https://www.leylobby.gob.cl/instituciones/'
    _fecha_inicio=None
    _fechaTermino=None
        
    def __init__(self,id_audiencia,lugar,observacion,ubicacion,fecha_inicio,fechaTermino):
        self._id_audiencia=id_audiencia 
        if Funciones.es_vacio_o_nulo(fecha_inicio)is False and fecha_inicio.isnumeric() is False:
            self._fecha_inicio=Funciones.stringafechatiempo(fecha_inicio)
        if Funciones.es_vacio_o_nulo(fechaTermino)is False and fechaTermino.isnumeric() is False:     
            self._fechaTermino=Funciones.stringafechatiempo(fechaTermino)
        if Funciones.es_vacio_o_nulo(ubicacion)is False and ubicacion.isnumeric() is False:   #Comuna
            self._ubicacion=Funciones.limpiar_texto(ubicacion).title()
        if Funciones.es_vacio_o_nulo(lugar)is False and lugar.isnumeric() is False :
            self._lugar=Funciones.limpiar_texto(lugar).title()
        if Funciones.es_vacio_o_nulo(observacion)is False and observacion.isnumeric() is False:
            observacion=Funciones.limpiar_texto(observacion).capitalize()                      
            self._observacion=total_caracteres(observacion)
            

    def url_build_web(self, codigo_institucion, id_cargo):          
        self._url_info_lobby= f'{self._url_info_lobby}{codigo_institucion}{self._id_audiencia}1'
        #anio=self._fecha_inicio.year#.strftime("%Y")# .split("-")[0]   
        self._url_ley_lobby= f'{self._url_ley_lobby}{codigo_institucion}/audiencias/{self._fecha_inicio.year}/{id_cargo}/{self._id_audiencia}' 
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
        if Funciones.es_vacio_o_nulo(rut)is False and type(rut) is str and len(rut)>=8 and len(rut) <=12  and rut.replace(".","").replace("-","").replace(" ","")[:-1].isnumeric() is True:
            self._rut=Funciones.dar_formato_al_rut(rut)  
        if Funciones.es_vacio_o_nulo(nombre)is False and nombre.isnumeric() is False:
            self._nombre=Funciones.limpiar_texto(nombre).upper()
        if Funciones.es_vacio_o_nulo(giro)is False and giro.isnumeric() is False:
            self._giro=Funciones.limpiar_texto(giro).title()
        if Funciones.es_vacio_o_nulo(representante)is False and representante.isnumeric() is False:
            representante=Funciones.limpiar_texto(representante)
            self._representante=Funciones.quitar_puntos(representante).title()
        if Funciones.es_vacio_o_nulo(naturaleza)is False and naturaleza.isnumeric() is False:
            self._naturaleza=Funciones.limpiar_texto(naturaleza).title()
        if Funciones.es_vacio_o_nulo(domicilio)is False and domicilio.isnumeric() is False:
            self._domicilio=Funciones.limpiar_texto(domicilio).title()
        if Funciones.es_vacio_o_nulo(directorio)is False and directorio.isnumeric() is False:
            directorio=Funciones.limpiar_texto(directorio)
            self._directorio=Funciones.quitar_puntos(directorio).title()
                
class Materia:
    _nombre=None
    
    def __init__(self,nombre):
        if  Funciones.es_vacio_o_nulo(nombre)is False:  
            self._nombre=Funciones.limpiar_texto(nombre)
#---------------------------------------


time_start=time.time()
header= {'Api-Key':'$2y$10$aEfzqlCR9Mpw5AgNoy8jS.Ji41kjDVhjakkKjPGRnqR', 'content-type':'application/json'}
cnxn =SQLServer()
crsr= cnxn._db_cursor

#List instituciones
crsr.execute('SELECT Id_Institucion, Id_Codigo FROM Ley_Lobby.dbo.Institucion')
obj_institucion =Instituciones()
obj_institucion._instituciones = crsr.fetchall()

#Num_page INCREMENTO
statement ='SELECT Page_Incremento FROM Ley_Lobby.dbo.Num_Page where Area_Num_Page=?'
crsr.execute(statement,["Audiencia"])
num_page =crsr.fetchall()[0][0]-2

cantidad_total_de_peticiones_establecidos_en_la_API=8000

while True:    
    url=Funciones.url_build_ley_lobby("Audiencias_Page",num_page) 
#   
    try:
        list_audiencias_api,cantidad_total_de_peticiones_establecidos_en_la_API,time_start=Funciones.get_api(url,time_start,cantidad_total_de_peticiones_establecidos_en_la_API,header,False,2)

        #Loop audiencias por page        
        for audiencia in list_audiencias_api["data"]:

            #Load Audiencia
            obj_audiencia=Audiencia(audiencia["id_audiencia"],audiencia['lugar'],audiencia['referencia'],audiencia['comuna'],audiencia['fecha_inicio'],audiencia['fecha_termino'])   #(self,id_audiencia,lugar,observacion,ubicacion,id_cargo):
            
            #Load Institucion
            obj_institucion._id_institucion=audiencia['id_institucion']
            cod_institucion = obj_institucion.getCodigo()

            #Si institucion no existe entonces Insert Institucion
            if cod_institucion is None:
                url=Funciones.url_build_ley_lobby("Instituciones",obj_institucion._id_institucion)                         
                institucion,cantidad_total_de_peticiones_establecidos_en_la_API,time_start=Funciones.get_api(url,time_start,cantidad_total_de_peticiones_establecidos_en_la_API,header,False,2)
                cod_institucion = institucion["codigo"]
                #Load a lista instituciones
                obj_institucion._instituciones.append([obj_institucion._id_institucion,institucion["codigo"]])
                #Insert data
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Institucion_sp] ?,?,?;"
                params= (obj_institucion._id_institucion,institucion["codigo"],institucion["nombre"])   
                crsr.execute(storeProcedure,params)            

            #Load Cargo Pasivo            
            obj_persona_pasiva=Persona(audiencia["id_sujeto_pasivo"],audiencia['nombres'],audiencia['apellidos'])    #(self,perfil,nombres,apellidos):   
            obj_persona_pasiva._id_cargoInstitucion=audiencia['id_cargo']

            #Insert Persona Pasiva            
            storeProcedure=" EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?;"
            params= (obj_persona_pasiva._idsujeto,'Pasivo',obj_persona_pasiva._nombres,obj_persona_pasiva._apellidos)
            crsr.execute(storeProcedure,params)
            obj_persona_pasiva._id_perfil=crsr.fetchval()

            obj_persona_pasiva._id_perfil_cargo_institucion=f'{obj_persona_pasiva._id_perfil}-{obj_persona_pasiva._id_cargoInstitucion}' 
           
            
            url=Funciones.url_build_ley_lobby("Cargos_Pasivos",obj_persona_pasiva._idsujeto)              
            list_cargos_pasivos_api,cantidad_total_de_peticiones_establecidos_en_la_API,time_start=Funciones.get_api(url,time_start,cantidad_total_de_peticiones_establecidos_en_la_API,header,False,2)
            #Search and Insert todos los cargos de Persona Pasiva
            for cargo_pasivo in list_cargos_pasivos_api:    
                objCargo=Cargo(cargo_pasivo["id_cargo_pasivo"],cargo_pasivo["cargo"],cargo_pasivo["resolucion"],cargo_pasivo["resolucion_url"],cargo_pasivo["fecha_inicio"],cargo_pasivo["fecha_termino"])   
                #List Cargoinstituciones --------------------------------------------------
                if len(objCargo._list_cargos) == 0:
                    statement='SELECT IHC.Id_Institucion_Cargo,PHC.Id_Perfil_Cargo FROM Ley_Lobby.dbo.Institucion_Has_Cargo IHC left join Ley_Lobby.dbo.Perfil_Has_Cargo PHC on IHC.Id_Institucion_Cargo= PHC.Id_Institucion_Cargo where PHC.Id_Perfil =?'
                    crsr.execute(statement,[obj_persona_pasiva._id_perfil])
                    objCargo._list_cargos = crsr.fetchall()
                if objCargo.getValidarCargo() is False:
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Institucion_Has_Cargo_sp] ?,?,?,?,?,?,?;"
                    crsr.execute(storeProcedure,[objCargo._id_cargoInstitucion,cargo_pasivo["id_institucion"],objCargo._fecha_inicio,objCargo._fecha_termino,objCargo._cargo,objCargo._resolucion,objCargo._url_resolucion])
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Cargo_sp] ?,?;"
                    #obj_persona_pasiva._id_perfil_cargo_institucion  Internamente, en el Store Procedure, se crea el _id_perfil_cargo_institucion
                    crsr.execute(storeProcedure,[obj_persona_pasiva._id_perfil,objCargo._id_cargoInstitucion])  
                

            #Create url's infoLobby & LeyLobby     
            obj_audiencia.url_build_web(cod_institucion,obj_persona_pasiva._id_cargoInstitucion)                   
            
            
            #Detalle de Audiencia e Insert           
            url=Funciones.url_build_ley_lobby("Audiencia",obj_audiencia._id_audiencia) 
            detalle_audiencia,cantidad_total_de_peticiones_establecidos_en_la_API,time_start=Funciones.get_api(url,time_start,cantidad_total_de_peticiones_establecidos_en_la_API,header,False,2)           
            
            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_sp] ?,?,?,?,?,?,?,?,?;"
            crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_audiencia._fecha_inicio,obj_audiencia._fechaTermino,obj_audiencia._lugar,detalle_audiencia['forma'],obj_audiencia._observacion,obj_audiencia._ubicacion,obj_audiencia._url_info_lobby,obj_audiencia._url_ley_lobby])             
            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?;"
            crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_persona_pasiva._id_perfil_cargo_institucion,'Principal']) 

            #Insert Materias
            for materia in detalle_audiencia['materias']:
                obj_materia=Materia(materia['nombre'])
                if obj_materia._nombre is not None:
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_Has_Materia_sp] ?,?;"
                    crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_materia._nombre]) 
            
            #Insert Cargos Activos,
            for cargo_activo in detalle_audiencia['asistentes']:
                obj_persona_activa= Persona(cargo_activo['id_cargo_activo'],cargo_activo['nombres'],cargo_activo['apellidos'])                  
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?"                
                crsr.execute(storeProcedure,[obj_persona_activa._idsujeto,'Activo',obj_persona_activa._nombres,obj_persona_activa._apellidos])                
                obj_persona_activa._id_perfil=crsr.fetchval()                
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Cargo_sp] ?,?;"
                crsr.execute(storeProcedure,[obj_persona_activa._id_perfil,None])  
                storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?;"
                crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_persona_activa._id_perfil,None])

                #Insert Empresa/Entidad del Persona Activo
                if 'rut_representado' in cargo_activo['representa']:
                    representa=cargo_activo['representa']
                    obj_entidad=Entidad(representa['rut_representado'],representa['nombre'],representa['giro'],representa['domicilio'],representa['representante_legal'],representa['naturaleza'],representa['directorio'])  #(self,rut,nombre,giro,domicilio,representante,naturaleza,directorio):                                        
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Entidad_sp] ?,?,?,?,?,?,?,?;"                    
                    crsr.execute(storeProcedure,[obj_entidad._rut,obj_entidad._nombre,obj_entidad._giro,obj_entidad._representante,obj_entidad._directorio,representa['pais'],obj_entidad._domicilio,obj_entidad._naturaleza])
                    obj_entidad._id_Entidad= crsr.fetchval() 
                    if  obj_entidad._id_Entidad!=0:
                        storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Entidad_sp] ?,?;"
                        crsr.execute(storeProcedure,[obj_persona_activa._id_perfil,obj_entidad._id_Entidad])                          
            
                #insert_perfil_institucion('369-P',259, '2014-11-26',null,'Integrante de Comisión Evaluadora formada en el marco de la Ley N° 19886','','http://documentos.minvu.cl/min_vivienda/resoluciones_exentas/Documents/res%20ex%20electronica%20783.pdf');          
    except Exception as exception:
        print(exception) 
        traceback.print_exc()    
        print(f'id_audiencia:{obj_audiencia._id_audiencia}   N° pag: {num_page}')
        #crsr.rollback()
        break;      
    else:
        num_page += 1   
        if num_page>list_audiencias_api["last_page"]:  
            print('todo ok')      
            break       
        statement = 'UPDATE Ley_Lobby.dbo.Num_Page set PAGE_INCREMENTO=?  WHERE Area_Num_Page=?'
        crsr.execute(statement,[num_page,"AUDIENCIA"])
        
        
cnxn.closeConnection()    


#Validar largo del RUT en PYTHON