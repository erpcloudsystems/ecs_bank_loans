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


