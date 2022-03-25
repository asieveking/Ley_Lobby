import datetime
from dateutil import tz

import Funciones

class Persona:
    id_perfil:int=None  #string      
    nombres:str=None
    apellidos:str=None    
    
    def __init__(self,nombres:str,apellidos:str):        
        if Funciones.es_vacio_o_nulo(nombres)is False:            
            nombres=Funciones.transcripcion_simbolos_vocales(nombres)
            nombres="".join( [caracter if caracter.isalpha() is True else " " for caracter in nombres ])
            self.nombres=" ".join(nombres.split()).title()            
        if Funciones.es_vacio_o_nulo(apellidos)is False:  
            apellidos=Funciones.transcripcion_simbolos_vocales(apellidos)
            apellidos="".join( [caracter if caracter.isalpha() is True else " " for caracter in apellidos])
            self.apellidos=" ".join(apellidos.split()).title()

class Institucion:
    id_institucion:int=None
    codigo_institucion:str=None
    list_instituciones:list=[]

    
    def get_codigo(self,id_institucion:int):
        self.id_institucion=id_institucion
        self.codigo_institucion=next((id[1] for id in self.list_instituciones if id[0]==self.id_institucion),None)       
        
    

class Cargo:   
    id_cargo_api:int=None 
    nombre_cargo:str=None
    resolucion:str=None
    url_resolucion:str=None
    fecha_inicio:datetime=None
    fecha_termino:datetime=None    
    list_identificadores_vinculados:list=None

    def __init__(self,id_cargo_api:int,nombre_cargo:str): 
        self.list_identificadores_vinculados =[]        
        self.id_cargo_api= id_cargo_api                  
        if Funciones.es_vacio_o_nulo(nombre_cargo)is False and any(char.isalpha() for char in nombre_cargo):
            nombre_cargo=Funciones.limpiar_texto(nombre_cargo)                    
            self.nombre_cargo=Funciones.limpiar_nombre(nombre_cargo).title()            
            self.licitacion_relacionada_dentro_de_texto(self.nombre_cargo)
    
    def rellenar_campos(self,resolucion:str,url_resolucion:str,fecha_inicio:str,fecha_termino:str):
        if Funciones.es_vacio_o_nulo(resolucion)is False and any(char.isalpha() for char in resolucion) :
            resolucion=Funciones.limpiar_texto(resolucion).capitalize()
            self.licitacion_relacionada_dentro_de_texto(resolucion)            
            self.resolucion=resolucion[:5000]            
        if Funciones.es_vacio_o_nulo(url_resolucion)is False:
            self.url_resolucion="".join(url_resolucion.split())
        if Funciones.es_vacio_o_nulo(fecha_inicio)is False :            
            self.fecha_inicio=fecha_inicio
        if Funciones.es_vacio_o_nulo(fecha_termino)is False:            
            self.fecha_termino=fecha_termino

    
    def licitacion_relacionada_dentro_de_texto(self,texto:str):             
        while True:    
            identificador=Funciones.buscar_identificador_licitacion_en_texto(texto)        
            if identificador is not None:
                cod_identificador=identificador.split("-")[2][:2]
                if identificador not in self.list_identificadores_vinculados and cod_identificador not in ["PC","CL","IQ","IN"]:                
                    self.list_identificadores_vinculados.append(identificador)                   
                texto= texto.replace(identificador,"")
            else:
                break    
            
            
class Audiencia:
    id_audiencia:int=None       
    lugar:str=None
    observacion:str=None
    ubicacion:str=None    
    url_info_lobby:str='https://www.infolobby.cl/Ficha/Audiencia/'
    url_ley_lobby:str='https://www.leylobby.gob.cl/instituciones/'
    fecha_inicio:datetime=None
    fecha_termino:datetime=None
        
    def __init__(self,id_audiencia:int,lugar:str,observacion:str,ubicacion:str,fecha_inicio:str,fecha_termino:str):
        self.id_audiencia=id_audiencia 
        if Funciones.es_vacio_o_nulo(fecha_inicio)is False and fecha_inicio.isnumeric() is False:
            self.fecha_inicio=Funciones.stringafechatiempo(fecha_inicio)
        if Funciones.es_vacio_o_nulo(fecha_termino)is False and fecha_termino.isnumeric() is False:     
            self.fecha_termino=Funciones.stringafechatiempo(fecha_termino)
        if Funciones.es_vacio_o_nulo(ubicacion)is False and ubicacion.isnumeric() is False and any(char.isalpha() for char in ubicacion):   #Comuna
            self.ubicacion=Funciones.limpiar_texto(ubicacion).title()
        if Funciones.es_vacio_o_nulo(lugar)is False and lugar.isnumeric() is False and any(char.isalpha() for char in lugar) :
            self.lugar=Funciones.limpiar_texto(lugar).title()
        if Funciones.es_vacio_o_nulo(observacion)is False and observacion.isnumeric() is False and any(char.isalpha() for char in observacion):
            observacion=Funciones.limpiar_texto(observacion).capitalize()                      
            self.observacion=observacion[:5000]
            
    
    def url_build_web(self, codigo_institucion:str, id_sujeto_pasivo:str):          
        self.url_info_lobby+= f'{codigo_institucion}{self.id_audiencia}1'
        #https://www.infolobby.cl/Ficha/Audiencia/AE006312971  
        self.url_ley_lobby+= f'{codigo_institucion}/audiencias/{self.fecha_inicio.year}/{id_sujeto_pasivo}/{self.id_audiencia}'         
        #https://www.leylobby.gob.cl/instituciones/AE006/audiencias/2015/1723/31297  

