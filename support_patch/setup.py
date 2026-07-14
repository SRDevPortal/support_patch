import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


CUSTOM_FIELDS = {
	"Department": [
		{
			"fieldname": "sp_require_medical_department",
			"label": "Require Medical Department on Issues",
			"fieldtype": "Check",
			"insert_after": "disabled",
			"default": "0",
			"description": "Require a Medical Department when this Department is selected on an Issue.",
		},
	],
	"Issue": [
		{
			"fieldname": "sp_customer_details_html",
			"label": "Customer Details",
			"fieldtype": "HTML",
			"insert_after": "customer",
			"depends_on": "eval:doc.customer",
		},
		{
			"fieldname": "sp_department",
			"label": "Department",
			"fieldtype": "Link",
			"options": "Department",
			"insert_after": "issue_type",
			"in_standard_filter": 1,
			"search_index": 1,
		},
		{
			"fieldname": "sp_medical_department",
			"label": "Medical Department",
			"fieldtype": "Link",
			"options": "Medical Department",
			"insert_after": "sp_department",
			"hidden": 1,
			"in_standard_filter": 1,
			"search_index": 1,
		},
	],
}


def setup_custom_fields():
	"""Create or update the app's custom fields safely on every migration."""
	for fields in CUSTOM_FIELDS.values():
		for field in fields:
			field.setdefault("module", "Support Patch")

	create_custom_fields(CUSTOM_FIELDS, update=True)
	frappe.clear_cache(doctype="Department")
	frappe.clear_cache(doctype="Issue")
