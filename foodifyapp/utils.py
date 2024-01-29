from .models import UserProfile

def get_user_profile(request):
    return UserProfile.objects.get(user=request.user)