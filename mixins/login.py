from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.shortcuts import redirect
from django.contrib.auth.views import redirect_to_login
from course_apps.course_post.models import Post


class LoginRequireMixin(AccessMixin):
    def handle_no_permission(self):

        ''' handle the user that not login '''

        message = self.get_permission_denied_message()
        messages.warning(self.request, message)
        return redirect('/')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.handle_no_permission()

        return super(LoginRequireMixin, self).dispatch(
            request, *args, **kwargs)


class OwnerCheckMixin(AccessMixin):

    # 待確認的 model, ex: Post
    model = ''

    def handle_no_permission(self):
        message = self.get_permission_denied_message()
        messages.warning(self.request, message)
        return redirect('/')

    def dispatch(self, request, *args, **kwargs):
        model = self.model
        if request.method == 'PUT':
            # ex: post_id, course_id
            id_name = model.__name__.lower() + '_id'
            p = model.objects.get(id=kwargs[id_name])
            if p.user.id != request.user.id:
                return self.handle_no_permission()
        return super(OwnerCheckMixin, self).dispatch(
            request, *args, **kwargs)


class ActiveOnlyMixin(AccessMixin):

    '''
    A view mixin that only allows users that are active on the site.
    '''

    permission_denied_message = ''
    not_activated_message = ''
    not_activated_redirect = ''

    def get_not_activated_message(self):
        return self.not_activated_message

    def handle_not_activated(self):

        ''' Deal with users that are logged in but not activated yet. '''

        message = self.get_not_activated_message()
        if self.raise_exception:
            raise PermissionDenied(message)
        messages.error(self.request, message)
        return redirect(self.get_not_activated_redirect())

    def get_not_activated_redirect(self):

        ''' Get the url name to redirect to if the user isn't activated. '''

        if not self.not_activated_redirect:
            raise ImproperlyConfigured(
                '{0} is missing the not_activated_redirect attribute. Define {0}.not_activated_redirect, or override '
                '{0}.get_not_activated_redirect().'.format(self.__class__.__name__))
        return self.not_activated_redirect

    def handle_no_permission(self):

        ''' Overwrite to allow a message to be sent. '''

        message = self.get_permission_denied_message()
        if self.raise_exception:
            raise PermissionDenied(message)
        messages.error(self.request, message)
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name())

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.handle_no_permission()
        if not request.user.is_active:
            return self.handle_not_activated()
        return super(ActiveOnlyMixin, self).dispatch(request, *args, **kwargs)
