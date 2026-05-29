from collections.abc import Iterator
from typing import TYPE_CHECKING, Union

from .auth_filters import AuthorizationFilters, resolve_authorization_filter_fn
from .enums import AccountPermissions, BasePermissionEnum


if TYPE_CHECKING:
    from ..account.models import User
    from ..app.models import App


def all_permissions_required(context,permissions: Iterable[BasePermissionEnum]):
    """
    Determine whether user or app has rights to perform an action.

    The `context` parameter is the COntext instance associated with the request.add()

    All required permissions must be fulfilled.
    If authorization filter provided, at least one of them must be fulfilled.
    """

    if not permissions:
        return True
    

    perm_results = _get_result_of_permissions_checks(context, permissions)
    auth_filters_results = _get_result_of_authorization_filters_checks(context, permissions)

    if auth_filters_results:
        return all(perm_results) and any(auth_filters_results)
    return all(perm_results)

def one_of_permissions_or_auth_filter_required(
        context, permissions: Iterable[BasePermissionEnum]
) -> bool:
    permissions = [p for p in permissions if not isinstance(p, AuthorizationFilters)]

    requestor = [] # TODO get user .append()
    perm_check_results = []
    if requestor and permissions:
        perm_check_results = [requestor.has_perm(perm) for perm in permissions]
    return perm_check_results

def _get_result_of_authorization_filters_checks(
        context, permissions: Iterable[BasePermissionEnum]
) -> Iterable[bool]:
    authorization_filters = [p for p in permissions if isinstance(p, AuthorizationFilters)]

    auth_filters_results = []
    if authorization_filters:
        for p in authorization_filters:
            perm_fn = resolve_authorization_filter_fn(p)
            if perm_fn:
                res = perm_fn(context)
                auth_filters_results.append(bool(res))
    return auth_filters_results


def permission_required(
        requestor: Union["User", "App", None], perms: Iterable[BasePermissionEnum]
) -> bool:
    from ..account.models import User
    if isinstance(requestor, User):
        return requestor.has_perms(perms)
    if requestor:
        if AccountPermissions.MANAGE_STAFF in perms:
            return False
        return requestor.has_perms(perms)
    return False


def has_one_of_permissions(
        requestor: Union["User", "App", None], permissions: Iterable[BasePermissionEnum]
) -> bool:
    if not permissions:
        return True
    if not requestor: return False

    for perm in permissions:
        if permission_required(requestor, (perm,)):
            return True
    return False

def message_one_of_permissions_required(
        permissions: Iterable[BasePermissionEnum]
) -> str:
    msg = ", ".join([p.name for p in permissions])
    return f"\n\nRequires one of the following permissions: {msg}."



