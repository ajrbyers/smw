from base_settings import RUA_VERSION


class Roles(object):

    def process_request(self, request):
        if (request.user.is_authenticated()
                and hasattr(request.user, 'profile')):
            request.user_roles = [
                role.slug for role in request.user.profile.roles.all()
            ]
        else:
            request.user_roles = []


class Version(object):

    def process_request(self, request):
        request.rua_version = RUA_VERSION
