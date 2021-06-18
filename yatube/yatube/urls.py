from django.contrib import admin
from django.urls import include, path

import posts.views as posts

urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
    path('group/<slug>/', posts.group_posts, name='group'),
]
