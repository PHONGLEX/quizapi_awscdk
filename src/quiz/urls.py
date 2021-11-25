from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.CategoryListCreateAPIView.as_view(), name="categories"),
    path('category/<int:pk>/', views.category_detail, name="category"),
    path('quizzes/', views.QuizListCreateAPIView.as_view(), name="quizzes"),
    path('questions/', views.QuestionListCreateAPIView.as_view(), name="questions"),
    path('answers/', views.AnswerListCreateAPIView.as_view(), name="answers"),
    path('answer/', views.AnswerDetailView.as_view(), name="answer"),
]