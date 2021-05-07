#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = "1.0.1"
__author__ = "reaitten@github"

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(),logging.FileHandler("tk_logs.txt")]
)

from tk.core.wserver import start_server
from .core.database_handle import tkupload, tkdb, tktorrents, userdb
from .core.varholdern import VarHolder
import time

logging.info("Database created")
upload_db = tkupload()
var_db = tkdb()
tor_db = tktorrents()
user_db = userdb()

uptime = time.time()
to_del = []
SessionVars = VarHolder(var_db)