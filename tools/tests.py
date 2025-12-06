from django.test import TestCase
from .models import Tool, Category, Tag, Submission

class ToolModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.tool = Tool.objects.create(
            name="Test Tool",
            short_description="A tool for testing",
            website="https://example.com",
            category=self.category
        )

    def test_tool_creation(self):
        self.assertEqual(self.tool.name, "Test Tool")
        self.assertEqual(self.tool.short_description, "A tool for testing")
        self.assertEqual(self.tool.website, "https://example.com")
        self.assertEqual(self.tool.category, self.category)

class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Test Category")

class SubmissionModelTest(TestCase):

    def setUp(self):
        self.submission = Submission.objects.create(
            name="Test Submission",
            website="https://example.com",
            description="A submission for testing"
        )

    def test_submission_creation(self):
        self.assertEqual(self.submission.name, "Test Submission")
        self.assertEqual(self.submission.website, "https://example.com")
        self.assertEqual(self.submission.description, "A submission for testing")