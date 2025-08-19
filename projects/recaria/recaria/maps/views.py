# -*- coding: utf-8 -*-
# API fonksiyonlarını backend/api.py'den içe aktar
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.api import health_check, get_geo_data, save_discovery, bulk_save_discoveries, get_player_data
