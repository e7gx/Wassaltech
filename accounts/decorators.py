from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def user_type_required(allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.account.user_type in allowed_types:
                    return view_func(request, *args, **kwargs)
                else:
                    raise PermissionDenied
            return redirect('login')  # Redirect to login page if user is not authenticated
        return _wrapped_view
    return decorator

# now we can use this decorator like this
# @user_type_required(['freelancer'])
# def my_view(request):
#     return render(request, 'my_view.html')
