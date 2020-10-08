from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('songs/metadata/', include('music_metadata.urls')),
]
