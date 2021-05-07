#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telethon import TelegramClient
from tk.core.HandleManager import add_handlers
from tk.core.getVars import get_val
import logging,asyncio
from tk.core.wserver import start_server_async
from pyrogram import Client
try:
    from tk.functions.rstuff import get_rstuff
except ImportError:pass

from tk.ttk_client import tkclient

if __name__ == "__main__":

    #logging stuff
    #thread name is just kept for future use
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s"
    )
    logging.getLogger("pyrogram").setLevel(logging.ERROR)
    
    # parallel connections limiter
    queue = asyncio.Queue()
    for i in range(1,4):
        queue.put_nowait(i)

    # Telethon client creation
    tkbot = tkclient("tkbot",get_val("API_ID"),get_val("API_HASH"))
    tkbot.queue = queue
    tkbot.start(bot_token=get_val("BOT_TOKEN"))
    logging.info("telethon client created.")

    # Pyro Client creation and linking
    pyroclient = Client("pyrosession", api_id=get_val("API_ID"), api_hash=get_val("API_HASH"), bot_token=get_val("BOT_TOKEN"), workers=100)
    pyroclient.start()
    tkbot.pyro = pyroclient
    logging.info("pyrogram client created.")

    # Associate the handlers
    add_handlers(tkbot)

    if get_val("IS_VPS"):
        tkbot.loop.run_until_complete(start_server_async(get_val("SERVPORT")))
    try:
        tkbot.loop.run_until_complete(get_rstuff())
    except:pass
    
    logging.info("LETS GOOO THE BOT WORKS")

    tkbot.run_until_disconnected()
