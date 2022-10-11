import datetime
import json
from os import getenv
import asyncio
import jwt
import requests
from telethon import TelegramClient,events
from telethon.tl.types import PeerChannel,PeerUser
tokens={}
nosleep=True
isactiverefcode=False
usersprov={}
user_with_codes=[]
master_key=getenv('MASTER_KEY')
bot_key=getenv('BOT_KEY')
api_id =getenv('API_ID')
api_hash = getenv('API_HASH')
AUTH_TOKEN=getenv('AUTH_TOKEN')
province_limits={}
province_mainlimits={}
provinces={
    "Artemisa": "UHJvdmluY2U6NjQ=",
    "La Habana": "UHJvdmluY2U6Mzk=",
    "Mayabeque": "UHJvdmluY2U6NTk=",
    "Matanzas": "UHJvdmluY2U6NjE=",
    "Villa Clara": "UHJvdmluY2U6NjU=",
    "Cienfuegos": "UHJvdmluY2U6NjA=",
    "Ciego de Avila": "UHJvdmluY2U6NjM=",
    "Camaguey": "UHJvdmluY2U6NTc=",
    "Las Tunas": "UHJvdmluY2U6NTY=",
    "Granma": "UHJvdmluY2U6NTI=",
    "Santiago de Cuba": "UHJvdmluY2U6NTQ=",
    "Municipio Especial Isla de la Juventud": "UHJvdmluY2U6NjY=",
    "Pinar del Rio": "UHJvdmluY2U6NTg=",
    "Sancti Spiritus": "UHJvdmluY2U6NjI=",
    "Holguin": "UHJvdmluY2U6NTM=",
    "Guantanamo": "UHJvdmluY2U6NTU="
}
for provid in provinces.values():
    tokens[provid]={}
    usersprov[provid]=[]
    province_limits[provid]=1
    province_mainlimits[provid]=5

