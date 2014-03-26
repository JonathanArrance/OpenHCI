from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import logout
from django.shortcuts import get_object_or_404



def get_object_by_pk_if_permission(user, Ob, pk):
    '''Get Object by pk and check permission for user to view.
    
    Will raise Http404 if object does not exist or if user_can_view fails.
    '''
    o = get_object_or_404(Ob, pk=pk)
    if not o.user_can_view(user):
        raise Http404
    else:
        return o
