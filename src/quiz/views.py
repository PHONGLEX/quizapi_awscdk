from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse

from rest_framework import generics, status, pagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Category, Quiz, Question, Answer
from .serializers import CategorySerializer, QuizSerializer, QuestionSerializer, AnswerSerializer


class QuizPagination(pagination.PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_query_param = "p"
    pgge_size_query_param = "count"


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    pagination_class = QuizPagination

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serializer = CategorySerializer(category)
    serializer.context['is_detail'] = True
    return Response(serializer.data, status=status.HTTP_200_OK)


class QuizListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Quiz.objects.all()
    pagination_class = QuizPagination


class QuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Question.objects.all()
    pagination_class = QuizPagination


class AnswerListCreateAPIView(APIView):
    serializer_class = AnswerSerializer
    permission_classes = (IsAuthenticated,)

    count = openapi.Parameter("page size", openapi.IN_QUERY, description="page size", type=openapi.TYPE_INTEGER)
    p = openapi.Parameter("page number", openapi.IN_QUERY, description="page number", type=openapi.TYPE_INTEGER)    

    @swagger_auto_schema(manual_parameters=[count, p])
    def get(self, request):
        answers = Answer.objects.all()
        count = request.GET.get('page size', 100)
        p = request.GET.get('page number', 1)
        paginator = Paginator(answers, count)
        return JsonResponse(list(paginator.page(p).object_list.values()), safe=False, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AnswerSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnswerDetailView(APIView):
    serializer_class = AnswerSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = self.serializer_class(answer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AnswerSerializer)
    def put(self, request, pk, format=None):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = self.serializer_class(answer, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk, format=None):
        answer = get_object_or_404(Answer, pk=pk)
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
