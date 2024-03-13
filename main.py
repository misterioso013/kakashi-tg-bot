""" Script para copiar todas as mensagens de um chat e enviar para outro chat """

import os
import sys
import json
import webbrowser
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

chat_target = int(os.getenv("CHAT_TARGET_ID"))  # Chat que vai receber as mensagens
chat_source = int(os.getenv("CHAT_SOURCE_ID"))  # Chat que vai enviar as mensagens

## Criar um bot que vai copiar todas as mensagens em sequência de um chat e enviar para outro chat
app = Client("my_account", api_id, api_hash)

print("Bot iniciado")


def load_ids():
    """Carregar os ids das mensagens que não foram enviadas"""
    # Verificar se o arquivo list_ids.json existe
    ids = []  # Lista de ids das mensagens: [123, 124, 125]
    allsent = []  # Lista de ids das mensagens enviadas: [123, 124, 125]
    if os.path.exists("list_ids.json"):
        print("Arquivo list_ids.json encontrado")
        # Carregar o arquivo list_ids.json: {messages: { id: 123, sent: true}, { id: 124, sent: false}
        with open("list_ids.json", "r", encoding="utf8") as file:
            get_ids = json.load(file)
            # pegar apenas os ids que não foram enviados
            for id in get_ids["messages"]:
                if not id["sent"]:
                    ids.append(id["id"])
                else:
                    allsent.append(id["id"])
        print(f"Total de mensagens não enviadas: {len(ids)}")
        print(f"Total de mensagens enviadas: {len(allsent)}")
    else:
        print("Arquivo list_ids.json não encontrado")
        print(
            "Envie /send no seu próprio chat para salvar as mensagens no arquivo list_ids.json e enviar para o chat alvo"
        )
        ids = []
    return {"ids": ids, "allsent": allsent, "all": ids + allsent}


ids = load_ids()["ids"]
allsIds = load_ids()["all"]
ids.sort()


@app.on_message(filters.command("send", prefixes="/") & filters.me)
async def send_messages(client, message):
    """Enviar as mensagens para o chat alvo"""
    await message.reply_text("Salvando as mensagens no arquivo list_ids.json")
    chatsourcetitle = await client.get_chat(chat_source)
    print(f"Chat de origem encontrado: {chatsourcetitle.title}")
    # Copiar as mensagem de de trás para frente
    async for msg in client.get_chat_history(chat_source):
        if msg.id not in allsIds:
            print(f"Adicionando {msg.id} na lista de ids")
            ids.append(msg.id)

    with open("list_ids.json", "w", encoding="utf8") as file:
        all_ids = ids + allsIds
        json.dump({"messages": [{"id": id, "sent": False} for id in all_ids]}, file)
    print(f"Total de mensagens: {len(ids)} adicionadas no arquivo list_ids.json")
    chat_target_show = await client.get_chat(chat_target)
    print(f"Chat alvo: {chat_target_show.title}")
    await message.reply_text(
        f"Total de mensagens: {len(ids)} adicionadas no arquivo list_ids.json e prontas para serem enviadas para o chat alvo {chat_target_show.title}\n\nScript criado por @AllDevsBR"
    )
    webbrowser.open("https://projects.all.dev.br")
    # organizar a lista de ids de forma crescente
    for id in ids:
        msg = await client.get_messages(chat_source, id)
        print(f"Enviando {msg.id}")
        await msg.copy(chat_target)
        # Marcar a mensagem como enviada no arquivo list_ids.json
        with open("list_ids.json", "r", encoding="utf8") as file:
            get_ids = json.load(file)
            for id in get_ids["messages"]:
                if id["id"] == msg.id:
                    id["sent"] = True
        with open("list_ids.json", "w", encoding="utf8") as file:
            json.dump(get_ids, file)
        print(f"Mensagem {msg.id} enviada")
        await asyncio.sleep(0.5)
    print("Todas as mensagens foram enviadas")
    await message.reply_text(
        f"Todas as mensagens foram enviadas para o chat alvo {chat_target_show.title}\n\nScript criado por @AllDevsBR"
    )
    webbrowser.open("https://projects.all.dev.br")
    sys.exit()


app.run()
