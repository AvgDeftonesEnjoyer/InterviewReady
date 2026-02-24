"""
Unit tests for Learning Service and Views.
Tests cover question answering, XP earning, and progress tracking.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from learning.models import Topic, Question, AnswerOption, UserProgress
from learning.services import LearningService
from gamification.models import UserProfile

User = get_user_model()


class TestLearningService(TestCase):
    """Test cases for LearningService."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='learner',
            email='learner@example.com',
            password='password123'
        )
        
        self.topic = Topic.objects.create(
            name='Python Basics',
            language='python',
            is_active=True
        )
        
        self.question = Question.objects.create(
            text='What is Python?',
            language='python',
            difficulty='easy',
            topic=self.topic,
            xp_reward=10,
            is_active=True
        )
        
        self.correct_option = AnswerOption.objects.create(
            question=self.question,
            text='A programming language',
            is_correct=True,
            order=1
        )
        
        self.wrong_option = AnswerOption.objects.create(
            question=self.question,
            text='A snake',
            is_correct=False,
            order=2
        )

    def test_submit_answer_correct(self):
        """Test submitting a correct answer."""
        result = LearningService.submit_answer(
            user=self.user,
            question_id=self.question.id,
            option_id=self.correct_option.id
        )
        
        assert result['is_correct'] is True
        assert result['xp_earned'] == 10
        assert UserProgress.objects.filter(
            user=self.user,
            question=self.question,
            is_correct=True
        ).exists()

    def test_submit_answer_incorrect(self):
        """Test submitting an incorrect answer."""
        result = LearningService.submit_answer(
            user=self.user,
            question_id=self.question.id,
            option_id=self.wrong_option.id
        )
        
        assert result['is_correct'] is False
        assert result['xp_earned'] == 0

    def test_user_profile_xp_updated(self):
        """Test that user profile XP is updated on correct answer."""
        LearningService.submit_answer(
            user=self.user,
            question_id=self.question.id,
            option_id=self.correct_option.id
        )
        
        profile = UserProfile.objects.get(user=self.user)
        assert profile.total_xp >= 10

    def test_daily_questions_excludes_answered(self):
        """Test that daily questions exclude already answered questions."""
        # Mark question as answered
        UserProgress.objects.create(
            user=self.user,
            question=self.question,
            is_correct=True,
            xp_earned=10
        )
        
        questions = LearningService.get_daily_questions(self.user)
        
        # The answered question should not be in the results
        assert self.question not in questions

    def test_get_daily_questions_limit(self):
        """Test that daily questions returns maximum 10 questions."""
        # Create 15 questions
        for i in range(15):
            q = Question.objects.create(
                text=f'Question {i}',
                language='python',
                difficulty='easy',
                topic=self.topic,
                is_active=True
            )
            AnswerOption.objects.create(
                question=q,
                text='Answer',
                is_correct=True
            )
        
        questions = LearningService.get_daily_questions(self.user)
        
        assert len(questions) <= 10


class TestAnswerQuestionView(TestCase):
    """Test cases for AnswerQuestionView."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.topic = Topic.objects.create(
            name='Test Topic',
            language='python'
        )
        
        self.question = Question.objects.create(
            text='Test question?',
            language='python',
            difficulty='easy',
            topic=self.topic,
            xp_reward=10,
            is_active=True
        )
        
        self.correct_option = AnswerOption.objects.create(
            question=self.question,
            text='Correct',
            is_correct=True
        )

    def test_answer_question_correct(self):
        """Test answering a question correctly."""
        response = self.client.post('/api/learning/answer/', {
            'question_id': self.question.id,
            'answer_option_id': self.correct_option.id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['is_correct'] is True
        assert data['xp_earned'] == 10

    def test_answer_question_wrong(self):
        """Test answering a question incorrectly."""
        wrong_option = AnswerOption.objects.create(
            question=self.question,
            text='Wrong',
            is_correct=False
        )
        
        response = self.client.post('/api/learning/answer/', {
            'question_id': self.question.id,
            'answer_option_id': wrong_option.id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['is_correct'] is False
        assert data['xp_earned'] == 0

    def test_no_xp_for_repeat_correct_answer_same_day(self):
        """Test that no XP is awarded for answering same question correctly again on same day."""
        # First answer
        self.client.post('/api/learning/answer/', {
            'question_id': self.question.id,
            'answer_option_id': self.correct_option.id
        })
        
        # Second answer (same day)
        response = self.client.post('/api/learning/answer/', {
            'question_id': self.question.id,
            'answer_option_id': self.correct_option.id
        })
        
        data = response.json()
        assert data['is_correct'] is True
        assert data['xp_earned'] == 0  # No XP for repeat
        assert data['previously_answered'] is True

    def test_invalid_question_id(self):
        """Test answering with invalid question ID."""
        response = self.client.post('/api/learning/answer/', {
            'question_id': 99999,
            'answer_option_id': 1
        })
        
        assert response.status_code == 404

    def test_missing_required_fields(self):
        """Test answering with missing required fields."""
        response = self.client.post('/api/learning/answer/', {})
        
        assert response.status_code == 400


class TestTopicProgress(TestCase):
    """Test topic progress calculation."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='progressuser',
            email='progress@example.com',
            password='password123'
        )
        
        self.topic = Topic.objects.create(
            name='Progress Topic',
            language='python'
        )
        
        # Create 5 questions
        self.questions = []
        for i in range(5):
            q = Question.objects.create(
                text=f'Question {i}',
                language='python',
                difficulty='easy',
                topic=self.topic,
                xp_reward=10,
                is_active=True
            )
            AnswerOption.objects.create(
                question=q,
                text='Answer',
                is_correct=True
            )
            self.questions.append(q)

    def test_topic_progress_calculation(self):
        """Test that topic progress is calculated correctly."""
        # Answer 2 questions correctly
        for q in self.questions[:2]:
            option = q.options.first()
            UserProgress.objects.create(
                user=self.user,
                question=q,
                is_correct=True,
                xp_earned=10
            )
        
        # Calculate progress
        total_q = self.topic.questions.count()
        done_q = UserProgress.objects.filter(
            user=self.user,
            question__topic=self.topic,
            is_correct=True
        ).values('question').distinct().count()
        
        progress = round((done_q / total_q) * 100) if total_q else 0
        
        assert total_q == 5
        assert done_q == 2
        assert progress == 40
