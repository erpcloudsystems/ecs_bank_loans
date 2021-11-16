// Copyright (c) 2021, erpcloud.systems and contributors
// For license information, please see license.txt
cur_frm.add_fetch('bank_account','account','current_account');
cur_frm.add_fetch('bank_account','collection_fee_account','receivable_account');
cur_frm.add_fetch('bank_account','payable_account','payable_account');
cur_frm.add_fetch('loan_type','rate_of_interest','rate_of_interest');

frappe.ui.form.on("Bank Loan", {
	setup: function(frm) {
		frm.set_query("bank_account", function() {
			return {
				filters: [
					["Bank Account","bank", "in", frm.doc.applicant],
					["Bank Account","is_company_account", "=", 1],

				]
			};
		});
	}
});

frappe.ui.form.on("Bank Loan", {
	setup: function(frm) {
		frm.set_query("loan_application", function() {
			return {
				filters: [
					["Loan Application","docstatus", "=", 1]
				]
			};
		});
	}
});

frappe.ui.form.on("Bank Loan", {
	setup: function(frm) {
		frm.set_query("loan_type", function() {
			return {
				filters: [
					["Loan Type","docstatus", "=", 1]
				]
			};
		});
	}
});

frappe.ui.form.on("Bank Loan","applicant", function(frm){
    cur_frm.set_value("bank_account","");
    cur_frm.set_value("current_account","");
    cur_frm.set_value("receivable_account","");
    cur_frm.set_value("payable_account","");
});

frappe.ui.form.on("Bank Loan","bank_account", function(frm){
    cur_frm.set_value("current_account","");
    cur_frm.set_value("receivable_account","");
    cur_frm.set_value("payable_account","");
});

frappe.ui.form.on("Bank Loan","payment_frequency", function(frm){
    if(cur_frm.doc.payment_frequency == "Monthly"){
        cur_frm.set_value("repayment_every",30);
    }
    if(cur_frm.doc.payment_frequency == "Quarterly"){
        cur_frm.set_value("repayment_every",90);
    }
    if(cur_frm.doc.payment_frequency == "Semi Annually"){
        cur_frm.set_value("repayment_every",180);
    }
    if(cur_frm.doc.payment_frequency == "Annually"){
        cur_frm.set_value("repayment_every",360);
    }
});

frappe.ui.form.on("Bank Loan", "validate", function(frm) {
    if(cur_frm.doc.administrative_expenses_depends_on == "Percent" && cur_frm.doc.percentage){
        cur_frm.doc.administrative_expenses_amount = cur_frm.doc.percentage * cur_frm.doc.loan_amount / 100;
    }
});

frappe.ui.form.on("Bank Loan", "validate", function(frm) {
    if(cur_frm.doc.included_in_loan_amount){
        cur_frm.doc.net_loan_amount = cur_frm.doc.loan_amount - cur_frm.doc.administrative_expenses_amount;
    }

    if(!cur_frm.doc.included_in_loan_amount){
        cur_frm.doc.net_loan_amount = cur_frm.doc.loan_amount;
    }
});


//frappe.ui.form.on("Bank Loan","validate", function(){
//    if (cur_frm.doc.repayment_schedule.length != cur_frm.doc.no_of_repayments){
//        frappe.throw("عدد الأقساط في جدول الاستهلاك لا يساوي عدد الأقساط التي تم تحديدها في تفاصيل القرض");
//    }
//});

frappe.ui.form.on("Bank Loan Repayment Schedule", "make_payment", function(frm,cdt,cdn) {
    var d = locals[cdt][cdn];
    if (cur_frm.doc.status != "Disbursed"){
        frappe.throw("You Must Receive The Loan From The Bank Before Making Payment");
    }
});

frappe.ui.form.on("Bank Loan Repayment Schedule", "make_payment", function(frm,cdt,cdn) {
    var d = locals[cdt][cdn];
    if (cur_frm.doc.total_amount_paid >= cur_frm.doc.total_payment){
        frappe.throw("Loan Has Been Fully Paid");
    }
});

frappe.ui.form.on("Bank Loan", "make_early_payment", function(frm,cdt,cdn) {
    if (cur_frm.doc.total_amount_paid >= cur_frm.doc.total_payment){
        frappe.throw("Loan Has Been Fully Paid");
    }
});


