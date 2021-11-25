from django.db import models

from authentication.models import User


class Category(models.Model):
    owner = models.ForeignKey(User, related_name="categories", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.title


class Quiz(models.Model):
    category = models.ForeignKey(Category, related_name="quizzes", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class QuestionUpdated(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Question(QuestionUpdated):
    SCALE = (
        (0, 'Fundamental'),
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
    )

    TYPE = (
        (0, 'Multiple Choice'),
    )

    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.DO_NOTHING)
    technique = models.IntegerField(choices=SCALE, default=0)
    difficulty = models.IntegerField(choices=TYPE, default=0)
    title = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title


class Answer(QuestionUpdated):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.DO_NOTHING)
    answer_text = models.TextField()
    is_right = models.BooleanField(default=False)