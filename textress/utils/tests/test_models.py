from django.test import TestCase

from model_mommy import mommy

from utils.models import Tester


class TesterTests(TestCase):

    def test_delete(self):
        obj = mommy.make(Tester)
        self.assertFalse(obj.hidden)
        obj.delete()
        self.assertTrue(obj.hidden)

    def test_delete_override(self):
        obj = mommy.make(Tester)
        self.assertFalse(obj.hidden)
        obj.delete(override=True)
        with self.assertRaises(Tester.DoesNotExist):
            Tester.objects.get(id=obj.id)

    def test_delete_query_with_all(self):
        obj = mommy.make(Tester)
        obj.delete()
        self.assertEqual(Tester.objects.archived().count(), 1)
        self.assertEqual(Tester.objects.current().count(), 0)
