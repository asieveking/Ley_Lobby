import datetime
from dateutil import tz
from sample import functions



class Persona:
    id_perfil:int=None
    _nombre_completo:str
    _apellido_completo:str=None
    
    def __init__(self,nombre_completo:str,apellido_completo:str):                 
        self.nombre_completo=nombre_completo    
        self.apellido_completo=apellido_completo                            

    @property
    def nombre_completo(self)->str:
        return self._nombre_completo
    
    @nombre_completo.setter
    def nombre_completo(self, nombre_completo:str)->None:
        if functions.es_vacio_o_nulo(nombre_completo)is False: 
            nombre_completo=functions.transcripcion_simbolos_vocales(nombre_completo)
            nombre_completo=functions.borrar_caracteres_no_alfabeticos(nombre_completo)
            self._nombre_completo=nombre_completo.title()

    @property
    def apellido_completo(self)->str:
        return self._apellido_completo
    
    @apellido_completo.setter
    def apellido_completo(self, apellido_completo:str)-> None:
        if functions.es_vacio_o_nulo(apellido_completo)is False: 
            apellido_completo=functions.transcripcion_simbolos_vocales(apellido_completo)
            apellido_completo=functions.borrar_caracteres_no_alfabeticos(apellido_completo)
            self._apellido_completo=apellido_completo.title()

        


class Institucion:
    id_institucion:int
    _codigo_institucion:str=None
    list_instituciones:list=[]  

    @property
    def codigo_institucion(self) -> str:        
        if self._codigo_institucion is None:
           self._get_codigo()
        return self._codigo_institucion 

    @codigo_institucion.setter
    def codigo_institucion(self,codigo_institucion:str) -> None:
        if codigo_institucion is not None:
            self._codigo_institucion=codigo_institucion

    def _get_codigo(self) -> None:        
        self.codigo_institucion=next((id[1] for id in self.list_instituciones if id[0]==self.id_institucion),None)
    

class Cargo:   
    id_cargo_api:int
    _nombre_cargo:str
    _resolucion:str
    _url_resolucion:str
    _fecha_inicio:datetime
    _fecha_termino:datetime    
    list_identificadores_vinculados:list

    def __init__(self,id_cargo_api:int,nombre_cargo:str,resolucion:str,url_resolucion:str,fecha_inicio:str,fecha_termino:str): 
        self.list_identificadores_vinculados = []        
        self.id_cargo_ap = id_cargo_api                  
        self.nombre_cargo = nombre_cargo
        self.resolucion = resolucion
        self.resolucion = url_resolucion
        self.fecha_inicio = fecha_inicio       
        self.fecha_termino = fecha_termino   
    
    @property
    def nombre_cargo(self) -> str:
        return self._nombre_cargo

    @nombre_cargo.setter
    def nombre_cargo(self,nombre_cargo) -> None:
        if functions.es_vacio_o_nulo(nombre_cargo)is False and any(char.isalpha() for char in nombre_cargo):
            nombre_cargo = functions.limpiar_texto(nombre_cargo)                    
            self._nombre_cargo=functions.limpiar_nombre(nombre_cargo).title()            
            self._licitacion_relacionada_dentro_de_texto(self._nombre_cargo)    
    
    @property
    def resolucion(self) -> str:
        return self._resolucion

    @resolucion.setter
    def resolucion(self,resolucion)->None:
        if functions.es_vacio_o_nulo(resolucion)is False and any(char.isalpha() for char in resolucion) :
            resolucion=functions.limpiar_texto(resolucion).capitalize()
            self._licitacion_relacionada_dentro_de_texto(resolucion)            
            self._resolucion=resolucion[:5000] 

    @property
    def url_resolucion(self) -> str:
        return self._url_resolucion

    @url_resolucion.setter
    def url_resolucion(self, url_resolucion) -> str:
        if functions.es_vacio_o_nulo(url_resolucion)is False:
            self._url_resolucion="".join(url_resolucion.split())
    
    @property
    def fecha_inicio(self)->str:
        return self._fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self,fecha_inicio)->None:
        if functions.es_vacio_o_nulo(fecha_inicio)is False :            
            self._fecha_inicio=fecha_inicio

    @property
    def fecha_termino(self)->str:
        return self._fecha_termino

    @fecha_termino.setter
    def fecha_termino(self,fecha_termino)->None:
        if functions.es_vacio_o_nulo(fecha_termino)is False :            
            self._fecha_termino=fecha_termino

    def _licitacion_relacionada_dentro_de_texto(self,texto:str):             
        while True:    
            identificador=functions.buscar_identificador_licitacion_en_texto(texto)        
            if identificador is None:
               break
            cod_identificador=identificador.split("-")[2][:2]
            if identificador not in self.list_identificadores_vinculados and cod_identificador not in ["PC","CL","IQ","IN"]:                
                self.list_identificadores_vinculados.append(identificador)                   
            texto= texto.replace(identificador,"")
            
            
            
