/**
 * Created by Atul on 18/08/18.
 */
$(function () {
    $('form').parsley('validate');
});

$('.date').datepicker({
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true,
    startDate: moment().add(0, 'days').format("DD-MMM-YYYY")
});
$('.past-date').datepicker({
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true,
    endDate: moment().add(0, 'days').format("DD-MMM-YYYY")
});
$('.year').datepicker({
    autoclose: true,
    format: " yyyy",
    viewMode: "years",
    minViewMode: "years",
    // startDate: moment().add(-30, 'years').format("DD-MMM-YYYY"),
    endDate: moment().add(0, 'days').format("DD-MMM-YYYY")
});

$('#vehicle_body_type').append('<option value=""></option>' +
    '<option value="open">Open</option>' +
    '<option value="closed">Closed</option>' +
    '<option value="semi">Semi</option>' +
    '<option value="half">Half</option>' +
    '<option value="containerized">Containerized</option>');

$("#vehicle_body_type").select2({
    placeholder: "Select Vehicle Body Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

var VEHICLE_NUMBER = $('#vehicle_number');
$("input").change(function () {
    VEHICLE_NUMBER.val(VEHICLE_NUMBER.val());
});


function resetVehicleForm() {

    $('#register-vehicle-form')[0].reset();
    $('.truck-category,#gps_enable,#vehicle_body_type,#owner_id').text('');

    $('#gps_enable').append('<option value=""></option><option value="yes">Yes</option><option value="no">No</option>');

    $("#gps_enable").select2({
        placeholder: "Select GPS Enable Status",
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });

    $('#vehicle_body_type').append('<option value=""></option>' +
        '<option value="open">Open</option>' +
        '<option value="closed">Closed</option>' +
        '<option value="semi">Semi</option>' +
        '<option value="half">Half</option>' +
        '<option value="containerized">Containerized</option>');

    $("#vehicle_body_type").select2({
        placeholder: "Select Vehicle Body Type",
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}

$(document).off('click', '#resetRegisterVehicle').on('click', '#resetRegisterVehicle', function (e) {
    e.preventDefault();
    resetVehicleForm();
});


$(document).off('click', '#btn-register-vehicle').on('click', '#btn-register-vehicle', function () {
    var REGISTER_VEHICLE_FORM = $('#register-vehicle-form');
    if (!REGISTER_VEHICLE_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = REGISTER_VEHICLE_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/owner-owner-vehicle-create/",
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
        setTimeout(function () {
            location.reload();
        }, 3000);
        NProgress.done();
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
            $.notify(jqXHR['responseText'], {
                position: "top center",
                autoHideDelay: 1000,
                clickToHide: true,
                className: 'error'
            });
        }

        NProgress.done();
    });
    return false;
});