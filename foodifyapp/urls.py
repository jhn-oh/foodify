"""
URL configuration for foodify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from foodifyapp import views


urlpatterns = [
    path('home/', views.homepage),
    path('about/', views.about),
    path('about/team', views.about_team),
    path('about/project', views.about_project),
    path('login/', views.LoginView.as_view(), name='login'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register),
    path('register_success/', views.register_success),
    path('survey/', views.survey),
    path('survey_info/', views.survey_info),
    path('survey/<int:survey_food_id>/', views.survey_food),
    path('survey/<int:survey_food_id>/<str:pref>', views.survey_upload),
    path('survey/spicy/', views.survey_spicy),
    path('survey/vegeterian/', views.survey_vegeterian),
    path('survey/hindu/', views.survey_hindu),
    path('survey/islam/', views.survey_islam),
    path('survey/spicy/<max_spicy>', views.survey_spicy_max),
    path('survey/<taboo>/<answer>', views.survey_taboo_answer),
    path('survey/complete', views.survey_complete),
    path('homeroom/', views.homeroom),
    path('food_random/', views.food_random),
    path('food_random/<recommended_food_id>', views.food_random2),
    path('answer/<id>/', views.answer),
    path('recommend/', views.recommend),
    path('recommend/<recommended_food_id>', views.recommend2),
    path('more/<int:recommended_food_id>', views.more),
    path('dislike/<recommendation_type>/<recommended_food_id>', views.dislike),
    path('terms/', views.terms),
    path('privacy/', views.privacy),
    path('desire/', views.desire_flavor),
    path('desire/<flavor>', views.desire_origin),
    path('desire/<flavor>/<origin>', views.desire_recommendation),
    #path('model_upload/', views.model_upload),
    #path('model_clear/', views.model_clear),
    path('', views.homepage),
    path('more/', views.more),
]
