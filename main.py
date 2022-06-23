import datetime
import json
from os import getenv
import asyncio
import jwt
import requests
from telethon import TelegramClient,events
tokens={}
nosleep=True
usersprov={}

master_key=getenv('MASTER_KEY')
bot_key=getenv('BOT_KEY')
api_id =getenv('API_ID')
api_hash = getenv('API_HASH')
province_limits={}
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
for i in provinces.values():
    tokens[i]={}
    usersprov[i]=[]
    province_limits[i]=1
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
        user=await event.get_sender()
        #maingroup=await telesender.get_input_entity(1315170897)#'Venta de Combos tu envío 2.0🤐'
        #print(maingroup)
        print(user)
        ausers=await telesender.get_participants(entity=1315170897)
        usersid=[i.id for i in ausers]
        print(user)
        if user.id==5461780118 or user.id==848517956:
            await telesender.send_message(user,'Comandos:\n /plist  |Muestra la lista de provincias. \n /limit #p #l |Selecciona un limite para una provincia especifica. Sin argumentos muestra los limites. \n /active #p | Activa una provincia especifica. \n /deactive #p | Desactiva una provincia especifica. \n /token #p | Genera el comando para agregar los tokens para una provincia especifica.')
            return
        
        if user.id in usersid:
            print(event.message.text)
            await telesender.send_message(user,'Este es el bot que recibirá los tokens. Estos deben ser enviados cuando se diga en el canal y no deben tener mas de 45 minutos de creados o serán rechazados.')
        print()
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
        global province_limits
        user=await event.get_sender()
        try: 
            texto=event.text.replace('/limit','').strip()
            if texto=='':
                print(province_limits)
                strlimits=''
                count=0
                for i in province_limits:
                    provkey=list(provinces.keys())[list(provinces.values()).index(i)]
                    provlimit=province_limits[i]
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
        except Exception as e:
            print(e)
            await telesender.send_message(user,f'Error en el formato. Correcto: /limit #prov #limit')
        
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/active'))
    async def active(event):
        user=await event.get_sender()
        try:
            pselect=int(event.text.replace('/active','').strip())
        except:
            await telesender.send_message(user,'Error en el codigo de provincia')  
            return         
        print(pselect)
        if 0<=pselect<16:
            pname=[*provinces][pselect]
            provinceid=provinces[pname]
            print(pname,':',provinceid)
            active_province.add(provinceid)
            await telesender.send_message(user,f'Provincia activa: {pname}, id:{provinceid}')
            await telesender.send_message(user,f'Provincias activas:{list(active_province)}')
        else:
            await telesender.send_message(user,f'Fuera del rango de provincias')
        
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/deactive'))
    async def deactive(event):
        user=await event.get_sender()
        try:
            pselect=int(event.text.replace('/deactive','').strip())
        except:
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
            await telesender.send_message(user,f'Fuera del rango de provincias')
        
    @telesender.on(events.NewMessage(pattern='{"province"'))        
    async def startMessage(event):
        ausers=await telesender.get_participants(entity='Venta de Combos tu envío 2.0🤐')
        user=await event.get_sender()
        usersid=[i.id for i in ausers]
        print(usersid)
        if user.id in usersid:
            print(event.message.text)
            try:
                datas=json.loads(event.message.text)
            except:
                print('Error al cargar json')
                await telesender.send_message(user,'Token enviado en mal formato')
                return
            print(active_province)
            provinceid=datas['province']
            if provinceid in active_province:
                print('provincia activa')
                if tokens[provinceid].get(user.id)==None:
                    try:
                        tokendecoded=jwt.decode(datas['token'].strip().replace('JWT ',''),options={'verify_signature':False})                   
                    except:
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
                    else:
                        return await telesender.send_message(user,'Ya envio el límite máximo de token para esta provincia')
                print('Token agregado correctamente')
                await telesender.send_message(user,'Token agregado correctamente') 
            else:
                print('provincia inactiva')
                pname=str(list(provinces.keys())[list(provinces.values()).index(provinceid)])
                await telesender.send_message(user,f'Provincia {pname} inactiva espere a q se anuncie en el grupo la activación de la provincia') 
            
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/token'))        
    async def generateToken(event):
        user=await event.get_sender()
        try:
            prov=int(event.text.replace('/token','').strip())
            pname=[*provinces][prov]
            provinceid=provinces[pname]
            print(pname,':',provinceid)
        except:
            await telesender.send_message(user,f'Mal formato en la solicitud de los tokens')
            return
        authTokens=[]
        if tokens[provinceid]=={}:
            await telesender.send_message(user,f'Todavia no hay tokens disponibles para esta provincia') 
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
    
    @telesender.on(events.NewMessage(from_users=[5461780118,848517956],pattern='/clean'))        
    async def clean(event):
        global tokens
        user=await event.get_sender()        
        clean=event.text.replace('/clean','').strip()
        if clean=='':
            await telesender.send_message(user,f'Limpiando todos los tokens') 
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
                await telesender.send_message(user,f'Mal formato en la solicitud de limpieza de tokens')
                return
                
                   
        
        
    await telesender.start(bot_token=bot_key)    
    await telesender.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(maintread())