class Audiencia:
    id_audiencia:int
    _lugar:str
    _observacion:str
    _ubicacion:str    
    _fecha_inicio:datetime
    _fecha_termino:datetime
    url_info_lobby:str='https://www.infolobby.cl/Ficha/Audiencia/'
    url_ley_lobby:str='https://www.leylobby.gob.cl/instituciones/'
        
    def __init__(self,id_audiencia:int,lugar:str,observacion:str,ubicacion:str,fecha_inicio:str,fecha_termino:str):
        self.id_audiencia=id_audiencia         
        self.fecha_inicio=fecha_inicio        
        self.fecha_termino=fecha_termino
        self.ubicacion=ubicacion                
        self.lugar=lugar
        self.observacion=observacion
       
    @property
    def fecha_inicio(self) -> datetime:
        return self._fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, fecha_inicio:datetime) -> None:
        if functions.es_vacio_o_nulo(fecha_inicio)is False and fecha_inicio.isnumeric() is False:
            self._fecha_inicio=functions.string_to_datetime(fecha_inicio)

    @property
    def fecha_termino(self) -> datetime:
        return self._fecha_termino

    @fecha_termino.setter
    def fecha_termino(self, fecha_termino:datetime) -> None:
        if functions.es_vacio_o_nulo(fecha_termino)is False and fecha_termino.isnumeric() is False:
            self._fecha_termino=functions.string_to_datetime(fecha_termino) 

    @property
    def ubicacion(self) -> str:
        return self._ubicacion

    @ubicacion.setter
    def ubicacion(self,ubicacion)-> None: #Comuna
        if functions.es_vacio_o_nulo(ubicacion)is False and ubicacion.isnumeric() is False and any(char.isalpha() for char in ubicacion):   
            self._ubicacion=functions.limpiar_texto(ubicacion).title()

    @property
    def lugar(self) -> str:
        return self._lugar
    
    @lugar.setter
    def lugar(self, lugar) -> str:
        if functions.es_vacio_o_nulo(lugar)is False and lugar.isnumeric() is False and any(char.isalpha() for char in lugar) :
            if lugar in ['.com', '.cl']:
                self.lugar=lugar.lower()
            else:    
                self._lugar=functions.limpiar_texto(lugar)


    @property
    def observacion(self) -> str:
        return self._observacion
    
    @observacion.setter
    def observacion(self,observacion) -> None:
        if functions.es_vacio_o_nulo(observacion)is False and observacion.isnumeric() is False and any(char.isalpha() for char in observacion):
            observacion=functions.limpiar_texto(observacion).capitalize()                      
            self._observacion=observacion[:5000]        

    
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
        if functions.es_vacio_o_nulo(rut)is False and len(rut)>=5: 
            rut=rut.replace(".","").replace(" ","")
            if len(rut)>=9 and len(rut)<=10  and rut[-2:-1]=='-' and rut[:-2].isnumeric() is True:                
                self.rut=functions.dar_formato_al_rut(rut) #Formato para el rut chileno  
                self.rut_es_valido=1            
            else:
                self.rut=rut.replace("-","") #identenficador para entranjeros ejemplo: "Hemasoft Software SL" id B82874173 orden de compra 956-1388-SE18
                self.rut_es_valido=0
        if functions.es_vacio_o_nulo(nombre)is False and any(char.isalpha() for char in nombre) and len(nombre)>=3:
            nombre=functions.limpiar_texto(nombre).upper()            
            nombre=functions.limpiar_nombre(nombre).replace(" SOCIEDAD ANONIMA","").replace("LTDA","").replace(" LTD","")
            self.nombre=" ".join([palabra for  palabra in nombre.split() if palabra not in ["SA","LIMITADA"]])         
            
        if functions.es_vacio_o_nulo(giro)is False and giro.isnumeric() is False and any(char.isalpha() for char in giro) :
            self.giro=functions.limpiar_texto(giro).title()
        if functions.es_vacio_o_nulo(representante_directorio)is False and any(char.isalpha() for char in representante_directorio) :
            representante_directorio=functions.limpiar_texto(representante_directorio)
            self.representante_directorio=functions.quitar_puntos(representante_directorio).title()
        if functions.es_vacio_o_nulo(naturaleza)is False and any(char.isalpha() for char in naturaleza):
            self.naturaleza=functions.limpiar_texto(naturaleza).title()
        if functions.es_vacio_o_nulo(domicilio)is False and any(char.isalpha() for char in domicilio):
            self.domicilio=functions.limpiar_texto(domicilio).title()
        if functions.es_vacio_o_nulo(directorio)is False and any(char.isalpha() for char in directorio) :
            directorio=functions.limpiar_texto(directorio)
            self.directorio=functions.quitar_puntos(directorio).title()
                
