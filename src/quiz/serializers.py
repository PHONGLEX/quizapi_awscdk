from rest_framework import serializers
from collections import OrderedDict

from .models import Category, Quiz, Question, Answer
from authentication.models import User


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Answer
        fields = ("id", "answer_text", "is_right", "question_id")


class QuestionSerializer(serializers.ModelSerializer):
    quiz_id = serializers.IntegerField(write_only=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "technique", "difficulty", "title", "is_active", "quiz_id", "answers")

    def get_answers(self, obj):
        if obj.answers.all().exists() and self.context['is_detail']:
            serializer = AnswerSerializer(obj.answers.all(), many=True)
            return serializer.data
        else:
            return None

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class QuizSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ("id", "title", "date_created", "category_id", "questions")

    def get_questions(self, obj):
        if obj.questions.all().exists() and self.context['is_detail']:
            serializer = QuestionSerializer(obj.questions.all(), many=True)
            serializer.context['is_detail'] = True
            return serializer.data
        else:
            return None

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")


class CategorySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    quizzes = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "title", "owner", "quizzes")

    def get_quizzes(self, obj):
        if obj.quizzes.all().exists() and self.context['is_detail']:
            serializer = QuizSerializer(obj.quizzes.all(), many=True)
            serializer.context['is_detail'] = True
            return serializer.data
        else:
            return None

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None]) 

        