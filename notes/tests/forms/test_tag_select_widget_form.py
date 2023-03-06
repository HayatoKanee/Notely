from django.test import TestCase
from notes.forms import TagSelectWidget
from notes.models import EventTag, PageTag, User
from django.utils.safestring import mark_safe


class TagSelectWidgetTestCase(TestCase):
    fixtures = [
        'notes/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.tag = EventTag.objects.create(user=self.user, title='Tag 1', color="#34eb67")

    def test_select_widget(self):
        widget = TagSelectWidget()
        widget.tag_model = EventTag
        option = widget.create_option('test_name', '2', f'{self.tag.id} &#x25CF', {self.tag.title}, False, 0,
                                      attrs=None)
        self.assertEqual(option['value'], str(self.tag.id))
        self.assertEqual(option['label'], mark_safe(f'&#x25CF  '))
        self.assertEqual(option['attrs']['style'], 'color: #34eb67')

    def test_create_option_with_nonexistent_tag(self):
        widget = TagSelectWidget()
        widget.tag_model = PageTag
        name = 'myfield'
        value = ''
        label = '9999&#x25CFTag1'  # use an ID that does not exist
        selected = False
        index = 0
        attrs = {}
        option = widget.create_option(name, value, label, selected, index, attrs=attrs)
        self.assertEqual(option['label'], '9999&#x25CFTag1')


