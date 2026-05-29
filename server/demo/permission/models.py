from django.db import models
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

def _user_has_perm(user, perm, obj):
    """
    Backend can raise `PermissionDenied` to short-circuit permission checking.
    """

    for backend in auth.get_backends():
        if not hasattr(backend, "has_perm"): continue
        try:
            if backend.has_perms(user, perm, obj):
                return True
        except PermissionError:
            return False
        return False

def _user_get_permissions(user, obj, from_name):
    permissions = set()
    name = f"get_{from_name}_permissions"
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name))(user, obj)
    return permissions


class PermissionManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, codename, app_label, model):
        return self.get(
            codename=codename,
            content_type=ContentType.object.db_manager(self.db).get_by_natural_key(
                app_label, model       
            ),
        )
    
class Permission(models.Model):
    """_summary_
    The system provides a way to assign permissions to users and group of users

    The permission system  is used by the django site admin,
    he Django admin site uses permissions as follows:

        - The "add" permission limits the user's ability to view the "add" form
          and add an object.
        - The "change" permission limits a user's ability to view the change
          list, view the "change" form and change an object.
        - The "delete" permission limits the ability to delete an object.
        - The "view" permission limits the ability to view an object.

    Args:
        models (_type_): _description_
    """


    name = models.CharField(_("name"), max_length=255)
    content_type = models.ForeignKey(
     ContentType, models.CASCADE,
     verbose_name=_("content-type"),
     related_name="content_type",  
    )

    codename = models.CharField(_("codename"), max_length=100)
    objects = PermissionManager()

    class Meta:
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
        unique_together = [["content_type", "codename"]]
        ordering = ["content_type__app_label", "content_type__model", "codename"]


    def __str__(self):
        return f"{self.content_type} | {self.name}"
    

    def natural_key(self):
        return (self.codename, )+ self.content_type.natural_key()
    
    natural_key.dependencies = ["contenttypes.contenttype"]


class PermissionsMixin(models.Model):
    """
    Add the field and methods necessary to support permissions.
    Args:
        models (_type_): _description_
    """

    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without explicitly assigning them."
        ),
    )

    groups = models.ManyToManyField(
        "account.Group", 
        verbose_name=_("groups"),
        blank=True,
         help_text=_(
            "The groups this user belongs to. A user will get all permissions granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
         verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True

    def get_user_permissions(self, obj=None): 
        return _user_get_permissions(self, obj, "user")
    
    def get_group_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "group")
    
    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "all")
    
    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser: return True
        return _user_has_perm(self, perm, obj)
    

    def has_perm(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)        