from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import logout
from django.shortcuts import get_object_or_404

def user_matches_company_url(function):
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if not request.user.is_active:
                # The user logged in when he was active and then the is_active
                # flag was set to False.  We need to log him off and not allow
                # him in the site.
                logout(request)
                raise PermissionDenied

            if request.user.profile.company_url != kwargs['company_url']:
                # print the access attempt.  Logging is a better solution.
                print "%s failed url company check %s while trying to access %s" % (request.user.username, kwargs['company_url'], request.META['PATH_INFO'])

                # action could be:
                # 1) return HttpResponseForbidden
                # 2) return render_to_response('units/do-not-have-permission.html', {'user': request.user})
                # 3) raise Http404
                # 4) raise PermissionDenied
                raise PermissionDenied
            else:
                return view_func(request, *args, **kwargs)
        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)

        return _view

def get_object_by_pk_if_permission(user, Ob, pk):
    '''Get Object by pk and check permission for user to view.
    
    Will raise Http404 if object does not exist or if user_can_view fails.
    '''
    o = get_object_or_404(Ob, pk=pk)
    if not o.user_can_view(user):
        raise Http404
    else:
        return o
