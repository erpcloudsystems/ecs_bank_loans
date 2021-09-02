# Copyright (c) 2021, erpcloud.systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.model.document import Document
from frappe import _
from frappe.desk.search import sanitize_searchfield
from frappe.utils import (flt, getdate, get_url, now,
nowtime, get_time, today, get_datetime, add_days)
from frappe.utils import add_to_date, now, nowdate

class BankLoan(Document):
	@frappe.whitelist()
	def on_submit(self):
		self.show_warnings()

	@frappe.whitelist()
	def validate(self):
		self.set_repayments()

	@frappe.whitelist()
	def show_warnings(self):
		if not self.current_account:
			frappe.throw(_(" برجاء تحديد الحساب الجاري داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

		if not self.receivable_account:
			frappe.throw(_(" برجاء تحديد حساب برسم التحصيل داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

		if not self.payable_account:
			frappe.throw(_(" برجاء تحديد حساب برسم الدفع داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

	'''@frappe.whitelist()
	def set_repayments(self):
		docs = frappe.db.sql(""" select repayment_start_date, repayment_every, repayment_amount, payment_frequency from `tabBank Loan` where `tabBank Loan`.name = %s """, self.name, as_dict=1)
		x = 0
		y = self.no_of_repayments
		for x in self.repayment_schedule and x <= y:
			z = self.append("repayment_schedule", {})
			z.payment_date = self.repayment_start_date
			z.total_payment = self.repayment_amount
			x += 1
	'''

	def set_repayments(self):
		if not self.repayment_start_date:
			frappe.throw(_("Repayment Start Date is mandatory"))

		if self.repayment_type == "Fixed":
			self.repayment_schedule = []
			payment_date = self.repayment_start_date
			balance_amount = self.net_loan_amount
			while (balance_amount > 0):
				interest_amount = self.interest_amount
				principal_amount = self.repayment_amount - interest_amount
				balance_amount = flt(balance_amount + interest_amount - self.repayment_amount)
				if balance_amount < 0:
					principal_amount += balance_amount
					balance_amount = 0.0

				total_payment = principal_amount + interest_amount
				self.append("repayment_schedule", {
					"payment_date": payment_date,
					"principal_amount": principal_amount,
					"interest_amount": interest_amount,
					"total_payment": total_payment,
					"balance_loan_amount": balance_amount
				})
				next_payment_date = add_days(payment_date, self.repayment_every)
				payment_date = next_payment_date

	pass



