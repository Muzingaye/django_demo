from django.conf import settings

class PrimaryReplicaRouter:
    def db_for_wrire(self, module,**hints):
        """Write only the primary connection"""
        return settings.DATABASE_CONNECTION_DEFAULT_NAME
    
    def allow_relation(self, obj, obj2, **hints):
        """ALl relation are allowed as we dont have pool separation."""
        return True