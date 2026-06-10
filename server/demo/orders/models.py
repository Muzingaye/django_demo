from datetime import datetime
import time
import pandas as pd
from decimal import Decimal
from typing import Dict, Any, Optional, Callable, List
from uuid import uuid4

from  django.db.models import QuerySet
from django.db import models, connection
from django.core.cache import cache
from django.conf import settings


from . import (OrderStatus, OrderAuthorizeStatus, OrderChargeStatus, OrderOrigin)


def __get_cache_expiry_datetime(key):
    """
    return cache expiration datetime for key.
    """

    return datetime.now()



def __get_order_number():
    with connection.cursor as c:
        c.execute("SELECT nextval('order_order_number_seq')")
        return c.fetchone()[0]

class Order(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid4))
    number = models.IntegerField(unique=True, default=__get_order_number, editable=False)
    use_old_id = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)
    expired_at = models.DateTimeField(blank=True, null=True)

    status = models.CharField(
        max_length=32, default=OrderStatus.UNFULFILLED, choices=OrderStatus.CHOICES
    )

    authorize_status = models.CharField(
        max_length=32,
        default=OrderAuthorizeStatus.NONE,
        choices=OrderAuthorizeStatus.CHOICES,
        db_index=True,
    )
    charge_status = models.CharField(
        max_length=32,
        default=OrderChargeStatus.NONE,
        choices=OrderChargeStatus.CHOICES,
        db_index=True,
    )
    user = models.ForeignKey(
        "account.User",
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    language_code = models.CharField(
        max_length=35, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE
    )
    tracking_client_id = models.CharField(max_length=36, blank=True, editable=False)
    billing_address = models.ForeignKey(
        "account.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        "account.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    # The flag is only applicable to draft orders and should be null for orders
    # with a status other than `DRAFT`.
    draft_save_billing_address = models.BooleanField(null=True, blank=True)
    draft_save_shipping_address = models.BooleanField(null=True, blank=True)
    user_email = models.EmailField(blank=True, default="")
    original = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
    origin = models.CharField(max_length=32, choices=OrderOrigin.CHOICES)

    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
    )

    shipping_method = models.ForeignKey(
        ShippingMethod,
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    collection_point = models.ForeignKey(
        "warehouse.Warehouse",
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    shipping_method_name = models.CharField(
        max_length=255, null=True, default=None, blank=True, editable=False
    )
    collection_point_name = models.CharField(
        max_length=255, null=True, default=None, blank=True, editable=False
    )

    # channel = models.ForeignKey(
    #     Channel,
    #     related_name="orders",
    #     on_delete=models.PROTECT,
    # )

    
    shipping_price_net_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.0"),
        editable=False,
    )

    # TODO MoneyField cls

    shipping_price_net = models.FloatField()
    # shipping_price_net = MoneyField(
    #     amount_field="shipping_price_net_amount", currency_field="currency"
    # )
    

    shipping_price_gross_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.0"),
        editable=False,
    )
    shipping_price_gross = models.FloatField()
    # # TODO MoneyField cls
    # shipping_price_gross = MoneyField(
    #     amount_field="shipping_price_gross_amount", currency_field="currency"
    # )

    shipping_price = models.FloatField()
    # Price with applied shipping voucher discount
    # shipping_price = TaxedMoneyField(
    #     net_amount_field="shipping_price_net_amount",
    #     gross_amount_field="shipping_price_gross_amount",
    #     currency_field="currency",
    # )
    base_shipping_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.0"),
    )
    # Shipping price with applied shipping voucher discount, without tax
    # base_shipping_price = MoneyField(
    #     amount_field="base_shipping_price_amount", currency_field="currency"
    # )
    # undiscounted_base_shipping_price_amount = models.DecimalField(
    #     max_digits=settings.DEFAULT_MAX_DIGITS,
    #     decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    #     default=Decimal("0.0"),
    # )
    # # Shipping price before applying any discounts
    # undiscounted_base_shipping_price = MoneyField(
    #     amount_field="undiscounted_base_shipping_price_amount",
    #     currency_field="currency",
    # )
    shipping_tax_rate = models.DecimalField(
        max_digits=5, decimal_places=4, blank=True, null=True
    )
    shipping_tax_class = models.ForeignKey(
        "tax.TaxClass",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    shipping_tax_class_name = models.CharField(max_length=255, blank=True, null=True)


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