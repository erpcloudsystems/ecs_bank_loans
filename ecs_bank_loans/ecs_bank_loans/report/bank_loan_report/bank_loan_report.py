# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns=get_columns()
	data=get_data(filters,columns)
	return columns, data

def get_columns():
	return [
		{
			"label": _("Loan"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Bank Loan",
			"width": 120
		},
		{
			"label": _("Provider Bank"),
			"fieldname": "loan_type",
			"fieldtype": "Link",
			"options": "Loan Type",
			"width": 120
		},
		{
			"label": _("Drawn Bank"),
			"fieldname": "bank_account",
			"fieldtype": "Link",
			"options": "Bank",
			"width": 100
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Loan Amount"),
			"fieldname": "loan_amount",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Start Date"),
			"fieldname": "repayment_start_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Payment Freq"),
			"fieldname": "payment_frequency",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Repayment Amount"),
			"fieldname": "repayment_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Rate Of Interest %"),
			"fieldname": "rate_of_interest",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Periods / Paid"),
			"fieldname": "periods_paid",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Administrative Expenses Amount"),
			"fieldname": "administrative_expenses_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Principal Payable"),
			"fieldname": "total_principal_payable",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Principal Paid"),
			"fieldname": "total_principal_paid",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Interest Payable"),
			"fieldname": "total_interest_payable",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Interest Paid"),
			"fieldname": "total_interest_paid",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Payable Amount"),
			"fieldname": "total_payment",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Amount Paid"),
			"fieldname": "total_amount_paid",
			"fieldtype": "Currency",
			"width": 120
		}

	]

def get_data(filters, columns):
	item_price_qty_data = []
	item_price_qty_data = get_item_price_qty_data(filters)
	return item_price_qty_data

def get_item_price_qty_data(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += " and a.posting_date>=%(from_date)s"
	if filters.get("to_date"):
		conditions += " and a.posting_date<=%(to_date)s"
	if filters.get("loan_type"):
		conditions += " and a.loan_type=%(loan_type)s"
	item_results = frappe.db.sql("""
				select
					a.name as name,
					a.loan_type as loan_type,
					a.bank_account as bank_account,
					a.status as status,
					a.loan_amount as loan_amount,
					a.posting_date as posting_date,
					a.repayment_start_date as repayment_start_date,
					a.payment_frequency as payment_frequency,
					a.repayment_amount as repayment_amount,
					a.rate_of_interest as rate_of_interest,
					a.administrative_expenses_amount as administrative_expenses_amount,
					a.total_principal_payable as total_principal_payable,
					a.total_principal_paid as total_principal_paid,
					a.total_interest_payable as total_interest_payable,
					a.total_interest_paid as total_interest_paid,
					a.total_payment as total_payment,
					CONCAT_WS(" / ",a.no_of_repayments,  (select count(name) from `tabBank Loan Repayment Schedule` b where b.parent = a.name and b.is_paid =1)) as periods_paid,
					a.total_amount_paid as total_amount_paid
					from `tabBank Loan` a 
				where
					docstatus =1
					{conditions}
		"""
		.format(conditions=conditions), filters, as_dict=1)

	#price_list_names = list(set([item.price_list_name for item in item_results]))

	#buying_price_map = get_price_map(price_list_names, buying=1)
	#selling_price_map = get_price_map(price_list_names, selling=1)

	result = []
	if item_results:
		for item_dict in item_results:
			data = {
				'name': item_dict.name,
				'loan_type': item_dict.loan_type,
				'bank_account': item_dict.bank_account,
				'status': item_dict.status,
				'loan_amount': item_dict.loan_amount,
				'posting_date': item_dict.posting_date,
				'repayment_start_date': item_dict.repayment_start_date,
				'payment_frequency': item_dict.payment_frequency,
				'repayment_amount': item_dict.repayment_amount,
				'rate_of_interest': item_dict.rate_of_interest,
				'administrative_expenses_amount': item_dict.administrative_expenses_amount,
				'total_principal_payable': item_dict.total_principal_payable,
				'total_principal_paid': item_dict.total_principal_paid,
				'total_interest_payable': item_dict.total_interest_payable,
				'total_interest_paid': item_dict.total_interest_paid,
				'total_payment': item_dict.total_payment,
				'periods_paid': item_dict.periods_paid,
				'total_amount_paid': item_dict.total_amount_paid,
			}
			result.append(data)

	return result

def get_price_map(price_list_names, buying=0, selling=0):
	price_map = {}

	if not price_list_names:
		return price_map

	rate_key = "Buying Rate" if buying else "Selling Rate"
	price_list_key = "Buying Price List" if buying else "Selling Price List"

	filters = {"name": ("in", price_list_names)}
	if buying:
		filters["buying"] = 1
	else:
		filters["selling"] = 1

	pricing_details = frappe.get_all("Item Price",
		fields = ["name", "price_list", "price_list_rate"], filters=filters)

	for d in pricing_details:
		name = d["name"]
		price_map[name] = {
			price_list_key :d["price_list"],
			rate_key :d["price_list_rate"]
		}

	return price_map


