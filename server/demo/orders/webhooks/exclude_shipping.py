import json
import logging
from typing import TYPE_CHECKING, Union

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from ...account.models import User
    from ...orders.models import Order

    
def generate_excluded_shipping_methods_for_order_payload(
    order: "Order", available_shipping_methods: list[ShippingMethodData]
): 
    pass
    # order_data = json.loads(generate_order_payload(order))[0]
    # payload = {
    #     "order": order_data,
    #     "shipping_methods": [
    #         generate_payload_for_shipping_method(shipping_method)
    #         for shipping_method in available_shipping_methods 
    #     ]
    # }
    # return json.dumps(payload, cls=CustomJsonEncoder)