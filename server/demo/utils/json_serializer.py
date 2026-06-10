from django.core.serializers.json import DjangoJSONEncoder, Serializer as JsonSerializer


MONEY_TYPE = "Money"

class Serializer(JsonSerializer):
    def _init_options(self):
        super*()._init_options()
        self.json_kwargs["cls"]= CustomJsonEncoder


class CustomJsonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        pass
        # if isinstance(obj, Money):
        #     return {"_type": MONEY_TYPE,"amount": obj.amount, "currency": obj.currency}
        