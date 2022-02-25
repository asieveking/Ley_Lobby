
import Funciones,SQL_Conection 
import datetime, time,traceback
from dateutil import tz


#---------------------------------------
    
def total_caracteres(texto):
    return texto[:5000]

#---------------------------------------
class Persona:
    _id_perfil=None  #string      
    _nombres=None
    _apellidos=None    
    
    def __init__(self,nombres,apellidos):        
        if Funciones.es_vacio_o_nulo(nombres)is False:            
            nombres=Funciones.quitar_tildes(nombres)
            nombres="".join( [caracter if caracter.isalpha() is True else " " for caracter in nombres ])
            self._nombres=" ".join(nombres.split()).title()            
        if Funciones.es_vacio_o_nulo(apellidos)is False:  
            apellidos=Funciones.quitar_tildes(apellidos)
            apellidos="".join( [caracter if caracter.isalpha() is True else " " for caracter in apellidos])
            self._apellidos=" ".join(apellidos.split()).title()

class Instituciones:
    _id_institucion=None
    _cod_institucion=None
    _instituciones=[]

    def get_codigo(self,id_institucion):
        self._id_institucion=id_institucion
        cod=[ id[1] for id in self._instituciones if id[0]==self._id_institucion ]       
        self._cod_institucion= cod[0] if len(cod)>0 else None
    

class Cargo:   
    _id_cargo_api=None 
    _nombre_cargo=None
    _resolucion=None
    _url_resolucion=None
    _fecha_inicio=None
    _fecha_termino=None
    _list_cargos_db = None
    _list_identificadores_vinculados=None

    def __init__(self,id_cargo_api,nombre_cargo): 
        self._list_identificadores_vinculados =[]
        self._list_cargos_db=[]
        self._id_cargo_api= id_cargo_api                  
        if Funciones.es_vacio_o_nulo(nombre_cargo)is False and any(char.isalpha() for char in nombre_cargo):
            nombre_cargo=Funciones.limpiar_texto(nombre_cargo)                    
            self._nombre_cargo=Funciones.limpiar_nombre(nombre_cargo).title()            
            self.licitacion_relacionada_dentro_de_texto(self._nombre_cargo)
   
    def rellenar_campos(self,resolucion,url_resolucion,fecha_inicio,fecha_termino):
        if Funciones.es_vacio_o_nulo(resolucion)is False and any(char.isalpha() for char in resolucion) :
            resolucion=Funciones.limpiar_texto(resolucion).capitalize()
            self.licitacion_relacionada_dentro_de_texto(resolucion.upper())
            #TODO quitar cantidad de caracteres
            self._resolucion=total_caracteres(resolucion)            
        if Funciones.es_vacio_o_nulo(url_resolucion)is False:
            self._url_resolucion="".join(url_resolucion.split())
        if Funciones.es_vacio_o_nulo(fecha_inicio)is False :
            # self._fecha_inicio=Funciones.stringafecha(fecha_inicio)
            self._fecha_inicio=fecha_inicio
        if Funciones.es_vacio_o_nulo(fecha_termino)is False:
            # self._fecha_termino=Funciones.stringafecha(fecha_termino)
            self._fecha_termino=fecha_termino
    
    def licitacion_relacionada_dentro_de_texto(self,texto):             
        while True:    
            identificador=Funciones.buscar_identificador_licitacion_en_texto(texto)        
            if identificador is not None:
                cod_identificador=identificador.split("-")[2][:2]
                if identificador not in self._list_identificadores_vinculados and cod_identificador not in ["PC","CL","IQ","IN"]:                
                    self._list_identificadores_vinculados.append(identificador)                   
                texto= texto.replace(identificador,"")
            else:
                break    
            
            
