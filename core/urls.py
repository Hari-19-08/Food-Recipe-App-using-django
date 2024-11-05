from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
from myrecpies.views import*  # Ensure you import your views
from django.urls import path


urlpatterns = [
    path('', home, name='home'),  # Homepage
    path('addrecipe/', add_recipe, name='add_recipe'),  # Add recipe
    path('search/', search, name='search'),  # Search recipes
    path('login_page/', login_page, name='login_page'),  # Login
    path('register/', register, name='register'),  # Register
    path('create_profile/', create_profile, name='create_profile'),  # Create profile
    path('update_profile/<id>/', update_profile, name='update_profile'),  # Update profile
    path('log_out/', log_out, name='log_out'),  # Logout
    path('profile/<id>/', profile, name='profile'),  # User profile
    path('recipe_detail/<id>/', recipe_detail, name='recipe_detail'),  # Recipe detail
    path('delete_recipe/<id>/', delete_recipe, name="delete_recipe"),  # Delete recipe
    path('update_recipe/<id>/', update_recipe, name="update_recipe"),  # Update recipe
    path('viewrecipe/', viewrecipe, name="viewrecipe"),  # View recipe
    path('recipes/', view_recipe_list, name="view_recipe_list"),  # View all recipes (add this line)
    path('admin/', admin.site.urls),  # Admin panel
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
