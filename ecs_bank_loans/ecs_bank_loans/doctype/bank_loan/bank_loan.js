// Copyright (c) 2021, erpcloud.systems and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bank Loan", {
	setup: function(frm) {
		frm.set_query("bank_account", function() {
			return {
				filters: [
					["Bank Account","bank", "in", frm.doc.applicant]
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

frappe.ui.form.on("Bank Loan", {
    validate:function(frm, cdt, cdn){
        var dw = locals[cdt][cdn];
        var total1 = 0;
        var total2 = 0;
        var total3 = 0;
        frm.doc.repayment_schedule.forEach(function(dw) { total1 += dw.principal_amount; });
        frm.doc.repayment_schedule.forEach(function(dw) { total2 += dw.interest_amount; });
        frm.doc.repayment_schedule.forEach(function(dw) { total3 += dw.total_payment; });
        frm.set_value("total_principal_payable", total1);
        frm.set_value("total_interest_payable", total2);
        frm.set_value("total_payment", total3);
        refresh_field("total_principal_payable");
        refresh_field("total_interest_payable");
        refresh_field("total_payment");
    }
});

//frappe.ui.form.on("Bank Loan","validate", function(frm){
//    var x = frm.doc.no_of_repayments;
//    cur_frm.doc.repayment_schedule.length = x;
//    for (var i =0; i < x; i++){
//    cur_frm.doc.repayment_schedule[i].total_payment = cur_frm.doc.repayment_amount;
//    }
//    cur_frm.refresh_field('repayment_schedule');
//});

//frappe.ui.form.on("Bank Loan","validate", function(){
//    if (cur_frm.doc.repayment_schedule.length != cur_frm.doc.no_of_repayments){
//        frappe.throw("عدد الأقساط في جدول الاستهلاك لا يساوي عدد الأقساط التي تم تحديدها في تفاصيل القرض");
//    }
//});


