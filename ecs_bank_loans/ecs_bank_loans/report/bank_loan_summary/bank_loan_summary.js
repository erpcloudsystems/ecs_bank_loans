// Copyright (c) 2016, erpcloud.systems and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank Loan Summary"] = {
	"filters": [
	    {
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"loan_type",
			"label": __("Bank"),
			"fieldtype": "Link",
			"options": "Loan Type"
		}

	]
};