class Entidad:
    rut:str=None
    rut_es_valido:bool=None
    nombre:str=None    
    giro:str=None
    domicilio:str=None
    representante_directorio:str=None
    naturaleza:str=None
    directorio:str=None    

    def __init__(self,rut:str,nombre:str,giro:str,domicilio:str,representante_directorio:str,naturaleza:str,directorio:str):        
        if Funciones.es_vacio_o_nulo(rut)is False and len(rut)>=5: 
            rut=rut.replace(".","").replace(" ","")
            if len(rut)>=9 and len(rut)<=10  and rut[-2:-1]=='-' and rut[:-2].isnumeric() is True:                
                self.rut=Funciones.dar_formato_al_rut(rut) #Formato para el rut chileno  
                self.rut_es_valido=1            
            else:
                self.rut=rut.replace("-","") #identenficador para entranjeros ejemplo: "Hemasoft Software SL" id B82874173 orden de compra 956-1388-SE18
                self.rut_es_valido=0
        if Funciones.es_vacio_o_nulo(nombre)is False and any(char.isalpha() for char in nombre) and len(nombre)>=3:
            nombre=Funciones.limpiar_texto(nombre).upper()            
            nombre=Funciones.limpiar_nombre(nombre).replace(" SOCIEDAD ANONIMA","").replace("LTDA","").replace(" LTD","")
            self.nombre=" ".join([palabra for  palabra in nombre.split() if palabra not in ["SA","LIMITADA"]])         
            
        if Funciones.es_vacio_o_nulo(giro)is False and giro.isnumeric() is False and any(char.isalpha() for char in giro) :
            self.giro=Funciones.limpiar_texto(giro).title()
        if Funciones.es_vacio_o_nulo(representante_directorio)is False and any(char.isalpha() for char in representante_directorio) :
            representante_directorio=Funciones.limpiar_texto(representante_directorio)
            self.representante_directorio=Funciones.quitar_puntos(representante_directorio).title()
        if Funciones.es_vacio_o_nulo(naturaleza)is False and any(char.isalpha() for char in naturaleza):
            self.naturaleza=Funciones.limpiar_texto(naturaleza).title()
        if Funciones.es_vacio_o_nulo(domicilio)is False and any(char.isalpha() for char in domicilio):
            self.domicilio=Funciones.limpiar_texto(domicilio).title()
        if Funciones.es_vacio_o_nulo(directorio)is False and any(char.isalpha() for char in directorio) :
            directorio=Funciones.limpiar_texto(directorio)
            self.directorio=Funciones.quitar_puntos(directorio).title()
                
class Materia:
    nombre:str=None
    
    def __init__(self,nombre:str):
        if  Funciones.es_vacio_o_nulo(nombre)is False:  
            self.nombre=Funciones.limpiar_texto(nombre)

class HoraChile():        
    hora_inicio_extraccion:datetime=None
    hora_final_extraccion:datetime=None        
    __utc_chile:tz=None

    def __init__(self):
        self.__utc_chile= tz.gettz('America/Santiago')#https://nodatime.org/TimeZones
        #print(type(self.__utc_chile))
        datetime_chile=self.reconstruir_hora_de_chile()      
        
        #Establece la hora de inicio y termino de ejecucion
        self._hora_inicio_extraccion = datetime_chile.replace(hour=18,minute=00,second=0,microsecond=0)+datetime.timedelta(days=-1 if datetime_chile.time() <= datetime.time(8,0,0,0) and datetime_chile.time() >= datetime.time.min else 0)# Hora Oficial Entre 22:00 a 07:00 hrs. Restriccion horaria para extraer desde la API
        self._hora_final_extraccion = datetime_chile.replace(hour=8,minute=00,second=0,microsecond=0)+datetime.timedelta(days=1 if datetime_chile.time() >= datetime.time(8,0,0,1) and datetime_chile.time() <= datetime.time.max else 0)#hora Oficial       

      
    def calcular_si_hora_de_extraccion_es_valida(self):                
        return datetime.datetime.now(self.__utc_chile).replace(tzinfo=None) < self._hora_inicio_extraccion  
    
    def calcular_si_fecha_actual_es_menor_a_la_hora_final_de_extraccion(self,fecha_extraccion):
        return  datetime.datetime.now(self.__utc_chile).replace(tzinfo=None) < self._hora_final_extraccion  and fecha_extraccion.date() < datetime.datetime.now(self.__utc_chile).date()
    
    def reconstruir_hora_de_chile(self):
        return datetime.datetime.now(self.__utc_chile).replace(tzinfo=None)   
    
    def calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion(self):
        return datetime.datetime.now(self.__utc_chile).replace(tzinfo=None) > self._hora_final_extraccion

class Num_Page:
    num_page_incremento:int
    num_page_decremento:int
    num_page_limit:int
    num_page:int

    def __init__(self,num_page_incremento:int,num_page_decremento:int,num_page_limit:int):
        self.num_page=self.num_page_incremento=num_page_incremento-2
        self.num_page_decremento=num_page_decremento if num_page_limit ==num_page_decremento else  num_page_decremento+3
        self.num_page_limit=num_page_limit
        