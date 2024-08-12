from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter, DefaultRouter
from services.views import SuscriptionView
from store.views import BookViewSet, UserBookRelationView, auth
from django.conf import settings


router = SimpleRouter()
router_2 = DefaultRouter()

router.register(r"book", BookViewSet)
router.register(r"book_relation", UserBookRelationView)

router_2.register(r"api/subscriptions", SuscriptionView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('auth/', auth),
]

urlpatterns += router.urls
urlpatterns += router_2.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
