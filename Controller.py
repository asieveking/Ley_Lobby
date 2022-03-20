import datetime
from dateutil import tz

import Funciones


class Persona:
    _id_perfil:int=None  #string      
    _nombres:str=None
    _apellidos:str=None    
    
    def __init__(self,nombres:str,apellidos:str):        
        if Funciones.es_vacio_o_nulo(nombres)is False:            
            nombres=Funciones.transcripcion_simbolos_vocales(nombres)
            nombres="".join( [caracter if caracter.isalpha() is True else " " for caracter in nombres ])
            self._nombres=" ".join(nombres.split()).title()            
        if Funciones.es_vacio_o_nulo(apellidos)is False:  
            apellidos=Funciones.transcripcion_simbolos_vocales(apellidos)
            apellidos="".join( [caracter if caracter.isalpha() is True else " " for caracter in apellidos])
            self._apellidos=" ".join(apellidos.split()).title()

class Instituciones:
    _id_institucion:int=None
    _cod_institucion:str=None
    _instituciones:list=[]

    def get_codigo(self,id_institucion:int):
        self._id_institucion=id_institucion
        cod=[ id[1] for id in self._instituciones if id[0]==self._id_institucion ]       
        self._cod_institucion= cod[0] if len(cod)>0 else None
    

class Cargo:   
    _id_cargo_api:int=None 
    _nombre_cargo:str=None
    _resolucion:str=None
    _url_resolucion:str=None
    _fecha_inicio:datetime=None
    _fecha_termino:datetime=None
    _list_cargos_db:list = None
    _list_identificadores_vinculados:list=None

    def __init__(self,id_cargo_api:int,nombre_cargo:str): 
        self._list_identificadores_vinculados =[]
        self._list_cargos_db=[]
        self._id_cargo_api= id_cargo_api                  
        if Funciones.es_vacio_o_nulo(nombre_cargo)is False and any(char.isalpha() for char in nombre_cargo):
            nombre_cargo=Funciones.limpiar_texto(nombre_cargo)                    
            self._nombre_cargo=Funciones.limpiar_nombre(nombre_cargo).title()            
            self.licitacion_relacionada_dentro_de_texto(self._nombre_cargo)
   
    def rellenar_campos(self,resolucion:str,url_resolucion:str,fecha_inicio:str,fecha_termino:str):
        if Funciones.es_vacio_o_nulo(resolucion)is False and any(char.isalpha() for char in resolucion) :
            resolucion=Funciones.limpiar_texto(resolucion).capitalize()
            self.licitacion_relacionada_dentro_de_texto(resolucion)
            #TODO quitar cantidad de caracteres
            self._resolucion=resolucion[:5000]            
        if Funciones.es_vacio_o_nulo(url_resolucion)is False:
            self._url_resolucion="".join(url_resolucion.split())
        if Funciones.es_vacio_o_nulo(fecha_inicio)is False :
            # self._fecha_inicio=Funciones.stringafecha(fecha_inicio)
            self._fecha_inicio=fecha_inicio
        if Funciones.es_vacio_o_nulo(fecha_termino)is False:
            # self._fecha_termino=Funciones.stringafecha(fecha_termino)
            self._fecha_termino=fecha_termino
    
    def licitacion_relacionada_dentro_de_texto(self,texto:str):             
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
    _id_audiencia:int=None       
    _lugar:str=None
    _observacion:str=None
    _ubicacion:str=None    
    _url_info_lobby:str='https://www.infolobby.cl/Ficha/Audiencia/'
    _url_ley_lobby:str='https://www.leylobby.gob.cl/instituciones/'
    _fecha_inicio:datetime=None
    _fecha_termino:datetime=None
        
    def __init__(self,id_audiencia:int,lugar:str,observacion:str,ubicacion:str,fecha_inicio:str,fecha_termino:str):
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
            self._observacion=observacion[:5000]
            

    def url_build_web(self, codigo_institucion:str, id_sujeto_pasivo:str):          
        self._url_info_lobby+= f'{codigo_institucion}{self._id_audiencia}1'
        #anio=self._fecha_inicio.year#.strftime("%Y")# .split("-")[0]   
        self._url_ley_lobby+= f'{codigo_institucion}/audiencias/{self._fecha_inicio.year}/{id_sujeto_pasivo}/{self._id_audiencia}' 
        #https://www.infolobby.cl/Ficha/Audiencia/AE006312971
        #https://www.leylobby.gob.cl/instituciones/AE006/audiencias/2015/1723/31297  

class Entidad:
    _rut:str=None
    _rut_es_valido:bool=None
    _nombre:str=None    
    _giro:str=None
    _domicilio:str=None
    _representante_directorio:str=None
    _naturaleza:str=None
    _directorio:str=None    

    def __init__(self,rut:str,nombre:str,giro:str,domicilio:str,representante_directorio:str,naturaleza:str,directorio:str):        
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
        if Funciones.es_vacio_o_nulo(representante_directorio)is False and any(char.isalpha() for char in representante_directorio) :
            representante_directorio=Funciones.limpiar_texto(representante_directorio)
            self._representante_directorio=Funciones.quitar_puntos(representante_directorio).title()
        if Funciones.es_vacio_o_nulo(naturaleza)is False and any(char.isalpha() for char in naturaleza):
            self._naturaleza=Funciones.limpiar_texto(naturaleza).title()
        if Funciones.es_vacio_o_nulo(domicilio)is False and any(char.isalpha() for char in domicilio):
            self._domicilio=Funciones.limpiar_texto(domicilio).title()
        if Funciones.es_vacio_o_nulo(directorio)is False and any(char.isalpha() for char in directorio) :
            directorio=Funciones.limpiar_texto(directorio)
            self._directorio=Funciones.quitar_puntos(directorio).title()
                
class Materia:
    _nombre:str=None
    
    def __init__(self,nombre:str):
        if  Funciones.es_vacio_o_nulo(nombre)is False:  
            self._nombre=Funciones.limpiar_texto(nombre)

class HoraChile():        
    _hora_inicio_extraccion:datetime=None
    _hora_final_extraccion:datetime=None        
    _utc_chile:tz=None

    def __init__(self):
        self._utc_chile= tz.gettz('America/Santiago')#https://nodatime.org/TimeZones
        print(type(self._utc_chile))
        datetime_chile=self.reconstruir_hora_de_chile()      
        
        #Establece la hora de inicio y termino de ejecucion
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

    def __init__(self,num_page_incremento:int,num_page_decremento:int,num_page_limit:int):
        self._num_page=self._num_page_incremento=num_page_incremento-2
        self._num_page_decremento=num_page_decremento if num_page_limit ==num_page_decremento else  num_page_decremento+3
        self._num_page_limit=num_page_limit
        