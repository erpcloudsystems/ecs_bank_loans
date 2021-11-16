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
        self.make_journal_entry()
        frappe.set_value('Bank Loan', self.name, 'disbursed_amount', self.loan_amount)

    @frappe.whitelist()
    def validate(self):
        self.calculate_repayment_and_interest_amount()
        self.calculate_repayment_schedule()
        self.calculate_totals()
        self.calculate_fixed_interest()

    @frappe.whitelist()
    def show_warnings(self):
        if not self.current_account:
            frappe.throw(_(" برجاء تحديد الحساب الجاري داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

        if not self.receivable_account:
            frappe.throw(_(" برجاء تحديد حساب برسم التحصيل داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

        if not self.payable_account:
            frappe.throw(_(" برجاء تحديد حساب برسم الدفع داخل الحساب البنكي وإعادة إختيار الحساب البنكي مرة أخرى "))

    def calculate_repayment_and_interest_amount(self):
        if self.calculate_repayment_schedule_automatically and not self.calculate_rate_of_interest:
            import numpy as np
            self.repayment_amount = -1 * np.pmt(0.01 * self.rate_of_interest / (360 / self.repayment_every), self.no_of_repayments, self.loan_amount)
            self.interest_amount = 0.01 * self.loan_amount * self.rate_of_interest / (360 / self.repayment_every)
        if self.calculate_repayment_schedule_automatically and self.calculate_rate_of_interest:
            import numpy as np
            self.rate_of_interest = np.rate(self.no_of_repayments,(-1*self.repayment_amount),self.loan_amount,12)*12*100
            self.interest_amount = 0.01 * self.loan_amount * self.rate_of_interest / (360 / self.repayment_every)

    def calculate_repayment_schedule(self):
        if self.calculate_repayment_schedule_automatically:
            self.repayment_schedule = []
            payment_date = self.repayment_start_date
            balance_amount = self.loan_amount
            a = self.no_of_repayments
            interest_amount = self.interest_amount
            balance_loan_amount = self.loan_amount - (self.repayment_amount - interest_amount)
            principal_amount = self.repayment_amount - interest_amount
            while (a > 0):
                balance_amount = flt(balance_amount + interest_amount - self.repayment_amount)
                if balance_loan_amount < 0:
                    total_payment = principal_amount + interest_amount
                    principal_amount += balance_amount
                    balance_loan_amount = 0.0
                    interest_amount = total_payment - principal_amount

                self.append("repayment_schedule", {
                    "payment_date": payment_date,
                    "principal_amount": principal_amount,
                    "interest_amount": interest_amount,
                    "total_payment": self.repayment_amount,
                    "balance_loan_amount": balance_loan_amount
                })
                next_payment_date = add_days(payment_date, self.repayment_every)
                next_interest_amount = (self.rate_of_interest/100/12) * (balance_loan_amount)
                payment_date = next_payment_date
                interest_amount = next_interest_amount
                next_principal_amount = self.repayment_amount - interest_amount
                principal_amount = next_principal_amount
                next_balance_loan_amount = balance_loan_amount - principal_amount
                balance_loan_amount = next_balance_loan_amount
                a -= 1

    def calculate_totals(self):
        self.total_payment = 0
        self.total_interest_payable = 0
        self.total_principal_payable = 0

        for data in self.repayment_schedule:
            self.total_payment += data.total_payment
            self.total_interest_payable += data.interest_amount
            self.total_principal_payable += data.principal_amount

    def calculate_fixed_interest(self):
        self.fixed_interest = 100 * (self.total_interest_payable / (self.no_of_repayments / 12) / self.loan_amount)

    def make_journal_entry(self):
        if self.included_in_loan_amount and self.loan_amount != self.net_loan_amount:
            frappe.db.sql(""" update `tabBank Loan` set status = "Disbursed" where name = %s""", self.name)
            accounts = [
                {
                    "doctype": "Journal Entry Account",
                    "account": self.current_account,
                    "credit": 0,
                    "debit": self.net_loan_amount,
                    "debit_in_account_currency": self.loan_amount,
                    "user_remark": self.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": self.payable_interest_account,
                    "credit": 0,
                    "debit": self.total_interest_payable,
                    "debit_in_account_currency": self.total_interest_payable,
                    "user_remark": self.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": self.administrative_expenses_account,
                    "debit": self.administrative_expenses_amount,
                    "credit": 0,
                    "debit_in_account_currency": self.administrative_expenses_amount,
                    "user_remark": self.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": self.loan_account_2,
                    "credit": self.total_payment,
                    "debit": 0,
                    "credit_in_account_currency": self.total_payment,
                    "user_remark": self.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": self.current_account,
                    "credit": self.administrative_expenses_amount,
                    "debit": 0,
                    "credit_in_account_currency": self.administrative_expenses_amount,
                    "user_remark": self.name
                }
            ]
            new_doc = frappe.get_doc({
                "doctype": "Journal Entry",
                "voucher_type": "Bank Entry",
                "reference_doctype": "Bank Loan",
                "reference_link": self.name,
                "cheque_no": self.name,
                "cheque_date": self.posting_date,
                "posting_date": self.posting_date,
                "accounts": accounts,
                "user_remark": self.applicant

            })
            new_doc.insert()
            new_doc.submit()

            self.reload()

        if not self.included_in_loan_amount:
            frappe.db.sql(""" update `tabBank Loan` set status = "Disbursed" where name = %s""", self.name)
            accounts = [
                {
                    "doctype": "Journal Entry Account",
                    "account": self.current_account,
                    "credit": 0,
                    "debit": self.total_principal_payable,
                    "debit_in_account_currency": self.total_principal_payable,
                    "user_remark": self.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": self.payable_interest_account,
                    "credit": 0,
                    "debit": self.total_interest_payable,
                    "debit_in_account_currency": self.total_interest_payable,
                    "user_remark": self.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": self.loan_account_2,
                    "credit": self.total_payment,
                    "debit": 0,
                    "credit_in_account_currency": self.total_payment,
                    "user_remark": self.name
                }
            ]
            new_doc = frappe.get_doc({
                "doctype": "Journal Entry",
                "voucher_type": "Bank Entry",
                "reference_doctype": "Bank Loan",
                "reference_link": self.name,
                "cheque_no": self.name,
                "cheque_date": self.posting_date,
                "posting_date": self.posting_date,
                "accounts": accounts,
                "user_remark": self.applicant

            })
            new_doc.insert()
            new_doc.submit()
            self.reload()


    pass

def make_paid(doc, method=None):
    if doc.reference_doctype == "Bank Loan" and doc.bill_no:
        frappe.set_value('Bank Loan Repayment Schedule',doc.bill_no,'is_paid','1')
        frappe.set_value('Bank Loan Repayment Schedule',doc.bill_no,'journal_entry',doc.name)
        row = frappe.get_doc('Bank Loan Repayment Schedule',doc.bill_no)
        parent = frappe.get_doc('Bank Loan',row.parent)
        cur_prnc = parent.total_principal_paid
        row_prnc = row.principal_amount
        new_prnc = cur_prnc+row_prnc
        cur_inter = parent.total_interest_paid
        row_inter = row.interest_amount
        new_inter = cur_inter + row_inter
        cur_tot = parent.total_amount_paid
        row_tot = row.total_payment
        new_tot = cur_tot + row_tot
        frappe.set_value('Bank Loan', row.parent, 'total_principal_paid',new_prnc)
        frappe.set_value('Bank Loan', row.parent, 'total_interest_paid', new_inter)
        frappe.set_value('Bank Loan', row.parent, 'total_amount_paid', new_tot)

    if doc.reference_doctype == "Bank Loan" and doc.early_payment == 1:
        frappe.set_value('Bank Loan', doc.reference_link, 'early_paid', '1')
        bank_loan = frappe.get_doc('Bank Loan',doc.reference_link)
        cur_prnc = bank_loan.total_principal_paid
        je_prnc = bank_loan.total_principal_payable - bank_loan.total_principal_paid
        new_prnc = cur_prnc + je_prnc
        frappe.set_value('Bank Loan', doc.reference_link, 'total_principal_paid', new_prnc)
        cur_inter = bank_loan.total_interest_paid
        je_inter = bank_loan.total_interest_payable - bank_loan.total_interest_paid
        new_inter = cur_inter + je_inter
        frappe.set_value('Bank Loan', doc.reference_link, 'total_interest_paid', new_inter)
        cur_tot = bank_loan.total_amount_paid
        je_tot = bank_loan.total_payment - bank_loan.total_amount_paid
        new_tot = cur_tot + je_tot
        frappe.set_value('Bank Loan', doc.reference_link, 'total_amount_paid', new_tot)



def journal_cancel(doc, method=None):
    if doc.reference_doctype == "Bank Loan" and doc.bill_no:
        frappe.db.sql("""update `tabJournal Entry` set reference_link ='' where bill_no='{bill_no}'""".format(bill_no=doc.bill_no))
        frappe.set_value('Bank Loan Repayment Schedule', doc.bill_no, 'is_paid', '0')
        frappe.set_value('Bank Loan Repayment Schedule', doc.bill_no, 'journal_entry', "")
        row = frappe.get_doc('Bank Loan Repayment Schedule', doc.bill_no)
        parent = frappe.get_doc('Bank Loan', row.parent)
        cur_prnc = parent.total_principal_paid
        row_prnc = row.principal_amount
        new_prnc = cur_prnc - row_prnc
        cur_inter = parent.total_interest_paid
        row_inter = row.interest_amount
        new_inter = cur_inter - row_inter
        cur_tot = parent.total_amount_paid
        row_tot = row.total_payment
        new_tot = cur_tot - row_tot
        frappe.set_value('Bank Loan', row.parent, 'total_principal_paid', new_prnc)
        frappe.set_value('Bank Loan', row.parent, 'total_interest_paid', new_inter)
        frappe.set_value('Bank Loan', row.parent, 'total_amount_paid', new_tot)

    if doc.reference_doctype == "Bank Loan" and doc.early_payment == 1:
        frappe.set_value('Bank Loan', doc.reference_link, 'early_paid', '0')
        frappe.set_value('Bank Loan', doc.reference_link, 'early_payment', '0')
        frappe.set_value('Bank Loan', doc.reference_link, 'early_payment_commission', '')
        bank_loan = frappe.get_doc('Bank Loan',doc.reference_link)
        cur_prnc = bank_loan.total_principal_paid
        je_prnc = doc.principal_amount
        new_prnc = cur_prnc - je_prnc
        frappe.set_value('Bank Loan', doc.reference_link, 'total_principal_paid', new_prnc)
        cur_inter = bank_loan.total_interest_paid
        je_inter = doc.interest_amount
        new_inter = cur_inter - je_inter
        frappe.set_value('Bank Loan', doc.reference_link, 'total_interest_paid', new_inter)
        cur_tot = bank_loan.total_amount_paid
        je_tot = doc.total_payment
        new_tot = cur_tot - je_tot
        frappe.set_value('Bank Loan', doc.reference_link, 'total_amount_paid', new_tot)




def set_accured():
    frappe.db.sql("""update `tabBank Loan Repayment Schedule` set is_accrued = '1' where payment_date >= date(CURRENT_DATE() + 5) and payment_date < date(CURRENT_DATE() +10) """)
    frappe.db.sql("""update `tabBank Loan Repayment Schedule` set is_accrued = '1' where payment_date < CURRENT_DATE()""")