class Materia:
    nombre:str=None
    
    def __init__(self,nombre:str):
        if  functions.es_vacio_o_nulo(nombre)is False:  
            self.nombre=functions.limpiar_texto(nombre)

class HoraChile():        
    hora_inicio_extraccion:datetime
    hora_final_extraccion:datetime        
    __utc_chile:tz

    def __init__(self):
        self.__utc_chile= tz.gettz('America/Santiago')#https://nodatime.org/TimeZones
        #print(type(self.__utc_chile))
        datetime_chile=self.reconstruir_hora_de_chile()      
        
        #Establece la hora de inicio y termino de ejecucion
        self.hora_inicio_extraccion = datetime_chile.replace(hour=18,minute=00,second=0,microsecond=0)+datetime.timedelta(days=-1 if datetime_chile.time() <= datetime.time(8,0,0,0) and datetime_chile.time() >= datetime.time.min else 0)# Hora Oficial Entre 22:00 a 07:00 hrs. Restriccion horaria para extraer desde la API
        self.hora_final_extraccion = datetime_chile.replace(hour=8,minute=00,second=0,microsecond=0)+datetime.timedelta(days=1 if datetime_chile.time() >= datetime.time(8,0,0,1) and datetime_chile.time() <= datetime.time.max else 0)#hora Oficial       

      
    def calcular_si_hora_de_extraccion_es_valida(self)->bool:                
        return datetime.datetime.now(self.__utc_chile).replace(tzinfo=None) < self.hora_inicio_extraccion  
    
    def calcular_si_fecha_actual_es_menor_a_la_hora_final_de_extraccion(self,fecha_extraccion)->bool:
        return  datetime.datetime.now(self.__utc_chile).replace(tzinfo=None) < self.hora_final_extraccion  and fecha_extraccion.date() < datetime.datetime.now(self.__utc_chile).date()
    
    def reconstruir_hora_de_chile(self)-> datetime:
        return datetime.datetime.now(self.__utc_chile).replace(tzinfo=None)   
    
    def calcular_si_fecha_actual_es_mayor_a_la_hora_final_de_extraccion(self)->datetime:
        return datetime.datetime.now(self.__utc_chile).replace(tzinfo=None) > self.hora_final_extraccion

class Num_Page:
    num_page_incremento:int
    num_page_decremento:int
    num_page_limit:int
    num_page:int

    def __init__(self,num_page_incremento:int,num_page_decremento:int,num_page_limit:int):
        self.num_page=self.num_page_incremento=num_page_incremento-2
        self.num_page_decremento=num_page_decremento if num_page_limit ==num_page_decremento else  num_page_decremento+3
        self.num_page_limit=num_page_limit
        