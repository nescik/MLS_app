from django.contrib import admin
from .models import Profile, Team, File, Key, TeamMembership

admin.site.register(Profile)
admin.site.register(Team)
admin.site.register(File)
admin.site.register(Key)
admin.site.register(TeamMembership)