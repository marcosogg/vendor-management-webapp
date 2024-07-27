from django.test import TestCase
from django.urls import reverse
from .models import Vendor, Part, Spend, Risk

class VendorModelTest(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(
            vendor_name="Test Vendor",
            vendor_id="TV001",
            payment_terms="Net 30",
            credit_limit=10000,
            contract_year=2023,
            relationship_type="STRATEGIC"
        )

    def test_vendor_creation(self):
        self.assertTrue(isinstance(self.vendor, Vendor))
        self.assertEqual(self.vendor.__str__(), "Test Vendor (TV001)")

class VendorListViewTest(TestCase):
    def setUp(self):
        Vendor.objects.create(
            vendor_name="Vendor 1",
            vendor_id="V001",
            payment_terms="Net 30",
            credit_limit=10000,
            contract_year=2023,
            relationship_type="STRATEGIC"
        )
        Vendor.objects.create(
            vendor_name="Vendor 2",
            vendor_id="V002",
            payment_terms="Net 60",
            credit_limit=20000,
            contract_year=2023,
            relationship_type="PREFERRED"
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/vendors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('vendor_list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('vendor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/vendor_list.html')

    def test_search_functionality(self):
        response = self.client.get(reverse('vendor_list'), {'search': 'Vendor 1'})
        self.assertContains(response, 'Vendor 1')
        self.assertNotContains(response, 'Vendor 2')
