from functools import partial
from collections.abc import Iterable
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.db.models.expressions import Exists, OuterRef 
from django.db import models
from django.db.models import Q, Value, Index, JSONField
from django.db import connection
from django.forms.models import model_to_dict
from django_countries.fields import Country, CountryField
# from ..app.models import App
from utils.json_serializer import CustomJsonEncoder
from permission.enums import AccountPermissions, BasePermissionEnum, get_permissions
from permission.models import Permission, PermissionsMixin, _user_has_perm


# from demo.permission import 

class ModelWithMetadata(models.Model):
    private_metadata = JSONField(
        blank=True, db_default={}, default=dict, encoder=CustomJsonEncoder
    )
    metadata = JSONField(
        blank=True, db_default={},encoder=CustomJsonEncoder
    )

class AddressQueryset(models.QuerySet["Address"]):
    def annotate_default(self, user):
        # Set default shipping/billing address pk to None
        # if default shipping/billing address doesn't exist
        default_shipping_address_pk, default_billing_address_pk = None, None
        if user.default_shipping_address:
            default_shipping_address_pk = user.default_shipping_address.pk
        if user.default_billing_address:
            default_billing_address_pk = user.default_billing_address.pk

        return user.addresses.annotate(
            user_default_shipping_address_pk=Value(
                default_shipping_address_pk, models.IntegerField()
            ),
            user_default_billing_address_pk=Value(
                default_billing_address_pk, models.IntegerField()
            ),
        )

AddressManager = models.Manager.from_queryset(AddressQueryset)
class Address(models.Model):
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    company_name = models.CharField(max_length=256, blank=True)
    street_address_1 = models.CharField(max_length=256, blank=True)
    street_address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    city_area = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = CountryField()
    country_area = models.CharField(max_length=128, blank=True)
    # phone = PossiblePhoneNumberField(blank=True, default="", db_index=True)
    validation_skipped = models.BooleanField(default=False)

    objects = AddressManager()

    class Meta:
        ordering = ("pk"),
        indexes = []

    def _eq__(self, other):
        if not isinstance(other, Address):
            return False
        return self.as_data() == other.as_data()
    
    __hash__ = models.Model.__hash__

    def as_data(self):
        """
            Return the address as a dict suitable for passing as kwargs.

        Result does not contain the primary key or an associated user.
        """

        data = model_to_dict(self, exclude=["id", "user"])

        if isinstance(data["country"], Country):
            data["country"] = data["country"].code
        if isinstance(data["phone"], PhoneNumber) and not data["validation_skipped"]:
            data["phone"] = data["phone"].as_e164
        return data
    

    def get_copy(self):
        return Address.objects.create(**self.as_data())
    

class UserManager(BaseUserManager["User"]):
    def customer(self):
        pass

    def staff(self):
        return self.get_queryset().filter(is_staff=True)

class User(PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    addresses = models.ManyToManyField(
        Address, blank=True, related_name="user_addresses"
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_confirmed = models.BooleanField(default=True)
    last_confirm_email_request = models.DateTimeField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    last_password_reset_request = models.DateTimeField(null=True, blank=True)
    default_shipping_address = models.ForeignKey(
        Address, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )
    default_billing_address = models.ForeignKey(
        Address, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )
    avatar = models.ImageField(upload_to="user-avatars", blank=True, null=True)
    jwt_token_key = models.CharField(
        max_length=12, default=partial(get_random_string, length=12)
    )
    language_code = models.CharField(
        max_length=35, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE
    )
    # search_vector = SearchVectorField(blank=True, null=True)
    # deprecated field - should be removed in 3.23
    search_document = models.TextField(blank=True, default="")
    uuid = models.UUIDField(default=uuid4, unique=True)

    # Denormalized number of orders placed by the user
    number_of_orders = models.PositiveIntegerField(default=0, db_default=0)

    USERNAME_FIELD = "email"
    NEWLY_CREATED_USER = False


    objects = UserManager()

    class Meta:
        ordering = ("email",)
        permissions = (
            (AccountPermissions.MANAGE_USERS.codename, "Manage customers."),
            (AccountPermissions.MANAGE_STAFF.codename, "Manage staff."),
            (AccountPermissions.IMPERSONATE_USER.codename, "Impersonate user."),
        )
        # TODO model meta data
        indexes = [

        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._effective_permissions = None

    def __str__(self):
        return str(self.uuid)
    
    @property
    def effective_permissions(self) -> models.QuerySet[Permission]:
        if self._effective_permissions is None:
            self._effective_permissions = get_permissions()
            if not self.is_superuser:
                UserPermission = User.user_permissions.through
                user_permission_queryset = UserPermission._default_manager.filter(
                    user_id=self.pk
                    ).values("permission_id")
                
                UserGroup = User.groups.through
                GroupPermission = Group.permissions.through
                user_group_queryset = UserGroup._default_manager.filter(
                    user_id = self.pk
                ).values("group_id")
                group_permission_queryset = GroupPermission.object.filter(
                    Exists(user_group_queryset.filter(group_id=OuterRef("group_id")))
                ).values("permission_id")

                self._effective_permissions = self.__effective_permissions.filter(
                    Q(
                        Exists(user_permission_queryset.filter(permission_id=OuterRef("pk")))
                    )
                    | Q(
                        Exists(group_permission_queryset.filter(permission_id=OuterRef("pk")))
                    )
                )

        return self._effective_permissions
    

    @effective_permissions.setter
    def effective_permissions(self, value: models.QuerySet[Permission]):
        self._effective_permissions = value
        # Dropped cache for authenticate backend
        self._effective_permissions = None


    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        if self.default_billing_address:
            first_name = self.default_billing_address.first_name
            last_name = self.default_billing_address.last_name

            if first_name or last_name:
                return f"{first_name} {last_name}".strip()
        return self.email
    

    def get_short_name(self):
        return self.email
    

    def has_perm(self, perm: BasePermissionEnum |str, obj=None) -> bool:
        perm = perm.value if isinstance(perm, BasePermissionEnum) else perm
        
        if self.is_active and self.is_superuser and not self._effective_permissions: return True

        return _user_has_perm(self, perm, obj)
    

    def can_login(self, site_settings):
        pass


class GroupManager(models.Manager):
    """The manager for auth's Group model."""
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)

class Group(models.Model):
    name = models.CharField("name", max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name="permissions",
        blank=True,
    )
    restricted_access_to_channels = models.BooleanField(default=False)
    # channels = models.ManyToManyField("channel.Channel", blank=True) TODO

    objects = GroupManager()

    class Meta:
        verbose_name = "group"
        verbose_name_plural = "groups"

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)