# -*- coding: utf-8 -*-
# (c) YashDK [yash-dk@github]

from ..consts.ExecVarsSample import ExecVars
from ..core.database_handle import tkdb
from tk import SessionVars
import os

def get_val(variable):
    return SessionVars.get_var(variable)

