from django.test import TestCase
from notes.forms import TagImageChoiceField
from notes.models import EventTag, User


class TagImageChoiceFieldTestCase(TestCase):
    fixtures = [
        'notes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        EventTag.objects.create(user=self.user, title='Tag 1', color="#34eb67")

    def test_label_from_instance(self):
        form_field = TagImageChoiceField(queryset=EventTag.objects.all())
        expected_labels = [
            f'{tag.id} &#x25CF {tag.title} ' for tag in EventTag.objects.all()
        ]
        choices = form_field.choices
        self.assertEqual(len(choices), len(expected_labels))
        for choice, expected_label in zip(choices, expected_labels):
            self.assertEqual(choice[1], expected_label)

