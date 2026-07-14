const SUPPORT_PATCH_FIELDS = {
	department: "sp_department",
	medical_department: "sp_medical_department",
	customer_details: "sp_customer_details_html",
};

frappe.ui.form.on("Issue", {
	setup(frm) {
		frm.set_query(SUPPORT_PATCH_FIELDS.department, () => ({
			filters: {
				disabled: 0,
				is_group: 0,
			},
		}));
	},

	refresh(frm) {
		// Required in Desk only. The Custom Field remains optional for email/API-created Issues.
		frm.toggle_reqd(SUPPORT_PATCH_FIELDS.department, true);
		update_medical_department_rule(frm);
		render_customer_details(frm);
	},

	sp_department(frm) {
		update_medical_department_rule(frm);
	},

	customer(frm) {
		render_customer_details(frm);
	},
});

async function update_medical_department_rule(frm) {
	const department = frm.doc[SUPPORT_PATCH_FIELDS.department];
	frm.__support_patch_department_request = department || null;

	if (!department) {
		await apply_medical_department_rule(frm, false);
		return;
	}

	const response = await frappe.db.get_value(
		"Department",
		department,
		"sp_require_medical_department"
	);

	if (
		frm.__support_patch_department_request !== department ||
		frm.doc[SUPPORT_PATCH_FIELDS.department] !== department
	) {
		return;
	}

	await apply_medical_department_rule(
		frm,
		Boolean(response.message && response.message.sp_require_medical_department)
	);
}

async function apply_medical_department_rule(frm, required) {
	frm.toggle_display(SUPPORT_PATCH_FIELDS.medical_department, required);
	frm.toggle_reqd(SUPPORT_PATCH_FIELDS.medical_department, required);

	if (!required && frm.doc[SUPPORT_PATCH_FIELDS.medical_department]) {
		await frm.set_value(SUPPORT_PATCH_FIELDS.medical_department, null);
	}
}

async function render_customer_details(frm) {
	const field = frm.fields_dict[SUPPORT_PATCH_FIELDS.customer_details];
	if (!field) {
		return;
	}

	const customer = frm.doc.customer;
	frm.__support_patch_customer_request = customer || null;

	if (!customer) {
		field.$wrapper.empty();
		frm.toggle_display(SUPPORT_PATCH_FIELDS.customer_details, false);
		return;
	}

	frm.toggle_display(SUPPORT_PATCH_FIELDS.customer_details, true);
	field.$wrapper.html(`<div class="text-muted small">${__("Loading customer details...")}</div>`);

	try {
		const response = await frappe.call({
			method: "support_patch.issue.get_customer_details",
			args: { customer },
		});

		if (
			frm.__support_patch_customer_request !== customer ||
			frm.doc.customer !== customer
		) {
			return;
		}

		field.$wrapper.html(build_customer_card(response.message || {}));
	} catch (error) {
		if (frm.__support_patch_customer_request === customer) {
			field.$wrapper.empty();
			frm.toggle_display(SUPPORT_PATCH_FIELDS.customer_details, false);
		}
	}
}

function build_customer_card(details) {
	const escape = (value) => frappe.utils.escape_html(String(value || ""));
	const rows = [];

	if (details.customer_id) {
		rows.push(detail_row(__("Customer ID"), escape(details.customer_id)));
	}
	if (details.mobile_no) {
		rows.push(detail_row(__("Phone"), escape(details.mobile_no)));
	}
	if (details.email_id) {
		rows.push(detail_row(__("Email"), escape(details.email_id)));
	}
	if (details.primary_address) {
		rows.push(detail_row(__("Address"), details.primary_address));
	}

	const route = `/app/customer/${encodeURIComponent(details.name || "")}`;
	const title = escape(details.customer_name || details.name || __("Customer"));

	return `
		<div class="border rounded p-3 mb-3 support-patch-customer-card">
			<div class="mb-2">
				<a class="font-weight-bold" href="${route}">${title}</a>
			</div>
			${rows.join("")}
		</div>
	`;
}

function detail_row(label, value) {
	return `
		<div class="row small mb-1">
			<div class="col-sm-3 text-muted">${frappe.utils.escape_html(label)}</div>
			<div class="col-sm-9">${value}</div>
		</div>
	`;
}
