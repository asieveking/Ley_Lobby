import re
import html
import datetime, time
#!pip install ntplib
import ntplib
import requests
#!pip install beautifulsoup4
from bs4 import BeautifulSoup


def quitar_tildes(texto):
    a,b = 'àáèéìíòóùúüÀÁÈÉÌÍÒÓÙÚÜ','aaeeiioouuuAAEEIIOOUUU'
    trans = str.maketrans(a,b)
    return texto.translate(trans).strip() 

def limpiar_nombre(texto):
    return "".join([caracter for caracter in texto if caracter not in ['?','¿','"',"'",".",',',":"]])
    

def limpiar_texto(texto): 
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
    return quitar_tildes(texto)

def quitar_puntos(texto):         
    return texto.replace('.','').strip() 
    
def total_caracteres(texto):
    return texto[:4790]

def stringafecha(fecha):
    return datetime.datetime.strptime(fecha,'%Y-%m-%d')

def stringafechatiempo(fecha):
    return datetime.datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S')    

def limpiarstringfechatiempo(fecha):
    return fecha.split('.')[0].replace("T"," ")

def stringafloat(texto): #TODO Este metodo puede ser mejorado a uno por expresion regular
    texto= texto.replace("UF","").replace("$","").replace("US","").replace("D","").replace("EUR","")
    return float(texto.replace(".","").replace(",",".") if texto.find(",")!=-1 else texto.replace(".",""))

def es_vacio_o_nulo(valor):
    if valor and type(valor) is str:
        valor=valor.strip() 
    if type(valor) in [int,float]:
        return False
    if not valor or valor is None or valor=="":
        return True #True si valor es NULO
    return False  #False si valor contiene una letra o numero

def buscar_identificador_licitacion_en_texto(texto):
    try:
        return re.search("[\d]+\-[\d]+\-[A-Z]{1,2}[\d]{1,3}", texto).group(0).upper()
        
    except:
        return None

def buscar_rut_en_texto(texto): #Precaucion!!! el return de datos jamas debe ser modificado (Upper -Lower) debido a que un metodo, relacionado al scrappy, necesita el rut sin modificar para luego limpiar el nombre del proveedor quitandole el rut encontrado. Ejemplo 11195673-k ASTRO QUIMICA ( rut debe ser respetado y nunca debe modificarse como retorno de este metodo)
    try:        
        return re.search("[\d]{7,8}\-[\w]|[\d]{1,2}\.[\d]{3}\.[\d]{3}\-[\w]|[\d]{7,8}[\w]", texto).group(0)
    except:
        return None

def email_es_valido(email):
  try: 
    re.search("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$|[\w]+\@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}|^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$", email).group(0)
    return True
  except:
    return False

def dar_formato_al_rut(rut):  
    rut=rut.upper().replace(" ","")       
    if True if rut.find("-")!=-1 and rut.find(".")!=-1 else False:
        return rut 
    else: 
        rut=rut.replace(".","").replace("-","")
        largo=len(rut)
        return f'{rut[0:largo-7]}.{rut[largo-7:largo-4]}.{rut[largo-4:-1]}-{rut[-1:]}'



def url_build_ley_lobby(nombre_consulta):
    url="https://www.leylobby.gob.cl/api/v1/"
    if nombre_consulta=="Audiencias_Page":
        url+="audiencias?page="
    if nombre_consulta=="Audiencias":
        url+="audiencias/"
    if nombre_consulta=="Cargos_Pasivos":
        url+="cargos-pasivos/"
    if nombre_consulta=="Instituciones":
        url+="instituciones/"    
    return url+'{}'

def get_request_api(url,time_start,header={},verify=True,segundos_espera=2): #5 segundos de espera por defecto. Si disminuye este valor a menos de 5, la consulta falla.
    flag_loop=True
    while flag_loop:
        diferencia=segundos_espera-(time.time()-time_start)
        time.sleep(0 if diferencia < 0 else diferencia ) # 300 miliseconds (.3) or 5 seconds (5)wwwwwwww
        #payload,headers ={},{}  
        json,flag,time_start=None,True,time.time()    
        try:            
            with requests.get( url,headers=header, timeout=180,verify=verify) as response:            
                # print(f'{response} and {response.text}')  
                json=response.json()            
                assert response.status_code==200 and json is not None
        except requests.ConnectionError or requests.ReadTimeout:
            time.sleep(30)     
        except Exception:
            flag=False 
        else:
            flag_loop=False
    
    return json,time_start,flag

def get_url_scrappy(url,segundos_espera=15):
    source,intento=None,3    
    time.sleep(segundos_espera)
    while source is None and intento>0:
        try:
            source= requests.get(url, timeout=120)
            source.raise_for_status()                                             
        except:
            source=None
            time.sleep(100)
        finally:
            intento-=1
    return BeautifulSoup(source.text, 'lxml') if source  else None   

def hora_chile():
    response,intento= None,3 
    c = ntplib.NTPClient()
    while response is None and intento>0:
        try:            
            response = c.request('ntp.shoa.cl',timeout=60)           
        except:
            time.sleep(5)
        finally:
            if response is None:
                intento-=1
    return datetime.datetime.fromtimestamp(response.dest_time) if response is not None else None 





# def buscar_distinto(lista_api,lista_db):
    
#     list_temp=[id["CodigoExterno"] for id in lista_api ]

#     list_temp2= list(set(list_temp))
#     list_temp3=list(dict.fromkeys(list_temp))
#     list_temp4= [x for  x in list_temp if list_temp.count(x) > 1]


# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
# def requests_retry_session(
#     retries=3,
#     backoff_factor=0.5,
#     status_forcelist=(500, 502, 504),
#     session=None,
# ):
#     session = session or requests.Session()
#     retry = Retry(
#         total=retries,
#         read=retries,
#         connect=retries,
#         backoff_factor=backoff_factor,
#         status_forcelist=status_forcelist,
#     )
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#     return session