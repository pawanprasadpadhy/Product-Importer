
from django.test import TestCase
from products.models import Product

class ProductModelTest(TestCase):

    def test_product_creation(self):
        """Tests that a Product can be created successfully."""
        product = Product.objects.create(
            sku="TESTSKU1",
            name="Test Product 1",
            description="This is a test product.",
            is_active=True
        )
        self.assertEqual(product.sku, "TESTSKU1")
        self.assertEqual(product.name, "Test Product 1")
        self.assertTrue(product.is_active)

    def test_sku_uppercasing_on_save(self):
        """Tests that the SKU is uppercased automatically on save."""
        product = Product.objects.create(
            sku="testsku2",
            name="Test Product 2"
        )
        self.assertEqual(product.sku, "TESTSKU2")

    def test_unique_sku_enforcement(self):
        """Tests that SKU uniqueness is enforced."""
        Product.objects.create(sku="UNIQUE1", name="Unique Product 1")
        with self.assertRaises(Exception):
            Product.objects.create(sku="UNIQUE1", name="Duplicate Product 1")

    def test_product_update(self):
        """Tests that a Product can be updated successfully."""
        product = Product.objects.create(sku="UPDATE1", name="Old Name")
        product.name = "New Name"
        product.save()
        updated_product = Product.objects.get(sku="UPDATE1")
        self.assertEqual(updated_product.name, "New Name")

    def test_product_deactivation(self):
        """Tests that a Product can be deactivated."""
        product = Product.objects.create(sku="DEACTIVATE1", name="Active Product", is_active=True)
        product.is_active = False
        product.save()
        deactivated_product = Product.objects.get(sku="DEACTIVATE1")
        self.assertFalse(deactivated_product.is_active)
