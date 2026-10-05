const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const context = {
	__: value => value,
	frappe: {
		ui: {form: {on() {}}},
		utils: {
			escape_html(value) {
				return String(value)
					.replaceAll("&", "&amp;")
					.replaceAll("<", "&lt;")
					.replaceAll(">", "&gt;")
					.replaceAll('"', "&quot;");
			},
		},
	},
};
vm.createContext(context);
const source = fs.readFileSync(path.join(__dirname, "../public/js/issue.js"), "utf8");
vm.runInContext(source, context);

const card = context.build_customer_card({
	name: "CUSTOMER/TEST",
	customer_name: "Patient <script>alert(1)</script>",
	mobile_no: "9876543210",
	mask_mobile: "******3210",
	number_restricted: true,
	primary_address: "Safe Street",
});

assert.match(card, /\*\*\*\*\*\*3210/);
assert.doesNotMatch(card, />9876543210</);
assert.doesNotMatch(card, /<script>/);
assert.match(card, /Patient &lt;script&gt;alert\(1\)&lt;\/script&gt;/);
assert.match(card, /\/app\/customer\/CUSTOMER%2FTEST/);

const fullViewCard = context.build_customer_card({
	name: "CUSTOMER-TEST",
	customer_name: "Full View",
	mobile_no: "9876543210",
	mask_mobile: "******3210",
	number_restricted: false,
});
assert.match(fullViewCard, />9876543210</);
console.log("Support customer privacy UI checks passed: mask precedence, escaping, encoded route.");