frappe.ui.form.on("Bank Loan Repayment Schedule", "make_payment", function(frm,cdt,cdn) {
{
                frappe.db.insert(populate_je_obj_3(frm))
                    .then(function (doc) {
                        console.log(`${doc.doctype} ${doc.name} created on ${doc.creation}`);
                        frappe.set_route('Form', doc.doctype, doc.name);

                        }
                );
}
    function populate_je_obj_3(frm, data) {
	var d = locals[cdt][cdn];
    let je = {};
    let accounts = [
                {
                    "doctype": "Journal Entry Account",
                    "account": frm.doc.loan_account_2,
                    "debit": d.total_payment,
                    "credit": 0,
                    "debit_in_account_currency": d.total_payment,
                    "user_remark": cur_frm.docname,
                    "loan_name": cur_frm.docname
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": frm.doc.interest_expense_account,
                    "debit": d.interest_amount,
                    "credit": 0,
                    "debit_in_account_currency": d.interest_amount,
                    "user_remark": cur_frm.docname,
                    "loan_name": cur_frm.docname
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": frm.doc.current_account,
                    "debit": 0,
                    "credit": d.total_payment,
                    "credit_in_account_currency": d.total_payment,
                    "user_remark": cur_frm.docname,
                    "loan_name": cur_frm.docname
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": frm.doc.payable_interest_account,
                    "debit": 0,
                    "credit": d.interest_amount,
                    "credit_in_account_currency": d.interest_amount,
                    "user_remark": cur_frm.docname,
                    "loan_name": cur_frm.docname
                },

            ];

    je["doctype"] = "Journal Entry";
    je["voucher_type"] = "Bank Entry";
    je["reference_doctype"] = "Bank Loan";
    je["reference_link"] = cur_frm.doc.name;
    je["total_payment"] = d.total_payment;
    je["interest_amount"] = d.interest_amount;
    je["principal_amount"] = d.principal_amount;
    je["cheque_no"] = cur_frm.doc.name;
    je["bill_no"] = d.name;
    je["cheque_date"] = d.payment_date;
    je["posting_date"] = d.payment_date;
    je["accounts"] = accounts;
    return je;

}

function submit_je(frm) {
    ccco_params.je["remark"] = cur_frm.docname;
    frappe.db.insert(ccco_params.je)
        .then(function (doc) {
            frappe.call({
                "method": "frappe.client.submit",
                "args": {
                    "doc": doc
                },
                "callback": (r) => {
                    console.log(r);
                }
            });
        });
}
});

frappe.ui.form.on("Bank Loan", "early_payment_commission", function() {
    cur_frm.save('Update');
});
frappe.ui.form.on("Bank Loan", "calculate_rate_of_interest", function(frm,cdt,cdn) {
   // cur_frm.save('Update');
   cur_frm.set_value("rate_of_interest", "");
   cur_frm.refresh_field("rate_of_interest");
});

frappe.ui.form.on("Bank Loan", "make_early_payment", function(frm,cdt,cdn) {
{
                frappe.db.insert(populate_je_obj_4(frm))
                    .then(function (doc) {
                        console.log(`${doc.doctype} ${doc.name} created on ${doc.creation}`);
                        frappe.set_route('Form', doc.doctype, doc.name);

                        }
                );
}
    function populate_je_obj_4(frm, data) {
    var d = locals[cdt][cdn];
    let je = {};
    let accounts = [
                {
                    "doctype": "Journal Entry Account",
                    "account": cur_frm.doc.loan_account_2,
                    "debit": cur_frm.doc.total_payment - cur_frm.doc.total_amount_paid,
                    "credit": 0,
                    "debit_in_account_currency": cur_frm.doc.total_payment - cur_frm.doc.total_amount_paid,
                    "user_remark": cur_frm.doc.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": cur_frm.doc.interest_expense_account,
                    "debit": cur_frm.doc.early_payment_commission,
                    "credit": 0,
                    "debit_in_account_currency": cur_frm.doc.early_payment_commission,
                    "user_remark": cur_frm.doc.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": cur_frm.doc.current_account,
                    "debit": 0,
                    "credit": (cur_frm.doc.total_payment - cur_frm.doc.total_amount_paid) + cur_frm.doc.early_payment_commission - (cur_frm.doc.total_interest_payable - cur_frm.doc.total_interest_paid),
                    "credit_in_account_currency": (cur_frm.doc.total_payment - cur_frm.doc.total_amount_paid) + cur_frm.doc.early_payment_commission - (cur_frm.doc.total_interest_payable - cur_frm.doc.total_interest_paid),
                    "user_remark": cur_frm.doc.name
                },
                {
                    "doctype": "Journal Entry Account",
                    "account": cur_frm.doc.payable_interest_account,
                    "debit": 0,
                    "credit": cur_frm.doc.total_interest_payable - cur_frm.doc.total_interest_paid,
                    "credit_in_account_currency": cur_frm.doc.total_interest_payable - cur_frm.doc.total_interest_paid,
                    "user_remark": cur_frm.doc.name
                },

            ];

    je["doctype"] = "Journal Entry";
    je["voucher_type"] = "Bank Entry";
    je["reference_doctype"] = "Bank Loan";
    je["reference_link"] = cur_frm.doc.name;
    je["cheque_no"] = cur_frm.doc.name;
    je["cheque_date"] = frappe.datetime.add_days(frm.doc.process_date, 0),
    je["posting_date"] = frappe.datetime.add_days(frm.doc.process_date, 0),
    je["early_payment"] = 1,
    je["total_payment"] = cur_frm.doc.total_payment - cur_frm.doc.total_amount_paid;
    je["interest_amount"] = cur_frm.doc.total_interest_payable - cur_frm.doc.total_interest_paid;
    je["principal_amount"] = cur_frm.doc.total_principal_payable - cur_frm.doc.total_principal_paid;
    je["accounts"] = accounts;
    return je;

}

function submit_je(frm) {
    ccco_params.je["remark"] = cur_frm.doc.name;
    frappe.db.insert(ccco_params.je)
        .then(function (doc) {
            frappe.call({
                "method": "frappe.client.submit",
                "args": {
                    "doc": doc
                },
                "callback": (r) => {
                    console.log(r);
                }
            });
        });
}
});

