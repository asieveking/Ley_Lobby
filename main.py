import time
import traceback
import os

# To work with the .env file
from dotenv import load_dotenv

from sample import functions, controller, sql_connection
      
#---------------------------------------
def main():
    obj_hora_chile=controller.HoraChile()
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
        
        with sql_connection.SQLServer() as crsr:
            #List instituciones
            crsr.execute('SELECT Id_Institucion, Id_Codigo FROM Ley_Lobby.dbo.Institucion')
            obj_institucion =controller.Institucion()
            obj_institucion.list_instituciones = crsr.fetchall()

            #Num_page INCREMENTO
            statement ='SELECT Page_Incremento,Page_Decremento,Page_Limit FROM Ley_Lobby.dbo.Num_Page where Area_Num_Page=?'
            list_num_page=crsr.execute(statement,["Audiencia"]).fetchall()[0]        
            obj_num_page = controller.Num_Page(*list_num_page)

            num_page=obj_num_page.num_page
            print(num_page)
            cantidad_total_de_peticiones_establecidos_en_la_API=8000

            url_api_list_audiencias_page,url_api_audiencia,url_api_list_cargos_pasivos,url_api_list_instituciones = [url+element+'{}' for element in elements_url ]             
            
            while obj_hora_chile.calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion()==False:  
                list_audiencias_api,time_start,flag=functions.get_request_api(url_api_list_audiencias_page.format(obj_num_page.num_page),time_start,header )
                cantidad_total_de_peticiones_establecidos_en_la_API-=1
                #Loop audiencias por page        
                for audiencia in list_audiencias_api["data"]:
                    start_performance=time.time() 
                    id_audiencia=audiencia["id_audiencia"]

                    #Load Persona Pasiva
                    obj_persona_pasiva=controller.Persona(audiencia['nombres'],audiencia['apellidos'])    #(self,nombres,apellidos): audiencia["id_sujeto_pasivo"]  
                    obj_persona_pasiva._id_sujeto_pasivo_api=audiencia["id_sujeto_pasivo"]  
                    
                    #List Cargo_instituciones por id de sujeto Pasivo                                   
                    statement='SELECT P.Id_Perfil,P.Id_Institucion,P.Id_Cargo_API,DP.Fecha_Inicio_Cargo,DP.Fecha_Termino_Cargo,DP.Id_Resolucion,DP.Id_Url_Resolucion FROM [Ley_Lobby].[dbo].PERFIL P LEFT JOIN [Ley_Lobby].[dbo].DETALLE_PERFIL DP ON P.Id_Perfil=DP.id_Detalle_Perfil  WHERE Id_Sujeto_Pasivo_API=?'
                    crsr.execute(statement,(obj_persona_pasiva._id_sujeto_pasivo_api))
                    list_cargos_pasivos_db=[]
                    list_cargos_pasivos_db = crsr.fetchall()

                    #Get Cargos Pasivos API 
                    list_cargos_pasivos_api,time_start,flag=functions.get_request_api(url_api_list_cargos_pasivos.format(obj_persona_pasiva._id_sujeto_pasivo_api),time_start,header)                
                    cantidad_total_de_peticiones_establecidos_en_la_API-=1
                    cod_institucion=None

                    #Search and Insert todos los cargos de Persona Pasiva
                    for cargo_pasivo in list_cargos_pasivos_api: 

                        if any(True for cargo_pasivo_db in list_cargos_pasivos_db  if cargo_pasivo["id_institucion"]==cargo_pasivo_db[1] 
                        and cargo_pasivo["id_cargo_pasivo"]==cargo_pasivo_db[2] and cargo_pasivo["fecha_inicio"]==cargo_pasivo_db[3]
                        and cargo_pasivo["fecha_termino"]==cargo_pasivo_db[4] and (functions.es_vacio_o_nulo(cargo_pasivo["resolucion"]) is False and cargo_pasivo_db[5] is not None
                        or functions.es_vacio_o_nulo(cargo_pasivo["resolucion"]) is True and cargo_pasivo_db[5] is None )
                        and (functions.es_vacio_o_nulo(cargo_pasivo["resolucion_url"]) is False and cargo_pasivo_db[6] is not None 
                        or functions.es_vacio_o_nulo(cargo_pasivo["resolucion_url"]) is True and cargo_pasivo_db[6] is None ) ):                        
                            continue
                        
                        obj_cargo=controller.Cargo(cargo_pasivo["id_cargo_pasivo"],cargo_pasivo["cargo"])   
                        obj_cargo.rellenar_campos(cargo_pasivo["resolucion"],cargo_pasivo["resolucion_url"],cargo_pasivo["fecha_inicio"],cargo_pasivo["fecha_termino"])                
                        
                        #Load Institucion            
                        obj_institucion.get_codigo(cargo_pasivo["id_institucion"] )

                        #Si institucion no existe entonces Insert Institucion
                        if obj_institucion.codigo_institucion  is None:                                                 
                            institucion,time_start,flag=functions.get_request_api(url_api_list_instituciones.format(obj_institucion.id_institucion),time_start,header)
                            cantidad_total_de_peticiones_establecidos_en_la_API-=1
                            obj_institucion.codigo_institucion = institucion["codigo"]
                            #Load a lista instituciones
                            obj_institucion.list_instituciones.append([obj_institucion.id_institucion,obj_institucion.codigo_institucion])
                            #Insert data
                            store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Institucion_sp] ?,?,?;"
                            params= (obj_institucion.id_institucion,obj_institucion.codigo_institucion,institucion["nombre"].strip())   
                            crsr.execute(store_procedure,params)    

                        #Insert Persona Pasiva            
                        store_procedure=" EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?,?,?,?;"
                        params= (obj_persona_pasiva.nombres,obj_persona_pasiva.apellidos,'Pasivo',obj_persona_pasiva._id_sujeto_pasivo_api,obj_cargo.nombre_cargo,obj_institucion.id_institucion,obj_cargo._id_cargo_api)
                        crsr.execute(store_procedure,params)
                        id_perfil_temp=crsr.fetchval() 
                        
                        #Cuando los id_cargos y las id_Instituciones sean iguales entonces se copiaran los valores entre las variables
                        if obj_cargo._id_cargo_api==audiencia['id_cargo'] and obj_institucion.id_institucion==audiencia['id_institucion']: 
                            obj_persona_pasiva.id_perfil=id_perfil_temp                      
                            cod_institucion=obj_institucion.codigo_institucion

                        #Insert Detalle Persona Pasiva   
                        store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Detalle_Perfil_sp] ?,?,?,?,?;"
                        crsr.execute(store_procedure,[id_perfil_temp,obj_cargo.fecha_inicio,obj_cargo.fecha_termino,obj_cargo.resolucion,obj_cargo.url_resolucion])
                        
                        #Insertar identificadores vinculadas Id_OC and Id_Licitacion
                        if len(obj_cargo.list_identificadores_vinculados)>0:   
                            for identificador in obj_cargo.list_identificadores_vinculados:                  
                                crsr.execute("EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Identificador_sp] ?,?;",[id_perfil_temp,identificador])

                    #En el caso de que el registro no este dentro de la lista "list_cargos_pasivos_api"... Entonces, buscarlo dentro de la "list_cargos_pasivos_db"
                    if obj_persona_pasiva.id_perfil is None:
                        if cod_institucion is None:
                            obj_institucion.get_codigo(audiencia["id_institucion"] )
                        else:
                            obj_institucion.id_institucion,obj_institucion.codigo_institucion=audiencia["id_institucion"],cod_institucion
                        
                        obj_persona_pasiva.id_perfil=next(cargo[0] for cargo in list_cargos_pasivos_db if obj_institucion.id_institucion==cargo[1] and cargo[2]==audiencia['id_cargo'])
                    
                    #Load Audiencia
                    obj_audiencia=controller.Audiencia(audiencia["id_audiencia"],audiencia['lugar'],audiencia['referencia'],audiencia['comuna'],audiencia['fecha_inicio'],audiencia['fecha_termino'])   #(self,id_audiencia,lugar,observacion,ubicacion,id_cargo):

                    #Detalle de Audiencia API                          
                    detalle_audiencia,time_start,flag=functions.get_request_api(url_api_audiencia.format(obj_audiencia.id_audiencia),time_start,header)                       
                    cantidad_total_de_peticiones_establecidos_en_la_API-=1

                    #Create url's infoLobby & LeyLobby     
                    obj_audiencia.url_build_web(obj_institucion.codigo_institucion,obj_persona_pasiva._id_sujeto_pasivo_api)   

                    #Detalle de Audiencia INSERT   
                    store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_sp] ?,?,?,?,?,?,?,?,?;"
                    crsr.execute(store_procedure,[obj_audiencia.id_audiencia,obj_audiencia.fecha_inicio,obj_audiencia.fecha_termino,obj_audiencia.lugar,detalle_audiencia['forma'],obj_audiencia.observacion,obj_audiencia.ubicacion,obj_audiencia.url_info_lobby,obj_audiencia.url_ley_lobby])             
                    store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?,?,?;"
                    crsr.execute(store_procedure,[obj_audiencia.id_audiencia,obj_persona_pasiva.id_perfil,None,None,'Principal']) #Existen reuniones donde hay mas de dos integrantes que son pasivos (empleados publicos). Estos, solo estan en visibles en la direccion url (Pagina WEB) pero no dentro de la respuesta de la API
                    
                    #Insert Materias
                    for materia in detalle_audiencia['materias']:
                        obj_materia=controller.Materia(materia['nombre'])
                        if obj_materia.nombre is not None:
                            store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Audiencia_Has_Materia_sp] ?,?;"
                            crsr.execute(store_procedure,[obj_audiencia.id_audiencia,obj_materia.nombre])                 
                    list_cargos_activos_temp=[]
                    #Insert Cargos Activos,
                    for cargo_activo in detalle_audiencia['asistentes']:
                        obj_persona_activa= controller.Persona(cargo_activo['nombres'],cargo_activo['apellidos'])                  
                        store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_sp] ?,?,?,?,?,?;"                
                        crsr.execute(store_procedure,[obj_persona_activa.nombres,obj_persona_activa.apellidos,'Activo',None,None,None])                
                        obj_persona_activa.id_perfil=crsr.fetchval()
                        
                        id_entidad=nombre_representa=None
                        representa=cargo_activo['representa']
                        list_nombres_representa,list_nombres_persona=[],[]  

                        #Insert Empresa/Entidad del Persona Activo
                        if 'rut_representado' in cargo_activo['representa']:                              
                            obj_entidad=controller.Entidad(representa['rut_representado'],representa['nombre'],representa['giro'],representa['domicilio'],representa['representante_legal'],representa['naturaleza'],representa['directorio'])  #(self,rut,nombre,giro,domicilio,representante,naturaleza,directorio):                                        
                            store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Entidad_sp] ?,?,?,?,?,?,?,?,?;"                    
                            crsr.execute(store_procedure,[obj_entidad.rut,obj_entidad.rut_es_valido,obj_entidad.nombre,obj_entidad.giro,obj_entidad.representante_directorio,obj_entidad.directorio,representa['pais'],obj_entidad.domicilio,obj_entidad.naturaleza])
                            id_entidad=obj_entidad._id_Entidad= crsr.fetchval() 
                        else:
                            nombre=representa['nombre']
                            if functions.es_vacio_o_nulo(nombre)is False and any(char.isalpha() for char in nombre) and len(nombre)>=3:
                                nombre_representa=functions.limpiar_texto(nombre)          
                                nombre_representa=functions.limpiar_nombre(nombre_representa).title()
                                list_nombres_representa=nombre_representa.split()
                                list_nombres_persona=obj_persona_activa.nombres.split()+obj_persona_activa.apellidos.split()
                                if any(nombre for nombre in  list_nombres_persona if nombre in list_nombres_representa ):
                                    nombre_representa=None    
                        
                        store_procedure="EXEC [Ley_Lobby].[dbo].[ins_Perfil_Has_Audiencia_sp] ?,?,?,?,?;"
                        crsr.execute(store_procedure,[obj_audiencia.id_audiencia,obj_persona_activa.id_perfil,id_entidad,nombre_representa,None])

                    print(f'id_audiencia: {id_audiencia} - cantidad de cargos activos: {len( detalle_audiencia["asistentes"] )} - cantidad de tiempo: {time.time()-start_performance}')          
                    
                    if obj_hora_chile.calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion()==True:
                        break
                
                if obj_num_page.num_page_incremento<list_audiencias_api["last_page"]: 
                    obj_num_page.num_page_incremento+=1 
                    num_page= obj_num_page.num_page = obj_num_page.num_page_incremento 
                    statement = 'UPDATE Ley_Lobby.dbo.Num_Page set PAGE_INCREMENTO=?  WHERE Area_Num_Page=?'
                    crsr.execute(statement,[obj_num_page.num_page,"AUDIENCIA"])  
                elif obj_num_page.num_page_decremento> obj_num_page.num_page_limit:
                    obj_num_page.num_page_decremento -=1
                    num_page = obj_num_page.num_page= obj_num_page.num_page_decremento 
                    statement = 'UPDATE Ley_Lobby.dbo.Num_Page set PAGE_DECREMENTO=?  WHERE Area_Num_Page=?'
                    crsr.execute(statement,[obj_num_page.num_page,"AUDIENCIA"]) 
                elif obj_num_page.num_page_incremento>=list_audiencias_api["last_page"] and obj_num_page.num_page_decremento<= obj_num_page.num_page_limit:
                    break
                print(num_page)           
                    
    except Exception as exception:
        print(exception) 
        traceback.print_exc()    
        print(f'id_audiencia:{id_audiencia}   N° pag: {num_page}')            
          
if __name__ == "__main__":
    main()

            
            
            



#Validar largo del RUT en PYTHON