class Audiencia:
    _id_audiencia=None       
    _lugar=None
    _observacion=None
    _ubicacion=None    
    _url_info_lobby='https://www.infolobby.cl/Ficha/Audiencia/'
    _url_ley_lobby='https://www.leylobby.gob.cl/instituciones/'
    _fecha_inicio=None
    _fecha_termino=None
        
    def __init__(self,id_audiencia,lugar,observacion,ubicacion,fecha_inicio,fecha_termino):
        self._id_audiencia=id_audiencia 
        if Funciones.es_vacio_o_nulo(fecha_inicio)is False and fecha_inicio.isnumeric() is False:
            self._fecha_inicio=Funciones.stringafechatiempo(fecha_inicio)
        if Funciones.es_vacio_o_nulo(fecha_termino)is False and fecha_termino.isnumeric() is False:     
            self._fecha_termino=Funciones.stringafechatiempo(fecha_termino)
        if Funciones.es_vacio_o_nulo(ubicacion)is False and ubicacion.isnumeric() is False and any(char.isalpha() for char in ubicacion):   #Comuna
            self._ubicacion=Funciones.limpiar_texto(ubicacion).title()
        if Funciones.es_vacio_o_nulo(lugar)is False and lugar.isnumeric() is False and any(char.isalpha() for char in lugar) :
            self._lugar=Funciones.limpiar_texto(lugar).title()
        if Funciones.es_vacio_o_nulo(observacion)is False and observacion.isnumeric() is False and any(char.isalpha() for char in observacion):
            observacion=Funciones.limpiar_texto(observacion).capitalize()                      
            self._observacion=total_caracteres(observacion)
            

    def url_build_web(self, codigo_institucion, id_sujeto_pasivo):          
        self._url_info_lobby= f'{self._url_info_lobby}{codigo_institucion}{self._id_audiencia}1'
        #anio=self._fecha_inicio.year#.strftime("%Y")# .split("-")[0]   
        self._url_ley_lobby= f'{self._url_ley_lobby}{codigo_institucion}/audiencias/{self._fecha_inicio.year}/{id_sujeto_pasivo}/{self._id_audiencia}' 
        #https://www.infolobby.cl/Ficha/Audiencia/AE006312971
        #https://www.leylobby.gob.cl/instituciones/AE006/audiencias/2015/1723/31297  

class Entidad:
    _rut=None
    _rut_es_valido=None
    _nombre=None    
    _giro=None
    _domicilio=None
    _representante=None
    _naturaleza=None
    _directorio=None    

    def __init__(self,rut,nombre,giro,domicilio,representante,naturaleza,directorio):        
        if Funciones.es_vacio_o_nulo(rut)is False and len(rut)>=5: 
            rut=rut.replace(".","").replace(" ","")
            if len(rut)>=9 and len(rut)<=10  and rut[-2:-1]=='-' and rut[:-2].isnumeric() is True:                
                self._rut=Funciones.dar_formato_al_rut(rut) #Formato para el rut chileno  
                self._rut_es_valido=1            
            else:
                self._rut=rut.replace("-","") #identenficador para entranjeros ejemplo: "Hemasoft Software SL" id B82874173 orden de compra 956-1388-SE18
                self._rut_es_valido=0
        if Funciones.es_vacio_o_nulo(nombre)is False and any(char.isalpha() for char in nombre) and len(nombre)>=3:
            nombre=Funciones.limpiar_texto(nombre).upper()            
            nombre=Funciones.limpiar_nombre(nombre).replace(" SOCIEDAD ANONIMA","").replace("LTDA","").replace(" LTD","")
            self._nombre=" ".join([palabra for  palabra in nombre.split() if palabra not in ["SA","LIMITADA"]])         
            
        if Funciones.es_vacio_o_nulo(giro)is False and giro.isnumeric() is False and any(char.isalpha() for char in giro) :
            self._giro=Funciones.limpiar_texto(giro).title()
        if Funciones.es_vacio_o_nulo(representante)is False and any(char.isalpha() for char in representante) :
            representante=Funciones.limpiar_texto(representante)
            self._representante=Funciones.quitar_puntos(representante).title()
        if Funciones.es_vacio_o_nulo(naturaleza)is False and any(char.isalpha() for char in naturaleza):
            self._naturaleza=Funciones.limpiar_texto(naturaleza).title()
        if Funciones.es_vacio_o_nulo(domicilio)is False and any(char.isalpha() for char in domicilio):
            self._domicilio=Funciones.limpiar_texto(domicilio).title()
        if Funciones.es_vacio_o_nulo(directorio)is False and any(char.isalpha() for char in directorio) :
            directorio=Funciones.limpiar_texto(directorio)
            self._directorio=Funciones.quitar_puntos(directorio).title()
                
