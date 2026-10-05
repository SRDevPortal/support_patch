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

	permitted = set(customer_doc.permitted_fieldnames)
	result = {"name": customer_doc.name}
	for fieldname in ("customer_name", "mobile_no", "email_id"):
		if fieldname in permitted:
			result[fieldname] = customer_doc.get(fieldname)
	if customer_doc.meta.has_field("sr_customer_id") and "sr_customer_id" in permitted:
		result["customer_id"] = customer_doc.get("sr_customer_id")
	if "primary_address" in permitted:
		primary_address = customer_doc.get("primary_address") or ""
		result["primary_address"] = clean_html(primary_address) if primary_address else ""

	if "privacy_shield" in frappe.get_installed_apps():
		from privacy_shield.activation import enabled_for
		if enabled_for("support_customer_details"):
			from privacy_shield.policy import current_capabilities
			from privacy_shield.projections import project_numbers
			capabilities = current_capabilities()
			result = project_numbers(result, {"mobile_no": "mask_mobile"}, capabilities.view_full)
			result["number_restricted"] = not capabilities.view_full
			if not capabilities.view_full:
				from privacy_shield.address_views import support_address
				from privacy_shield.display_text import mask_display
				if "customer_name" in result:
					result["customer_name"] = mask_display(result["customer_name"])
				result["primary_address"] = support_address(customer_doc)
	return result
