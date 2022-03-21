import time
import traceback
import os

# To work with the .env file
from dotenv import load_dotenv

import Funciones
import Controller
import SQL_Conection 
      
#---------------------------------------
def main():
    obj_hora_chile=Controller.HoraChile()
    if obj_hora_chile.calcular_si_hora_de_extraccion_es_valida():# is False:
        diferencia_entre_hora_inicio_extraccion_y_hora_chile=obj_hora_chile._hora_inicio_extraccion-obj_hora_chile.reconstruir_hora_de_chile()
        print(f'Precaucion⚠: el programa se debe ejecutar entre las: {obj_hora_chile._hora_inicio_extraccion.time()} hasta las {obj_hora_chile._hora_final_extraccion.time()}, Horario de Chile')     
        time.sleep(diferencia_entre_hora_inicio_extraccion_y_hora_chile.total_seconds()+1)

    id_audiencia=num_page=None

    try:
        load_dotenv()
        api_key = os.getenv('LEY_LOBBY_API_KEY')
        time_start=time.time()-2 #Se quita 2 segs para comenzar lo mas pronto posible con la primera request a la API
        header= {'Api-Key':api_key, 'content-type':'application/json'}

        url="https://www.leylobby.gob.cl/api/v1/"
        elements_url=["audiencias?page=","audiencias/", "cargos-pasivos/", "instituciones/"]
        
        with SQL_Conection.SQLServer() as crsr:
            #List instituciones
            crsr.execute('SELECT Id_Institucion, Id_Codigo FROM Ley_Lobby.dbo.Institucion')
            obj_institucion =Controller.Instituciones()
            obj_institucion._instituciones = crsr.fetchall()

            #Num_page INCREMENTO
            statement ='SELECT Page_Incremento,Page_Decremento,Page_Limit FROM Ley_Lobby.dbo.Num_Page where Area_Num_Page=?'
            list_num_page=crsr.execute(statement,["Audiencia"]).fetchall()[0]        
            obj_num_page = Controller.Num_Page(*list_num_page)

            num_page=obj_num_page._num_page
            print(num_page)
            cantidad_total_de_peticiones_establecidos_en_la_API=8000

            url_api_list_audiencias_page,url_api_audiencia,url_api_list_cargos_pasivos,url_api_list_instituciones = [url+element+'{}' for element in elements_url ]             
            
            while obj_hora_chile.calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion()==False:  
                list_audiencias_api,time_start,flag=Funciones.get_request_api(url_api_list_audiencias_page.format(obj_num_page._num_page),time_start,header )
                cantidad_total_de_peticiones_establecidos_en_la_API-=1
                #Loop audiencias por page        
                for audiencia in list_audiencias_api["data"]:
                    start_performance=time.time() 
                    id_audiencia=audiencia["id_audiencia"]

                    #Load Persona Pasiva
                    obj_persona_pasiva=Controller.Persona(audiencia['nombres'],audiencia['apellidos'])    #(self,nombres,apellidos): audiencia["id_sujeto_pasivo"]  
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
                        
                        obj_cargo=Controller.Cargo(cargo_pasivo["id_cargo_pasivo"],cargo_pasivo["cargo"])   
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
                    obj_audiencia=Controller.Audiencia(audiencia["id_audiencia"],audiencia['lugar'],audiencia['referencia'],audiencia['comuna'],audiencia['fecha_inicio'],audiencia['fecha_termino'])   #(self,id_audiencia,lugar,observacion,ubicacion,id_cargo):

                    #Detalle de Audiencia API                          
                    detalle_audiencia,time_start,flag=Funciones.get_request_api(url_api_audiencia.format(obj_audiencia._id_audiencia),time_start,header)                       
                    cantidad_total_de_peticiones_establecidos_en_la_API-=1

                    #Create url's infoLobby & LeyLobby     
                    obj_audiencia.url_build_web(obj_institucion._cod_institucion,obj_persona_pasiva._id_sujeto_pasivo_api)   

                    #Detalle de Audiencia INSERT   
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_sp] ?,?,?,?,?,?,?,?,?;"
                    crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_audiencia._fecha_inicio,obj_audiencia._fecha_termino,obj_audiencia._lugar,detalle_audiencia['forma'],obj_audiencia._observacion,obj_audiencia._ubicacion,obj_audiencia._url_info_lobby,obj_audiencia._url_ley_lobby])             
                    storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?,?,?;"
                    crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_persona_pasiva._id_perfil,None,None,'Principal']) #Existen reuniones donde hay mas de dos integrantes que son pasivos (empleados publicos). Estos, solo estan en visibles en la direccion url (Pagina WEB) pero no dentro de la respuesta de la API
                    
                    #Insert Materias
                    for materia in detalle_audiencia['materias']:
                        obj_materia=Controller.Materia(materia['nombre'])
                        if obj_materia._nombre is not None:
                            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_Has_Materia_sp] ?,?;"
                            crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_materia._nombre])                 
                    list_cargos_activos_temp=[]
                    #Insert Cargos Activos,
                    for cargo_activo in detalle_audiencia['asistentes']:
                        obj_persona_activa= Controller.Persona(cargo_activo['nombres'],cargo_activo['apellidos'])                  
                        storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?,?,?;"                
                        crsr.execute(storeProcedure,[obj_persona_activa._nombres,obj_persona_activa._apellidos,'Activo',None,None,None])                
                        obj_persona_activa._id_perfil=crsr.fetchval()
                        
                        id_entidad=nombre_representa=None
                        representa=cargo_activo['representa']
                        list_nombres_representa,list_nombres_persona=[],[]  

                        #Insert Empresa/Entidad del Persona Activo
                        if 'rut_representado' in cargo_activo['representa']:                              
                            obj_entidad=Controller.Entidad(representa['rut_representado'],representa['nombre'],representa['giro'],representa['domicilio'],representa['representante_legal'],representa['naturaleza'],representa['directorio'])  #(self,rut,nombre,giro,domicilio,representante,naturaleza,directorio):                                        
                            storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Entidad_sp] ?,?,?,?,?,?,?,?,?;"                    
                            crsr.execute(storeProcedure,[obj_entidad._rut,obj_entidad._rut_es_valido,obj_entidad._nombre,obj_entidad._giro,obj_entidad._representante_directorio,obj_entidad._directorio,representa['pais'],obj_entidad._domicilio,obj_entidad._naturaleza])
                            id_entidad=obj_entidad._id_Entidad= crsr.fetchval() 
                        else:
                            nombre=representa['nombre']
                            if Funciones.es_vacio_o_nulo(nombre)is False and any(char.isalpha() for char in nombre) and len(nombre)>=3:
                                nombre_representa=Funciones.limpiar_texto(nombre)          
                                nombre_representa=Funciones.limpiar_nombre(nombre_representa).title()
                                list_nombres_representa=nombre_representa.split()
                                list_nombres_persona=obj_persona_activa._nombres.split()+obj_persona_activa._apellidos.split()
                                if any(nombre for nombre in  list_nombres_persona if nombre in list_nombres_representa ):
                                    nombre_representa=None    
                        
                        storeProcedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?,?,?;"
                        crsr.execute(storeProcedure,[obj_audiencia._id_audiencia,obj_persona_activa._id_perfil,id_entidad,nombre_representa,None])

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