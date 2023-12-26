import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder#Transformar instancias de modelo de datos a un diccionario de datos
from fastapi.responses import JSONResponse #formatear respuesta json y poder incluir incluir el codigo de estado en la API
from pydantic import BaseModel#para crear clases, modelos de datos

from constants import FAKE_DB_TOOLS
from typing import Union, Optional #permitira definir parametros de tipo query en en API, estos se insertar como parametros de la función. Fastapi los detecta automaticamente como parametro de la funcion
from mangum import Mangum


tools_list=[]
tools_list.extend(FAKE_DB_TOOLS)#Se guarda en una lista la lista de json declarada en el archivo constants

class Tool(BaseModel):#Para esto se creo un modelo de datos con la clase Tool, que hereda d ela clase BaseModel. Este objeto sera recibido como json en la API y fastapi lo parsea y lo convirte en clase.
#El id debe ser opcional para la inserción de datos
    id: Optional[str] = None #valor por defecto es None y es una variable opcional
    name: str
    category:str

def find_index_by_id(tool_id):#encuentra el indice por id, en el id de herramienta, recibe como herramienta el id del elemento a buscar
    _index=None#Valor por defecto sera nulo, ya que si no lo encuentra lo retorna vacio
    for index,value in enumerate(tools_list):# se itera en la lista, y con enumerate vuelve la lista en u objeto json, guarda como clave el indice y el valor es el objeto, asi se almacena el inice cuando encontremos el valor
        if value['id']==tool_id:# se valida si el id del objeto iterado es igual al id que se quiere encontrar
            _index= index#se guarda el indice
            break#salimos del bluque
    return _index#se retorna el indice mediente el id y se pueda actualizar sin ningun problema

app = FastAPI()#instancia de la clase fastapi
handler=Mangum(app)

######## GET ALL

@app.get(path='/api/tools/get_all')#Ruta que retornará las herramientas, el parametro path indica la ruta

async def get_all_tools(category:Union[str, None]=None):#función asincronica como parte de la sincronia que caracteriza a startlet, el parametro lo detecta automaticamente y se le entrega como parametro a union el tipo de valor y el valor por defecto. Modificar categoria y recuperar la cateogira
    response =tools_list#valor por defecto
    if category:#si la caetgoria existe
        response=list(filter(lambda x:x['category']==category, tools_list))
    return JSONResponse(content=response, status_code=200)#sirve para generar un json, donde el paramero content es la data y status_code el estado de solicitud. Puede revisar esta solicitud dirigiendome a la URL http://localhost:8000/api/tools/get_all 


######## GET Query String

#filtro con pathparams, filtro a través de ID
#definir endpoint que entrgue herramienta en base a su ID. Este ID sera pasado como pathparam. Si el ID no esta retornará nulo junto con un ccodigo 404 y si existe retornará el objeto en caso exista.

@app.get(path='/api/tools/{tool_id}')#Ruta que retornará las herramientas, el parametro path indica la ruta

async def get_tool(tool_id:str):#función asincronica como parte de la sincronia que caracteriza a startlet, el parametro se debe entregar e igualar
    response =None#valor por defecto
    status_code =404#valocodigo por defecto, se definen asi en caso de que no lo encuentre

    for tool in tools_list:#se recore la lista de herramientas
        if tool['id']==tool_id:#en caso que cosida el id
            response = tool#se entrega el json de ese id
            status_code=200#status code cambia a exitoso
            break
        
    return JSONResponse(content=response, status_code=status_code)#sirve para generar un json, donde el paramero content es la data y status_code el estado de solicitud. Puede revisar esta solicitud dirigiendome a la URL http://localhost:8000/api/tools/{tool_id}}


######## POST

#agregar una elemento nuevo al lista existente. Crear nuevos registros. Implementar metodo con fastAPI, generar un ID nuevo y se añade el objeto en el listado 

@app.post(path='/api/tools')#Se implementa un nuevo endpoint de tipo post que recibira en el request body el objeto a crear. Los parametros body no son parte del endpoint
async def create_tool(tool: Tool):#FastApi leera el request body, obtiene los atributos necesarios para instanciar la calse tool y devolveria  instancia de la misma como argumento
    tool_id=tool.id#Se recupera el id si es que exista
    if tool_id is None:
        tool.id =  f'{tool.name}-{tool.category}'
    tools_list.append(tool.dict())# se agrega el registro a la lista json
    json_data = jsonable_encoder(tool)#se cododifca como json el registro a agregar
    return JSONResponse(content=json_data, status_code=201)
######## PUT

#Actualizar o reemplazar un registro en una API, se configurará un endpoint que reemplace un elemento del listado. Para ello se necesita el id del elemento y el objeto a reemplazar. Por esto se necesita un path para buscar el id de la herramienta y un request body para agregar el elemento con modificaciones 
@app.put(path='/api/tools/{tool_id}')#Recibirá un path parameter del id de la herramienta a actualizar, si es que existe se actualiza, si es que no se retorna un codigo 404 con data nula, también se recibira un request body, se bueca indice d ela li
async def update_tool(tool_id:str, tool:Tool):#recibira el id del elemento a modificar y luego el body de la herramienta a modificar
    if tool.id is None:
        tool.id =  f'{tool.name}-{tool.category}'
    index_update=find_index_by_id(tool_id=tool_id)#Buscar el elemento dentro de la lista, y esta variable guarda el indice del elemento a actualizar
    if index_update is None:#no ha encontrado el indice en la lista, por tanto se retorna data nula con codigo de error 404
        return JSONResponse(content=None, status_code=404)
    else:
        tools_list[index_update]=tool.dict()#se accede a la lista en el indice que se quiere actualizar y se reemplaza el elemento sin problemas, transformando tool en un elemento dict
    return JSONResponse(content=True, status_code=200)


######## DELETE                                                               

#Para eliminar se configurará un endpoint para identificar el recurso a eliminar, en caso de que no enccontremos el elemento se retorna un error 404 y content nulo en caso que si lo encontremos se retornará un flag true junto a un codigo 200
@app.delete(path='/api/tools/{tool_id}')#Recibirá un path parameter del id de la herramienta a eliminar
async def delete_tool(tool_id:str):#recibira el id del elemento a modificar
    index_delete=find_index_by_id(tool_id=tool_id)#Buscar el elemento dentro de la lista, y esta variable guarda el indice del elemento a eliminar
    if index_delete is None:#no ha encontrado el indice en la lista, por tanto se retorna data nula con codigo de error 404
        return JSONResponse(content=None, status_code=404)
    else:
        #para eliminar elementos en una lista en base al indice se usa el metodo pop, eliminara el elemetno y retornará el elemendo eliminado
        eliminado = tools_list.pop(index_delete)
        return JSONResponse(content=eliminado, status_code=200)