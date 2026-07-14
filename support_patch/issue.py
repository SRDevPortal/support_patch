import frappe
from frappe import _
from frappe.utils.html_utils import clean_html


DEPARTMENT_FIELD = "sp_department"
MEDICAL_DEPARTMENT_FIELD = "sp_medical_department"
REQUIRE_MEDICAL_DEPARTMENT_FIELD = "sp_require_medical_department"


def validate_medical_department(doc, method=None):
	"""Normalize and validate the conditional Medical Department selection."""
	if not doc.meta.has_field(DEPARTMENT_FIELD):
		return

	department = doc.get(DEPARTMENT_FIELD)
	medical_department = doc.get(MEDICAL_DEPARTMENT_FIELD)

	if not department:
		if medical_department:
			doc.set(MEDICAL_DEPARTMENT_FIELD, None)
		return

	required = is_medical_department_required(department)
	if not required:
		if medical_department:
			doc.set(MEDICAL_DEPARTMENT_FIELD, None)
		return

	if not medical_department:
		frappe.throw(
			_("Medical Department is required for Department {0}.").format(frappe.bold(department)),
			frappe.MandatoryError,
		)


def is_medical_department_required(department):
	return frappe.db.get_value("Department", department, REQUIRE_MEDICAL_DEPARTMENT_FIELD)


@frappe.whitelist()
def get_customer_details(customer):
	"""Return current primary Customer details after enforcing document read permission."""
	if not customer:
		return {}

	customer_doc = frappe.get_doc("Customer", customer)
	customer_doc.check_permission("read")

	customer_id = customer_doc.get("sr_customer_id") if customer_doc.meta.has_field("sr_customer_id") else None
	primary_address = customer_doc.get("primary_address") or ""

	return {
		"name": customer_doc.name,
		"customer_name": customer_doc.customer_name,
		"customer_id": customer_id,
		"mobile_no": customer_doc.get("mobile_no"),
		"email_id": customer_doc.get("email_id"),
		"primary_address": clean_html(primary_address) if primary_address else "",
	}
