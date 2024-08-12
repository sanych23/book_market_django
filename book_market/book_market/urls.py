from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from store.views import BookViewSet, UserBookRelationView, auth
from django.conf import settings
# from django.conf.urls import url


router = SimpleRouter()

router.register(r"book", BookViewSet)
router.register(r"book_relation", UserBookRelationView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('auth/', auth),
]

urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
