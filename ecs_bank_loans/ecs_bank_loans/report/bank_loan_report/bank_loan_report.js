// Copyright (c) 2016, erpcloud.systems and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank Loan Report"] = {
	"filters": [
	    {
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",

		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",

		},
		{
			"fieldname":"loan_type",
			"label": __("Bank"),
			"fieldtype": "Link",
			"options": "Loan Type"
		}

	]
};
