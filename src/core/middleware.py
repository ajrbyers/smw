
class Roles(object):
    def process_request(self, request):
        try:
            if not request.user.is_anonymous():
                request.user_roles = [role.slug for role in request.user.profile.roles.all()]
            else:
                request.user_roles = []
        except:
            request.user_roles = []
