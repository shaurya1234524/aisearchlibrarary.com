from django.urls import path
from .views import (ToolListView, image_generation, upvote_tool, CategoryListView, 
                   productivity_tools, marketing_tools, generative_ai, 
                    web_development_tools, video_generation,
                   education_tools, data_analysis_tools, automation_tools,
                   ai_chatbots, privacy_policy)
from tools import views

app_name = 'tools'

urlpatterns = [
    path('', ToolListView.as_view(), name='list'),
    path('<int:pk>/', views.ToolDetailView.as_view(), name='detail'),
    path('upvote/<int:pk>/', upvote_tool, name='upvote'),

    # Category List URL
    path('categories/', CategoryListView.as_view(), name='category_list'),
    
    # Individual Category Pages
    path('productivity-tools/', productivity_tools, name='productivity_tools'),
    path('marketing-tools/', marketing_tools, name='marketing_tools'),
    path('generative_ai/', generative_ai, name='generative_ai'),
    path('image_generation/', image_generation, name='image_generation'),
    path('web-development-tools/', web_development_tools, name='web_development_tools'),
    path('video_generation/', video_generation, name='video_generation'),
    path('education-tools/', education_tools, name='education_tools'),
    path('data-analysis-tools/', data_analysis_tools, name='data_analysis_tools'),
    path('automation-tools/', automation_tools, name='automation_tools'),
    path('ai_chatbots/',ai_chatbots, name='ai_chatbots'),
    path('privacy_policy/',privacy_policy,name='privacy_policy'),
]
