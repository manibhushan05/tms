/**
 * Created by mani on 4/10/16.
 */

var INWARD_PAYMENT_MODE_ID = $('.inward_payment_mode');
var CHEQUE_NUMBER_ID = $('.cheque_number_area');
var outward_payment_date_id = $('#outward_payment_date');
var OUTWARD_PAYMENT_MODE_ID = $('.outward_payment_mode');

$('#out-ward-payment-table').DataTable();
$('#in-ward-payment-table').DataTable();

function isInArray(target, array) {
    for (var i = 0; i < array.length; i++) {
        if (array[i] === target) {
            return true;
        }
    }
    return false;
}

var dateFormat = {
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true
};
$('input[name=pod_date]').datepicker(dateFormat);
$('input[name=delivered_date]').datepicker(dateFormat);

$('#party_invoice_date').datepicker(dateFormat);

$('#dl_validity').datepicker(dateFormat);
$('#insurance_date').datepicker(dateFormat);


$(".username").select2({
    placeholder: "Select a username",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".transaction_type").select2({
    placeholder: "Select a Transaction Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#invoice_raise_to").select2({
    placeholder: "Select Invoice Raise To",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".billing_type").select2({
    placeholder: "Select a Billing Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".outward_payment_status").select2({
    placeholder: "Select a outward payment status",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#fuel_card_area").hide();

$("#bank_account_area").hide();

$(".inward_payment_status").select2({
    placeholder: "Select a inward payment status",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".pod_status").select2({
    placeholder: "Select POD Status",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".invoice_status").select2({
    placeholder: "Select Invoice Status",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});



$("#supplier_name").select2({
    placeholder: "Select Supplier Name",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$("#truck_owner_name").select2({
    placeholder: "Select Truck Owner Name",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#truck_driver_name").select2({
    placeholder: "Select Truck Owner Name",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

function save_full_booking_data() {
    var responseStatus = false;
    var form_id = $('#update-commission-booking-form');
    form_id.parsley().validate();
    if (!form_id.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = form_id.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: '/api/manual-booking-partial-update/' + $('#manual_booking_id').val() + '/',
        type: 'PATCH',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        async: false,
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        responseStatus = true;
        NProgress.done();
    }).fail(function (data, status, error) {
        responseStatus = false;
        if (jqXHR.status == "401") {
            redirectToLogin(error);
        }
        NProgress.done();
    });
    return responseStatus;
}
$("#btn_print_invoice").click(function (e) {
    if (!$("#raise-invoice-form").parsley().isValid()) {
        return true;
    }
    var commissionBookingDataStatus = save_full_booking_data();
    e.preventDefault();
    if (commissionBookingDataStatus) {
        var formData = $("#raise-invoice-form").find(':input').filter(function () {
            return $.trim(this.value).length > 0
        }).serializeJSON();
        if (!$("#raise-invoice-form").parsley().isValid()) {
            return true;
        }
        NProgress.start();
        $.ajax({
            url: '/api/create-single-booking-invoice/',
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            async: false,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
            }
        }).done(function (data, status) {
            setTimeout(function () {
                location.reload();
            }, 1000);
            responseStatus = true;
            NProgress.done();
        }).fail(function (data, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
            responseStatus = false;
            NProgress.done();
        });
    }
});

$('#save-changes').click(function (e) {
    var form_id = $('#update-commission-booking-form');
    form_id.parsley().validate();
    if (!form_id.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = form_id.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: '/api/manual-booking-partial-update/' + $('#manual_booking_id').val() + '/',
        type: 'PATCH',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        getAjaxCallFunction('/page/full-booking-list-page/');
        // location.reload();
        NProgress.done();
    }).fail(function (data, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        NProgress.done();
    });
    return false;
});