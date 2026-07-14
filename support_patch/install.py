import frappe

from support_patch.setup import setup_custom_fields


def after_install():
	setup_custom_fields()


def after_migrate():
	setup_custom_fields()


def before_tests():
	setup_custom_fields()
	frappe.clear_cache()
