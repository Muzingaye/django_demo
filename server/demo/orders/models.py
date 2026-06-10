from datetime import datetime
import time
import pandas as pd

from typing import Dict, Any, Optional, Callable, List

from  django.db.models import QuerySet
from django.db import models, connection
from django.core.cache import cache

CACHE = {}


def __get_cache_expiry_datetime(key):
    """
    return cache expiration datetime for key.
    """

    return datetime.now()

class Order(models.Model):
    def __init__(self):
        pass
    
    @classmethod
    def __get_cache_expiry_datetime(cls):
        pass


    @classmethod
    def __insert_cache_data(cls, key, cache_dt, cache_duration, func):
        pass


    @classmethod
    def _fetch_data_cache(cls, refresh: bool, startup: bool, force_reload: bool, key: str, 
                         stale_key: str, sql: str, params=None, cache_timeout: int = 300, stale_cache_timeout: int = 3600, 
                         system_cache_tolerance: int = 10, retry_wait: float = 0.05, retry_count: int = 0, max_retries: int = 3):
       
        active_cache_flag = f"{key}:lock"

        
        stale_data = cache.get(stale_key)

        if not refresh and not startup and not force_reload:
            if stale_data:
                return stale_data

     
        if cache.get(active_cache_flag):
            time.sleep(retry_wait)
            return cache.get(key) or stale_data

        cached_data = cache.get(key)

        if cached_data and not refresh and not force_reload:
            return cached_data

        try:
            cache.set(active_cache_flag, True, timeout=30)

        
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            cache.set(key, data, timeout=cache_timeout)

        
            if data:
                cache.set(stale_key, data, timeout=stale_cache_timeout)
            elif stale_data:
                data = stale_data
                cache.set(key, data, timeout=cache_timeout)

            return data

        except Exception as e:
            retry_count += 1

            if retry_count <= max_retries:
                time.sleep(retry_wait)
                cache.delete(active_cache_flag)
                return cls.fetch_data_cache(refresh, startup, force_reload, key, stale_key, sql, params,
                                             cache_timeout, stale_cache_timeout, system_cache_tolerance,
                                               retry_wait, retry_count, max_retries)

            # raise

        finally:
            cache.delete(active_cache_flag)