print(tokens)
active_province=set([])
print('Abierto')
async def maintread():
    # async def waker():
    #     while nosleep==True:
    #         requests.get()
    print('a')
    telesender=TelegramClient('BotSession', api_id, api_hash,loop=asyncio.get_running_loop())
    @telesender.on(events.NewMessage(pattern='/start'))
    async def startMessage(event):
        maingroup= await telesender.get_entity(PeerChannel(1315170897))
        user=await event.get_sender()
        print(maingroup)
        userslist=await telesender.get_participants(maingroup)
        usersid=[i.id for i in userslist]
        print(user)
        if user.id==5461780118 or user.id==848517956:
            await telesender.send_message(user,'Comandos:\n\
                                          /start |  Muestra este mensaje.\n\
                                          /plist |  Muestra la lista de provincias. \n\
                                          /limit #p #l|  Selecciona un limite para una provincia especifica. Sin argumentos muestra los limites. \n\
                                          /active #p  |  Activa una provincia especifica. Sin argumentos muestra provincias activas.\n\
                                          /deactive #p| Desactiva una provincia especifica.\n\
                                          /token #p   | Genera el comando para agregar los tokens para una provincia especifica.\n\
                                          /check {userlist}   |  Muestra los usuarios a los q pertenece cada cuenta.\n\
                                          /gettoken #tokenid  |  Envia la lista de tokens al programa.\n\
                                          /count #p  |  Cuenta los tokens de una provincia.\n\
                                          /cleanprov |  Limpia los tokens de una provincia.\n\
                                          /cleancode |  Limpia la lista de códigos para q puedan ser nuevamente solicitados.\n\
                                          /actcode   |  Activa la solicitud de tokens en la programa.\n\
                                          /deactcode |  Desactiva la solicitud de tokens en la programa.\n\
                                          /cleanchannel  |  Elimina las cuentas del canal q no esten en la base de datos.'
                                          )
            return
        
        if user.id in usersid:
            print(event.message.text)
            await telesender.send_message(user,'Bot para solicitar los codigos de la app ComboPick, envie el mensaje /code para solicitar el código')
        
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/plist'))
    async def plistMessage(event):
        user=await event.get_sender()
        plist=''
        count=0
        for a in provinces:
            if count>0:
                coma=', '
            else:
                coma=''
            plist=plist+coma+str(count)+'-'+a
            count=count+1
        await telesender.send_message(user,f'Seleccione una provincia: {plist}.\n Para activar una provincia envie el codigo /activate #p')
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/limit'))
    async def changeLimit(event):
        user=await event.get_sender()
        try:
            texto=event.text.replace('/limit','').strip()
            if texto=='':
                print(province_limits)
                strlimits=''
                count=0
                for key,value in province_limits.items():
                    provkey=list(provinces.keys())[list(provinces.values()).index(key)]
                    provlimit=value
                    strlimits+=str(count)+'-'+str(provkey)+':'+str(provlimit)+'\n'
                    count+=1
                await telesender.send_message(user,f'Limites:\n {strlimits}')
                return
            prov,limit=texto.split(' ')
            pname=[*provinces][int(prov)]
            provinceid=provinces[pname]
            print(pname,':',provinceid)
            province_limits[provinceid]=int(limit)
            await telesender.send_message(user,f'Limite cambiado: {pname}, Limite:{limit}')
        except Exception as err:
            print(err)
            await telesender.send_message(user,'Error en el formato. Correcto: /limit #prov #limit')
        
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/active'))
    async def active(event):
        user=await event.get_sender()
        acttext=event.text.replace('/active','').strip()
        if acttext=='':
            actname=[]
            for prov in active_province:
                actname.append(str(list(provinces.keys())[list(provinces.values()).index(prov)]))
            await telesender.send_message(user,f'Provincias activas: {actname}')
        try:
            pselect=int(acttext)
        except Exception as e:
            print(e)
            await telesender.send_message(user,'Error en el codigo de provincia')  
            return         
        print(pselect)
        if 0<=pselect<16:
            pname=[*provinces][pselect]
            provinceid=provinces[pname]
            print(pname,':',provinceid)
            active_province.add(provinceid)
            await telesender.send_message(user,f'Provincia activa: {pname}, id:{provinceid}')
            actname=[]
            for prov in active_province:
                actname.append(str(list(provinces.keys())[list(provinces.values()).index(prov)]))
            await telesender.send_message(user,f'Provincias activas:{actname}')
        else:
            await telesender.send_message(user,'Fuera del rango de provincias')
        
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/deactive'))
    async def deactive(event):
        user=await event.get_sender()
        try:
            pselect=int(event.text.replace('/deactive','').strip())
        except Exception as e:
            print(e)
            await telesender.send_message(user,'Error en el codigo de provincia')
            return
        print(pselect)
        if 0<=pselect<16:
            pname=[*provinces][pselect]
            provinceid=provinces[pname]
            print(pname,':',provinceid)
            active_province.discard(provinceid)
            await telesender.send_message(user,f'Provincia desactivada: {pname}, id:{provinceid}')
            await telesender.send_message(user,f'Provincias activas:{list(active_province)}')
        else:
            await telesender.send_message(user,'Fuera del rango de provincias')
        
    @telesender.on(events.NewMessage(pattern='{"province"'))        
    async def provMessage(event):
        maingroup= await telesender.get_entity(PeerChannel(1315170897))
        user=await event.get_sender()
        print(maingroup)
        userslist=await telesender.get_participants(maingroup)
        usersid=[i.id for i in userslist]
        print(user)        
        if user.id in usersid:
            print(event.message.text)
            try:
                datas=json.loads(event.message.text)
            except Exception as err:
                print(f'Error al cargar json:{err}')
                await telesender.send_message(user,'Token enviado en mal formato')
                return
            print(active_province)
            provinceid=datas['province']
            if provinceid in active_province:
                provtokenlist=[]
                for token in tokens[provinceid]:
                    provtokenlist=provtokenlist+tokens[provinceid][token]
                  
                if len(provtokenlist)>=province_mainlimits[provinceid]:
                    return await telesender.send_message(user,'La provincia ya esta llena y no acepta mas tokens')
                print('provincia activa')
                if tokens[provinceid].get(user.id) is None:
                    try:
                        tokendecoded=jwt.decode(datas['token'].strip().replace('JWT ',''),options={'verify_signature':False})                   
                    except Exception as err:
                        print(err)
                        return await telesender.send_message(user,'Token no valido')
                    if (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromtimestamp(tokendecoded['origIat'],datetime.timezone.utc)).total_seconds()<=2700:
                        tokens[provinceid][user.id]=[datas['token']]
                    else:
                        return await telesender.send_message(user,'Genere el token de nuevo este no es valido')
                else:
                    if len(tokens[provinceid].get(user.id))<province_limits[provinceid]:
                        if datas['token'] not in tokens[provinceid][user.id]:
                            tokens[provinceid][user.id].append(datas['token'])
                        else:
                            print("Token ya agregado")
                            return await telesender.send_message(user,'Este token ya fue agregado')
                    else:
                        return await telesender.send_message(user,'Ya envio el límite máximo de token para esta provincia')
                print('Token agregado correctamente')
                await telesender.send_message(user,'Token agregado correctamente')
            else:
                print('provincia inactiva')
                pname=str(list(provinces.keys())[list(provinces.values()).index(provinceid)])
                await telesender.send_message(user,f'Provincia {pname} inactiva espere a q se anuncie en el grupo la activación de la provincia')
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/count'))
    async def countTokens(event):
        user=await event.get_sender()
        strcount=event.text.replace('/count').strip()
        if strcount=='':
            return
        else:
            try:
                strcount=int(strcount)
                pname=[*provinces][strcount]               
            except:
                await telesender.send_message(user,'Error en el formato del comando. Correcto /count #p')
                return
            
        count=0
        for userid in tokens[strcount]:
            for i in userid:
                count+=1
        await telesender.send_message(user,f'{count} tokens almacenados en la provincia {pname}')
            
          
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/token'))        
    async def generateToken(event):
        user=await event.get_sender()
        try:
            prov=int(event.text.replace('/token','').strip())
            pname=[*provinces][prov]
            provinceid=provinces[pname]
            print(pname,':',provinceid)
        except:
            await telesender.send_message(user,'Mal formato en la solicitud de los tokens')
            return
        authTokens=[]
        if tokens[provinceid]=={}:
            await telesender.send_message(user,'Todavia no hay tokens disponibles para esta provincia')
            return
        for i in tokens[provinceid]:
            authTokens=authTokens+tokens[provinceid][i]
            print(i)
        url = 'https://api.jsonbin.io/v3/b'
        headers = {
        'Content-Type': 'application/json',
        'X-Master-Key':  master_key
        }
        data = {"authTokens":authTokens,"province":provinceid}

        req = requests.post(url, json=data, headers=headers)
        gentoken=json.loads(req.text)
        print(gentoken)
        id=gentoken['metadata']['id']
        cont=len(authTokens)
        await telesender.send_message(user,f'{cont} tokens agregados')
        await telesender.send_message(user,f'/gettoken {id}')
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/check'))
    async def checkUsers(event):
        user=await event.get_sender()
        chtext=event.text.replace('/check','').strip()
        if chtext=='':
            await telesender.send_message(user,'Este comando no puede estar vacio')
            return
        datas=json.loads(chtext)
        strcorreos='Usuarios con sus cuentas:'
        for userid in tokens[datas['province']]:
            count=0
            for j in tokens[datas['province']][userid]:
                userentity=await telesender.get_entity(PeerUser(userid))
                tokendecoded=jwt.decode(j.replace('JWT ','').strip(),options={'verify_signature':False})
                email=tokendecoded['email']
                if email in datas['users']:
                    if count==0:
                        strcorreos=strcorreos+f"\n {userentity.username} : {email}"
                    else:
                        strcorreos=strcorreos+f", {email}"
                    count+=1
        await telesender.send_message(user,strcorreos)
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/cleanprov'))
    async def clean(event):
        user=await event.get_sender()
        clean=event.text.replace('/cleanprov','').strip()
        if clean=='':
            await telesender.send_message(user,'Limpiando todos los tokens')
            for i in provinces.values():
                tokens[i]={}
        else:
            try:
                prov=int(clean)
                pname=[*provinces][prov]
                provinceid=provinces[pname]
                print(pname,':',provinceid)
                tokens[provinceid]={}
                await telesender.send_message(user,f'Limpiando los tokens de la provincia: {pname}')
            except:
                await telesender.send_message(user,'Mal formato en la solicitud de limpieza de tokens')
                return
    @telesender.on(events.NewMessage(pattern='/code'))
    async def refreshCode(event):
        print('refreshingCode')
        maingroup= await telesender.get_entity(PeerChannel(1315170897))
        
        url='https://todusup1.herokuapp.com/user/products/get'
        url2='https://todusup1.herokuapp.com/user/token'
        user=await event.get_sender()
        userslist=await telesender.get_participants(maingroup)
        usersid=[i.id for i in userslist]
        print(user)        
        if user.id not in usersid:
            return
        if isactiverefcode is False:
            return await telesender.send_message(user,'Aún no se puede solicitar el codigo')
        if user.id in user_with_codes:
            return await telesender.send_message(user,'Ya usted solicito el codigo de hoy')
        response=requests.post(url, json={'id':str(user.id)},headers={'Content-Type':'application/json','Authorization':f'Bearer {AUTH_TOKEN}'})
        print(response.json())
        try:
            print(len(response.json()['products'])==0)
        except:
            await telesender.send_message(user,'Usted no esta registrado en el servidor, solicite el registro a @reservatoken')
        if len(response.json()['products'])==0:
            try:
                response2=requests.post(url2, json={'id':str(user.id)},headers={'Content-Type':'application/json','Authorization':f'Bearer {AUTH_TOKEN}'})
                code=response2.json()['code']
                await telesender.send_message(user,code)
                user_with_codes.append(user.id)
            except:
                await telesender.send_message(user,'Error al obtener código')
        else:
            await telesender.send_message(user,'Usted tiene pagos por confirmar, solicite el código a @reservatoken')
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/cleancode'))
    async def cleanCodeActivate(event):
        global user_with_codes
        user=await event.get_sender()
        print('Act Code')
        user_with_codes=[]
        await telesender.send_message(user,'La lista de códigos fue limpiada con éxito')
        
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/actcode'))
    async def refreshCodeActivate(event):
        global isactiverefcode
        user=await event.get_sender()
        print('Act Code')
        isactiverefcode=True
        await telesender.send_message(user,'Refresh Code esta activado')
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/deactcode'))
    async def refreshCodeDeactivate(event):
        global isactiverefcode
        user=await event.get_sender()
        print('Deact Code')
        isactiverefcode=False
        await telesender.send_message(user,'Refresh Code esta desactivado')
    
    @telesender.on(events.NewMessage(pattern='/pago'))
    async def payMethod(event):
        maingroup= await telesender.get_entity(PeerChannel(1315170897))
        userslist=await telesender.get_participants(maingroup)
        usersid=[i.id for i in userslist] 
        user=await event.get_sender()  
        print(user)
        if user.id not in usersid:
            return        
        return await telesender.send_message(user,'Tarjeta de pago: ```9238-1299-7097-7767```\n Número a confirmar: ```58849746```')
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/cleanchannel'))
    async def cleanChannel(event):
        user=await event.get_sender()
        maingroup= await telesender.get_entity(PeerChannel(1315170897))
        userslist=await telesender.get_participants(maingroup)
        usersid=[i.id for i in userslist]
        url='https://todusup1.herokuapp.com/userid/get'
        response=requests.post(url,headers={'Content-Type':'application/json','Authorization':f'Bearer {AUTH_TOKEN}'})
        usersiddb=response.json()['usersidlist']
        userstodelete=[i for i in usersid if i not in usersiddb]
        print(userstodelete)
        return await telesender.send_message(user,f'{userstodelete}')
        
        
        
        
    await telesender.start(bot_token=bot_key)
    await telesender.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(maintread())

