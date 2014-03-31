from django.test import TestCase
from django.core.urlresolvers import reverse

from lims.models import Apparatus


class ApparatusTests(TestCase):
    def setUp(self):
        Apparatus.objects.get_or_create(name="apparatus1", location="basement")

        self.create_read_url = reverse("lims.views.browse.apparatus")

    def test_browse(self):
        response = self.client.get(self.create_read_url)

        self.assertContains(response, "apparatus1")
