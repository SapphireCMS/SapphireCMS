from .adapter import adpaters
from .models import models
import os, sys
sys.path.append(os.getcwd())

try:
    import config
except:
    raise ImportError("Could not find a valid SapphireCMS environment")

DATABASE = adpaters[config.active.dbplatform](config.active.db_uri, config.active.dbname, models)