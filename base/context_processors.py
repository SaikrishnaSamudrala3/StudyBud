from .models import JoinRequest


def pending_invites(request):
    if not request.user.is_authenticated:
        return {'pending_invites_count': 0}

    return {
        'pending_invites_count': JoinRequest.objects.filter(
            room__host=request.user,
            status=JoinRequest.PENDING,
        ).count()
    }