class Materia:
    _nombre=None
    
    def __init__(self,nombre):
        if  Funciones.es_vacio_o_nulo(nombre)is False:  
            self._nombre=Funciones.limpiar_texto(nombre)

class HoraChile():        
    _hora_inicio_extraccion=None
    _hora_final_extraccion=None        
    _utc_chile=None

    def __init__(self):
        self._utc_chile= tz.gettz('America/Santiago')#https://nodatime.org/TimeZones
        datetime_chile=self.reconstruir_hora_de_chile()      
        
        #hora,minuto,segundo=self._datetime_chile.hour,self._datetime_chile.minute, self._datetime_chile.second
        self._hora_inicio_extraccion = datetime_chile.replace(hour=18,minute=00,second=0,microsecond=0)+datetime.timedelta(days=-1 if datetime_chile.time() <= datetime.time(8,0,0,0) and datetime_chile.time() >= datetime.time.min else 0)# Hora Oficial Entre 22:00 a 07:00 hrs. Restriccion horaria para extraer desde la API
        self._hora_final_extraccion = datetime_chile.replace(hour=8,minute=00,second=0,microsecond=0)+datetime.timedelta(days=1 if datetime_chile.time() >= datetime.time(8,0,0,1) and datetime_chile.time() <= datetime.time.max else 0)#hora Oficial       
        
    def calcular_si_hora_de_extraccion_es_valida(self):                
        return datetime.datetime.now(self._utc_chile).replace(tzinfo=None) < self._hora_inicio_extraccion  

    def calcular_si_fecha_actual_es_menor_a_la_hora_final_de_extraccion(self,fecha_extraccion):
        return  datetime.datetime.now(self._utc_chile).replace(tzinfo=None) < self._hora_final_extraccion  and fecha_extraccion.date() < datetime.datetime.now(self._utc_chile).date()

    def reconstruir_hora_de_chile(self):
        return datetime.datetime.now(self._utc_chile).replace(tzinfo=None)   
    
    def calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion(self):
        return datetime.datetime.now(self._utc_chile).replace(tzinfo=None) > self._hora_final_extraccion

class Num_Page:
    _num_page_incremento:int
    _num_page_decremento:int
    _num_page_limit:int
    _num_page:int

    def __init__(self,num_page_incremento,num_page_decremento,num_page_limit):
        self._num_page=self._num_page_incremento=num_page_incremento-2
        self._num_page_decremento=num_page_decremento if num_page_limit ==num_page_decremento else  num_page_decremento+3
        self._num_page_limit=num_page_limit
        
        
