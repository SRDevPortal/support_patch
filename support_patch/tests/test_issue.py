from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from support_patch.issue import validate_medical_department


class TestIssueDepartmentValidation(FrappeTestCase):
	def make_issue(self, department=None, medical_department=None):
		return frappe.get_doc(
			{
				"doctype": "Issue",
				"subject": "Support Patch validation test",
				"sp_department": department,
				"sp_medical_department": medical_department,
			}
		)

	def test_issue_without_department_remains_compatible(self):
		issue = self.make_issue()
		validate_medical_department(issue)
		self.assertIsNone(issue.sp_department)

	@patch("support_patch.issue.is_medical_department_required", return_value=1)
	def test_configured_department_requires_medical_department(self, _get_value):
		issue = self.make_issue(department="Support")

		with self.assertRaises(frappe.MandatoryError):
			validate_medical_department(issue)

	@patch("support_patch.issue.is_medical_department_required", return_value=1)
	def test_configured_department_accepts_medical_department(self, _get_value):
		issue = self.make_issue(department="Support", medical_department="General")
		validate_medical_department(issue)
		self.assertEqual(issue.sp_medical_department, "General")

	@patch("support_patch.issue.is_medical_department_required", return_value=0)
	def test_unconfigured_department_clears_medical_department(self, _get_value):
		issue = self.make_issue(department="Support", medical_department="General")
		validate_medical_department(issue)
		self.assertIsNone(issue.sp_medical_department)
