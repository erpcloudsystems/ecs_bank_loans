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
import frappe, math, json
import erpnext
from frappe import _
from six import string_types
from frappe.utils import flt, rounded, add_months, nowdate, getdate, now_datetime

class BankLoan(Document):
    @frappe.whitelist()
    def on_submit(self):
        self.show_warnings()

    @frappe.whitelist()
    def validate(self):
        self.calculate_repayment_and_interest_amount()
        self.calculate_repayment_schedule()
        self.calculate_totals()

    @frappe.whitelist()
    def show_warnings(self):
        if not self.current_account:
            frappe.throw(_(" برجاء تحديد الحساب الجاري داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

        if not self.receivable_account:
            frappe.throw(_(" برجاء تحديد حساب برسم التحصيل داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

        if not self.payable_account:
            frappe.throw(_(" برجاء تحديد حساب برسم الدفع داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

    def calculate_repayment_and_interest_amount(self):
        if self.calculate_repayment_schedule_automatically:
            import numpy as np
            self.repayment_amount = -1 * np.pmt(0.01 * self.rate_of_interest / (360 / self.repayment_every), self.no_of_repayments, self.net_loan_amount)
            self.interest_amount = 0.01 * self.net_loan_amount * self.rate_of_interest / (360 / self.repayment_every)

    def calculate_repayment_schedule(self):
        if self.calculate_repayment_schedule_automatically:
            self.repayment_schedule = []
            payment_date = self.repayment_start_date
            balance_amount = self.net_loan_amount
            while (balance_amount > 0):
                interest_amount = self.interest_amount
                principal_amount = self.repayment_amount - interest_amount
                balance_amount = flt(balance_amount + interest_amount - self.repayment_amount)
                balance_loan_amount = self.net_loan_amount - principal_amount
                if balance_amount < 0:
                    principal_amount += balance_amount
                    balance_amount = 0.0

                total_payment = principal_amount + interest_amount
                self.append("repayment_schedule", {
                    "payment_date": payment_date,
                    "principal_amount": principal_amount,
                    "interest_amount": interest_amount,
                    "total_payment": total_payment,
                    "balance_loan_amount": balance_loan_amount
                })
                next_payment_date = add_days(payment_date, self.repayment_every)
                next_interest_amount = self.interest_amount * balance_loan_amount
                next_balance_loan_amount = balance_loan_amount - principal_amount
                payment_date = next_payment_date
                interest_amount = next_interest_amount
                balance_loan_amount = next_balance_loan_amount


    def calculate_totals(self):
        self.total_payment = 0
        self.total_interest_payable = 0
        self.total_principal_payable = 0

        for data in self.repayment_schedule:
            self.total_payment += data.total_payment
            self.total_interest_payable +=data.interest_amount
            self.total_principal_payable += data.principal_amount

    pass



