/**
 * Created by mani on 19/4/17.
 */
var inward_payment_date_id = $('#inward_payment_date');
var INWARD_PAYMENT_MODE_ID = $('.inward_payment_mode');
var CHEQUE_NUMBER_ID = $('.cheque_number_area');

$('#show_inward_payment_modal').click(function (e) {
    var form_id = $('#update-full-booking-form');
    if (form_id[0]) {
        form_id.parsley().validate();
        if (!form_id.parsley().isValid()) {
            return true;
        }
        $('#full-booking-inward-payment-form')[0].reset();
        $('#inward_payment_modal').modal('show');
    }
    else {
        var commissionBookingForm = $('#update-commission-booking-form');
        commissionBookingForm.parsley().validate();
        if (!commissionBookingForm.parsley().isValid()) {
            return true;
        }
        $('#update-commission-booking-form')[0].reset();
        $('#inward_payment_modal').modal('show');
    }
});


$('button#commission-booking-inward-submit').click(function (e) {
    var payment_form = $('#commission-booking-inward-payment-form');
    if (!payment_form.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    var fullBookingDataStatus = save_full_booking_data();
    if (fullBookingDataStatus) {
        $("#inward_payment_modal").modal('hide');
        NProgress.start();
        var data = payment_form.find(':input').filter(function () {
            return $.trim(this.value).length > 0
        }).serializeJSON();
        $.ajax({
            url: "/api/team-inward-payment-create/",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(data),
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
            }
        }).done(function (response, status) {
            $.notify(response['msg'], {
                position: "top center",
                autoHideDelay: 1000,
                clickToHide: true,
                className: 'success'
            });
            NProgress.done();
            setTimeout(function () {
                location.reload();
            }, 1000);
        }).fail(function (jqXHR, status, error) {
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
        return false
    }
});

$('button#full-booking-inward-submit').click(function (e) {
    var payment_form = $('#full-booking-inward-payment-form');
    if (!payment_form.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    var fullBookingDataStatus = save_full_booking_data();
    if (fullBookingDataStatus) {
        $("#inward_payment_modal").modal('hide');
        NProgress.start();
        var data = payment_form.find(':input').filter(function () {
            return $.trim(this.value).length > 0
        }).serializeJSON();
        $.ajax({
            url: "/api/team-inward-payment-create/",
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(data),
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
            }
        }).done(function (response, status) {
            $.notify(response['msg'], {
                position: "top center",
                autoHideDelay: 1000,
                clickToHide: true,
                className: 'success'
            });
            NProgress.done();
            setTimeout(function () {
                location.reload();
            }, 1000);
        }).fail(function (jqXHR, status, error) {
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
        return false
    }
});

$('#btn-inward-payment-only').click(function () {
    if (!$('#inward-payment-only').parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = $('#inward-payment-only').serialize();
    $.ajax({
        url: "/team/inward-payments/",
        type: 'POST',
        data: data
    }).done(function (data, status) {
        NProgress.done();
        window.location.href = "/team/inward-payments/";
    }).fail(function (data, status) {
        NProgress.done();
        window.location.href = "/team/inward-payments/";
    });
    return false;
});

inward_payment_date_id.click(function () {
    if (INWARD_PAYMENT_MODE_ID.val() === '') {
        alert('Please Select Mode of Payment');
    }
});
CHEQUE_NUMBER_ID.hide();

var dateFormat = {
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true,
    startDate: moment().add(-120, 'days').format("DD-MMM-YYYY"),
    endDate: moment().add(0, 'days').format("DD-MMM-YYYY")
};

INWARD_PAYMENT_MODE_ID.select2({
    placeholder: "Select mode of payment",
    allowClear: true
}).change(function () {
    INWARD_PAYMENT_MODE_ID.parsley().validate();
    if (INWARD_PAYMENT_MODE_ID.val() === '') {
        alert('Please Select Mode of Payment');
    }
    else if (INWARD_PAYMENT_MODE_ID.val() === 'cheque') {
        CHEQUE_NUMBER_ID.show();
        CHEQUE_NUMBER_ID.show().prop('required', true);
        inward_payment_date_id.datepicker(dateFormat);
    }
    else {
        CHEQUE_NUMBER_ID.hide();
        CHEQUE_NUMBER_ID.prop('required', true);
        inward_payment_date_id.datepicker(dateFormat);
    }
});


