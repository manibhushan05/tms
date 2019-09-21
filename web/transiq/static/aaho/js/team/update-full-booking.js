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
$('#pod_date').datepicker(dateFormat);
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

$(".truck_type").select2({
    placeholder: "Select a Truck Type",
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

$(".consignor_city").select2({
    placeholder: "Select a Consignor City",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".consignee_city").select2({
    placeholder: "Select a Consignee City",
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
$("#accounting_supplier_name").select2({
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


$("#btn_print_invoice").click(function (e) {
    if (!$("#raise-invoice-form").parsley().isValid()) {
        return true;
    }
    var fullBookingDataStatus = save_full_booking_data();
    e.preventDefault();
    if (fullBookingDataStatus) {
        var formData = $("#raise-invoice-form").find(':input').filter(function () {
            return $.trim(this.value).length > 0
        }).serializeJSON();
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
            }, 4000);
            responseStatus = true;
            NProgress.done();
        }).fail(function (data, status, error) {
            if (jqXHR.status === "401") {
                redirectToLogin(error);
            }
            else {
                $.notify('Fail', {
                    position: "top center",
                    autoHideDelay: 1000,
                    clickToHide: true,
                    className: 'error'
                });
            }
            NProgress.done();
        });
    }


});
$("#btn_download_edit_invoice").click(function () {
    $("#submit_type").val("download_invoice");
});

function save_full_booking_data() {
    var responseStatus = false;
    var form_id = $('#update-full-booking-form');
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

$('.btn-save-full-booking').click(function (e) {
    var form_id = $('#update-full-booking-form');
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
        NProgress.done();
    }).fail(function (data, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        NProgress.done();
    });
    return false;
});

$('#btn_save_and_print').click(function (e) {
    var form_id = $('#update-full-booking-form');
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

        printLR();

    }).fail(function (data, status) {
        NProgress.done();
    });
    return false;
});

function printLR() {
    $.ajax({
        url: '/api/manual-booking-reprint-lr/' + $('#manual_booking_id').val() + '/',
        type: 'GET',
        dataType: 'json',
        contentType: 'application/json',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        if (data.msg) {
            window.open(data.msg, "_self", "");
            NProgress.done();
            getAjaxCallFunction('/page/full-booking-list-page/');
        }
        NProgress.done();
    }).fail(function (data, status) {
        NProgress.done();
    });
}

function downloadLR() {
    $.ajax({
        url: '#',
        type: 'GET',
        dataType: 'json',
        contentType: 'application/json',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        if (data.msg) {
            // window.open(data.msg);
            window.open(data.msg, "_self", "");
            NProgress.done();
        }
        NProgress.done();
    }).fail(function (data, status) {
        NProgress.done();
    });
}

$('#download_lr').click(function (e) {
    var form_id = $('#update-full-booking-form');
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

        downloadLR();
        // location.reload();
        //NProgress.done();
    }).fail(function (data, status) {
        NProgress.done();
    });
    return false;
});
