from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe

from support_patch.issue import get_customer_details


class FakeCustomer:
	def __init__(self, permitted=None, deny=False):
		self.name = "CUSTOMER-TEST"
		self.permitted_fieldnames = set(permitted or ())
		self.values = {
			"customer_name": "Call 9876543210",
			"sr_customer_id": "CUST-ID",
			"mobile_no": "9876543210",
			"email_id": "patient@example.test",
			"primary_address": "Street Phone 9876543210",
		}
		self.meta = SimpleNamespace(has_field=lambda fieldname: fieldname in self.values)
		self.deny = deny

	def get(self, fieldname):
		return self.values.get(fieldname)

	def check_permission(self, permission):
		if self.deny:
			raise frappe.PermissionError()


class CustomerPrivacyTests(TestCase):
	def test_field_permissions_apply_without_privacy_shield(self):
		customer = FakeCustomer({"customer_name"})
		with (
			patch.object(frappe, "get_doc", return_value=customer),
			patch.object(frappe, "get_installed_apps", return_value=[]),
		):
			result = get_customer_details(customer.name)

		self.assertEqual(result, {
			"name": customer.name,
			"customer_name": "Call 9876543210",
		})
		self.assertNotIn("mobile_no", result)
		self.assertNotIn("email_id", result)
		self.assertNotIn("primary_address", result)
		self.assertNotIn("customer_id", result)

	def test_restricted_response_masks_mobile_name_and_address(self):
		customer = FakeCustomer(customer_field_permissions())
		with (
			patch.object(frappe, "get_doc", return_value=customer),
			patch.object(frappe, "get_installed_apps", return_value=["privacy_shield"]),
			patch(
				"privacy_shield.policy.current_capabilities",
				return_value=SimpleNamespace(view_full=False),
			),
			patch("privacy_shield.address_views.support_address", return_value="Safe Street"),
		):
			result = get_customer_details(customer.name)

		self.assertTrue(result["number_restricted"])
		self.assertEqual(result["mask_mobile"], "******3210")
		self.assertEqual(result["customer_name"], "Call ******3210")
		self.assertEqual(result["primary_address"], "Safe Street")
		self.assertNotIn("mobile_no", result)
		self.assertNotIn("9876543210", str(result))

	def test_full_view_preserves_permitted_values(self):
		customer = FakeCustomer(customer_field_permissions())
		with (
			patch.object(frappe, "get_doc", return_value=customer),
			patch.object(frappe, "get_installed_apps", return_value=["privacy_shield"]),
			patch(
				"privacy_shield.policy.current_capabilities",
				return_value=SimpleNamespace(view_full=True),
			),
		):
			result = get_customer_details(customer.name)

		self.assertEqual(result["mobile_no"], "9876543210")
		self.assertEqual(result["customer_name"], "Call 9876543210")
		self.assertEqual(result["primary_address"], "Street Phone 9876543210")
		self.assertFalse(result["number_restricted"])
		self.assertEqual(result["mask_mobile"], "******3210")

	def test_unreadable_customer_is_denied(self):
		customer = FakeCustomer(customer_field_permissions(), deny=True)
		with patch.object(frappe, "get_doc", return_value=customer):
			with self.assertRaises(frappe.PermissionError):
				get_customer_details(customer.name)


def customer_field_permissions():
	return {"customer_name", "sr_customer_id", "mobile_no", "email_id", "primary_address"}