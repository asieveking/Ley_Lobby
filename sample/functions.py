import requests
import datetime
import time
import re
import html

def transcripcion_simbolos_vocales(texto:str)->str:
    """_summary_

    Args:
        texto (str): Transcripcion de vocales con simbolos a el cual les cambiares a vocales normales (sin simbolos)
        

    Returns:
        str: retorna el valor sin tildes ni simbolos en las vocales   
             
        EXAMPLE: (input): Pingüino (output): Pinguino
        
        De: (àáèéìíòóùúüÀÁÈÉÌÍÒÓÙÚÜ) A: aaeeiioouuuAAEEIIOOUUU
    """
    a,b = 'àáèéìíòóùúüÀÁÈÉÌÍÒÓÙÚÜ','aaeeiioouuuAAEEIIOOUUU'
    transcription = str.maketrans(a,b)
    return texto.translate(transcription).strip() 

def borrar_caracteres_no_alfabeticos(texto:str) -> str:
    texto = "".join( [caracter if caracter.isalpha() is True else " " for caracter in texto])
    return " ".join(texto.split())  


def limpiar_nombre(texto:str)->str:
    return "".join([caracter for caracter in texto if caracter not in ['?','¿','"',"'",".",',',":"]])
    

def limpiar_texto(texto:str)->str: 
    texto=html.unescape(texto)     
    texto=" ".join(texto.split())    
    texto =texto.replace('--', ' ').replace(': -', ':-').replace('**', ' ').replace('""', '"').replace('.,', '.').replace('Nº','Nº ').replace('/ ','/').replace(' /','/')
    texto=" ".join(texto.split())  
    texto =texto.replace(' :', ': ').replace(' ,', ', ').replace(' .', '. ').replace(' "', '" ').replace('""', '').replace('( ', ' (').replace(' )', ') ').replace(' -', '-').replace('- ', '-').replace('• ', ' •')                   
    texto=" ".join(texto.split())
    while texto[-1:].isalnum()==False:
        texto=texto[:-1]
    while texto[:1].isalnum()==False: 
        texto=texto[1:]   
    return transcripcion_simbolos_vocales(texto)
    
def total_caracteres(texto:str)->str:
    return texto[:5000]

def stringafecha(fecha:str)->datetime:
    return datetime.datetime.strptime(fecha,'%Y-%m-%d')

def string_to_datetime(fecha:str)->datetime:
    return datetime.datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S')    

def stringafloat(texto:str)->float: #TODO Este metodo puede ser mejorado a uno por expresion regular
    texto= texto.replace("UF","").replace("$","").replace("US","").replace("D","").replace("EUR","")
    return float(texto.replace(".","").replace(",",".") if texto.find(",")!=-1 else texto.replace(".",""))

def es_vacio_o_nulo(valor)->bool:
    if valor and type(valor) is str:
        valor=valor.strip() 
    if type(valor) in [int,float]:
        return False
    if not valor or valor is None or valor=="":
        return True #True si valor es NULO
    return False  #False si valor contiene una letra o numero

def buscar_identificador_licitacion_en_texto(texto:str)->str:
    try:
        return re.search("[\d]+\-[\d]+\-[A-Z]{1,2}[\d]{1,3}", texto).group(0).upper()
        
    except:
        return None

def buscar_rut_en_texto(texto:str)->str: #Precaucion!!! el return de datos jamas debe ser modificado (Upper -Lower) debido a que un metodo, relacionado al scrappy, necesita el rut sin modificar para luego limpiar el nombre del proveedor quitandole el rut encontrado. Ejemplo 11195673-k ASTRO QUIMICA ( rut debe ser respetado y nunca debe modificarse como retorno de este metodo)
    try:        
        return re.search("[\d]{7,8}\-[\w]|[\d]{1,2}\.[\d]{3}\.[\d]{3}\-[\w]|[\d]{7,8}[\w]", texto).group(0)
    except:
        return None

def email_es_valido(email:str)->str:
  try: 
    re.search("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$|[\w]+\@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}|^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$", email).group(0)
    return True
  except:
    return False

def dar_formato_al_rut(rut:str)->str:  
    rut=rut.upper().replace(" ","")       
    if True if rut.find("-")!=-1 and rut.find(".")!=-1 else False:
        return rut 
    else: 
        rut=rut.replace(".","").replace("-","")
        largo=len(rut)
        return f'{rut[0:largo-7]}.{rut[largo-7:largo-4]}.{rut[largo-4:-1]}-{rut[-1:]}'

def get_request_api(url:str,time_start:time,header:dict={},verify:bool=True,segundos_espera:int=2)->list: #5 segundos de espera por defecto. Si disminuye este valor a menos de 5, la consulta falla.
    flag_loop=True
    while flag_loop:
        diferencia=segundos_espera-(time.time()-time_start)
        time.sleep(0 if diferencia < 0 else diferencia ) # 300 miliseconds (.3) or 5 seconds (5)wwwwwwww        
        json,flag,time_start=None,True,time.time()    
        try:            
            with requests.get( url,headers=header, timeout=180,verify=verify) as response:                            
                json=response.json()            
                assert response.status_code==200 and json is not None
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            time.sleep(30)             
        except Exception:
            flag=False 
        else:
            flag_loop=False
    
    return json,time_start,flag