#---------------------------------------
def main():
    obj_hora_chile=HoraChile()
    if obj_hora_chile.calcular_si_hora_de_extraccion_es_valida():# is False:
        diferencia_entre_hora_inicio_extraccion_y_hora_chile=obj_hora_chile._hora_inicio_extraccion-obj_hora_chile.reconstruir_hora_de_chile()
        print(f'Precaucion⚠: el programa se debe ejecutar entre las: {obj_hora_chile._hora_inicio_extraccion.time()} hasta las {obj_hora_chile._hora_final_extraccion.time()}, Horario de Chile')     
        time.sleep(diferencia_entre_hora_inicio_extraccion_y_hora_chile.total_seconds()+1)

    id_audiencia=num_page=None

    try:
        time_start=time.time()
        header= {'Api-Key':'$2y$10$KjpEayK8CvOywKuM2zW3x.BF1oZ1uyv8MpOHtywhDa8', 'content-type':'application/json'}

        with SQL_Conection.SQLServer() as crsr:
            #List instituciones
            crsr.execute('SELECT Id_Institucion, Id_Codigo FROM Ley_Lobby.dbo.Institucion')
            obj_institucion =Instituciones()
            obj_institucion._instituciones = crsr.fetchall()

            #Num_page INCREMENTO
            statement ='SELECT Page_Incremento,Page_Decremento,Page_Limit FROM Ley_Lobby.dbo.Num_Page where Area_Num_Page=?'
            list_num_page=crsr.execute(statement,["Audiencia"]).fetchall()[0]        
            obj_num_page = Num_Page(*list_num_page)

            num_page=obj_num_page._num_page
            print(num_page)
            cantidad_total_de_peticiones_establecidos_en_la_API=8000
            
            url_api_list_page=Funciones.url_build_ley_lobby("Audiencias_Page") 
            url_api_list_cargos_pasivos=Funciones.url_build_ley_lobby("Cargos_Pasivos")
            url_api_list_instituciones=Funciones.url_build_ley_lobby("Instituciones") 
            url_api_audiencia=Funciones.url_build_ley_lobby("Audiencias")
            
            while obj_hora_chile.calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion()==False:  
                list_audiencias_api,time_start,flag=Funciones.get_request_api(url_api_list_page.format(obj_num_page._num_page),time_start,header )
                cantidad_total_de_peticiones_establecidos_en_la_API-=1
                #Loop audiencias por page        
                for audiencia in list_audiencias_api["data"]:
                    start_performance=time.time() 
                    id_audiencia=audiencia["id_audiencia"]

                    #Load Persona Pasiva
                    obj_persona_pasiva=Persona(audiencia['nombres'],audiencia['apellidos'])    #(self,nombres,apellidos): audiencia["id_sujeto_pasivo"]  
                    obj_persona_pasiva._id_sujeto_pasivo_api=audiencia["id_sujeto_pasivo"]  
                    
                    #List Cargo_instituciones por id de sujeto Pasivo                                   
                    statement='SELECT P.Id_Perfil,P.Id_Institucion,P.Id_Cargo_API,DP.Fecha_Inicio_Cargo,DP.Fecha_Termino_Cargo,DP.Id_Resolucion,DP.Id_Url_Resolucion FROM [Ley_Lobby].[dbo].PERFIL P LEFT JOIN [Ley_Lobby].[dbo].DETALLE_PERFIL DP ON P.Id_Perfil=DP.id_Detalle_Perfil  WHERE Id_Sujeto_Pasivo_API=?'
                    crsr.execute(statement,(obj_persona_pasiva._id_sujeto_pasivo_api))
                    list_cargos_pasivos_db=[]
                    list_cargos_pasivos_db = crsr.fetchall()

                    #Get Cargos Pasivos API 
                    list_cargos_pasivos_api,time_start,flag=Funciones.get_request_api(url_api_list_cargos_pasivos.format(obj_persona_pasiva._id_sujeto_pasivo_api),time_start,header)                
                    cantidad_total_de_peticiones_establecidos_en_la_API-=1
                    cod_institucion=None

                    #Search and Insert todos los cargos de Persona Pasiva
                    for cargo_pasivo in list_cargos_pasivos_api: 

                        if any(True for cargo_pasivo_db in list_cargos_pasivos_db  if cargo_pasivo["id_institucion"]==cargo_pasivo_db[1] 
                        and cargo_pasivo["id_cargo_pasivo"]==cargo_pasivo_db[2] and cargo_pasivo["fecha_inicio"]==cargo_pasivo_db[3]
                        and cargo_pasivo["fecha_termino"]==cargo_pasivo_db[4] and (Funciones.es_vacio_o_nulo(cargo_pasivo["resolucion"]) is False and cargo_pasivo_db[5] is not None
                        or Funciones.es_vacio_o_nulo(cargo_pasivo["resolucion"]) is True and cargo_pasivo_db[5] is None )
                        and (Funciones.es_vacio_o_nulo(cargo_pasivo["resolucion_url"]) is False and cargo_pasivo_db[6] is not None 
                        or Funciones.es_vacio_o_nulo(cargo_pasivo["resolucion_url"]) is True and cargo_pasivo_db[6] is None ) ):                        
                            continue
                        
                        obj_cargo=Cargo(cargo_pasivo["id_cargo_pasivo"],cargo_pasivo["cargo"])   
                        obj_cargo.rellenar_campos(cargo_pasivo["resolucion"],cargo_pasivo["resolucion_url"],cargo_pasivo["fecha_inicio"],cargo_pasivo["fecha_termino"])                
                        
                        #Load Institucion            
                        obj_institucion.get_codigo(cargo_pasivo["id_institucion"] )

                        #Si institucion no existe entonces Insert Institucion
                        if obj_institucion._cod_institucion  is None:                                                 
                            institucion,time_start,flag=Funciones.get_request_api(url_api_list_instituciones.format(obj_institucion._id_institucion),time_start,header)
                            cantidad_total_de_peticiones_establecidos_en_la_API-=1
                            obj_institucion._cod_institucion = institucion["codigo"]
                            #Load a lista instituciones
                            obj_institucion._instituciones.append([obj_institucion._id_institucion,obj_institucion._cod_institucion])
                            #Insert data
                            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Institucion_sp] ?,?,?;"
                            params= (obj_institucion._id_institucion,obj_institucion._cod_institucion,institucion["nombre"].strip())   
                            crsr.execute(storeProcedure,params)    

                        #Insert Persona Pasiva            
                        storeProcedure=" EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?,?,?,?;"
                        params= (obj_persona_pasiva._nombres,obj_persona_pasiva._apellidos,'Pasivo',obj_persona_pasiva._id_sujeto_pasivo_api,obj_cargo._nombre_cargo,obj_institucion._id_institucion,obj_cargo._id_cargo_api)
                        crsr.execute(storeProcedure,params)
                        id_perfil_temp=crsr.fetchval() 
                        
                        #Cuando los id_cargos y las id_Instituciones sean iguales entonces se copiaran los valores entre las variables
                        if obj_cargo._id_cargo_api==audiencia['id_cargo'] and obj_institucion._id_institucion==audiencia['id_institucion']: 
                            obj_persona_pasiva._id_perfil=id_perfil_temp                      
                            cod_institucion=obj_institucion._cod_institucion

                        #Insert Detalle Persona Pasiva   
                        storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Detalle_Perfil_sp] ?,?,?,?,?;"
                        crsr.execute(storeProcedure,[id_perfil_temp,obj_cargo._fecha_inicio,obj_cargo._fecha_termino,obj_cargo._resolucion,obj_cargo._url_resolucion])
                        
                        #Insertar identificadores vinculadas Id_OC and Id_Licitacion
                        if len(obj_cargo._list_identificadores_vinculados)>0:   
                            for identificador in obj_cargo._list_identificadores_vinculados:                  
                                crsr.execute("EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Identificador_sp] ?,?;",[id_perfil_temp,identificador])

                    #En el caso de que el registro no este dentro de la lista "list_cargos_pasivos_api"... Entonces, buscarlo dentro de la "list_cargos_pasivos_db"
                    if obj_persona_pasiva._id_perfil is None:
                        if cod_institucion is None:
                            obj_institucion.get_codigo(audiencia["id_institucion"] )
                        else:
                            obj_institucion._id_institucion,obj_institucion._cod_institucion=audiencia["id_institucion"],cod_institucion
                        
                        obj_persona_pasiva._id_perfil=next(cargo[0] for cargo in list_cargos_pasivos_db if obj_institucion._id_institucion==cargo[1] and cargo[2]==audiencia['id_cargo'])
                    
                    #Load Audiencia
                    obj_audiencia=Audiencia(audiencia["id_audiencia"],audiencia['lugar'],audiencia['referencia'],audiencia['comuna'],audiencia['fecha_inicio'],audiencia['fecha_termino'])   #(self,id_audiencia,lugar,observacion,ubicacion,id_cargo):

                    #Detalle de Audiencia API                          
                    detalle_audiencia,time_start,flag=Funciones.get_request_api(url_api_audiencia.format(obj_audiencia._id_audiencia),time_start,header)                       
                    cantidad_total_de_peticiones_establecidos_en_la_API-=1

                    #Create url's infoLobby & LeyLobby     
                    obj_audiencia.url_build_web(obj_institucion._cod_institucion,obj_persona_pasiva._id_sujeto_pasivo_api)   

                    #Detalle de Audiencia INSERT   
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_sp] ?,?,?,?,?,?,?,?,?;"
                    crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_audiencia._fecha_inicio,obj_audiencia._fecha_termino,obj_audiencia._lugar,detalle_audiencia['forma'],obj_audiencia._observacion,obj_audiencia._ubicacion,obj_audiencia._url_info_lobby,obj_audiencia._url_ley_lobby])             
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?,?;"
                    crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_persona_pasiva._id_perfil,None,'Principal']) #Existen reuniones donde hay mas de dos integrantes que son pasivos (empleados publicos). Estos, solo estan en visibles en la direccion url (Pagina WEB) pero no dentro de la respuesta de la API
                    
                    #Insert Materias
                    for materia in detalle_audiencia['materias']:
                        obj_materia=Materia(materia['nombre'])
                        if obj_materia._nombre is not None:
                            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_Has_Materia_sp] ?,?;"
                            crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_materia._nombre])                 
                    list_cargos_activos_temp=[]
                    #Insert Cargos Activos,
                    for cargo_activo in detalle_audiencia['asistentes']:
                        obj_persona_activa= Persona(cargo_activo['nombres'],cargo_activo['apellidos'])                  
                        storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?,?,?;"                
                        crsr.execute(storeProcedure,[obj_persona_activa._nombres,obj_persona_activa._apellidos,'Activo',None,None,None])                
                        obj_persona_activa._id_perfil=crsr.fetchval()
                        
                        id_entidad=None
                        #Insert Empresa/Entidad del Persona Activo
                        if 'rut_representado' in cargo_activo['representa']:
                            representa=cargo_activo['representa']
                            obj_entidad=Entidad(representa['rut_representado'],representa['nombre'],representa['giro'],representa['domicilio'],representa['representante_legal'],representa['naturaleza'],representa['directorio'])  #(self,rut,nombre,giro,domicilio,representante,naturaleza,directorio):                                        
                            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Entidad_sp] ?,?,?,?,?,?,?,?,?;"                    
                            crsr.execute(storeProcedure,[obj_entidad._rut,obj_entidad._rut_es_valido,obj_entidad._nombre,obj_entidad._giro,obj_entidad._representante,obj_entidad._directorio,representa['pais'],obj_entidad._domicilio,obj_entidad._naturaleza])
                            id_entidad=obj_entidad._id_Entidad= crsr.fetchval() 
                        
                        storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?,?;"
                        crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_persona_activa._id_perfil,id_entidad,None])                        

                    print(f'id_audiencia: {id_audiencia} - cantidad de cargos activos: {len( detalle_audiencia["asistentes"] )} - cantidad de tiempo: {time.time()-start_performance}')          
                    
                    if obj_hora_chile.calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion()==True:
                        break
                
                if obj_num_page._num_page_incremento<list_audiencias_api["last_page"]: 
                    obj_num_page._num_page_incremento+=1 
                    num_page= obj_num_page._num_page = obj_num_page._num_page_incremento 
                    statement = 'UPDATE Ley_Lobby.dbo.Num_Page set PAGE_INCREMENTO=?  WHERE Area_Num_Page=?'
                    crsr.execute(statement,[obj_num_page._num_page,"AUDIENCIA"])  
                elif obj_num_page._num_page_decremento> obj_num_page._num_page_limit:
                    obj_num_page._num_page_decremento -=1
                    num_page = obj_num_page._num_page= obj_num_page._num_page_decremento 
                    statement = 'UPDATE Ley_Lobby.dbo.Num_Page set PAGE_DECREMENTO=?  WHERE Area_Num_Page=?'
                    crsr.execute(statement,[obj_num_page._num_page,"AUDIENCIA"]) 
                elif obj_num_page._num_page_incremento>=list_audiencias_api["last_page"] and obj_num_page._num_page_decremento<= obj_num_page._num_page_limit:
                    break
                print(num_page)           
                    
    except Exception as exception:
        print(exception) 
        traceback.print_exc()    
        print(f'id_audiencia:{id_audiencia}   N° pag: {num_page}')            
          
if __name__ == "__main__":
    main()

            
            
            



#Validar largo del RUT en PYTHON