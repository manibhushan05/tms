/**
 * Created by Atul on 20/08/18.
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
    minViewMode: "years"
});

var bodyTypeArr = ['open', 'closed', 'semi', 'half', 'containerized'];
var deviceStatusArr = ['yes', 'no'];

var bodyType = $('#vehicle_body_type').val();
var deviceStatus = $('#gps_enable').val();
$.each(bodyTypeArr, function (index, value) {
    if (value != bodyType) {
        $('#vehicle_body_type').append($('<option>', {
            id: value,
            text: value
        }));
    }
});
$.each(deviceStatusArr, function (index, value) {
    if (value != deviceStatus) {
        $('#gps_enable').append($('<option>', {
            id: value,
            text: value
        }));
    }
});

$(document).off('click', '#btn-update-vehicle').on('click', '#btn-update-vehicle', function () {
    var UPDATE_VEHICLE_FORM = $('#update-vehicle-form');
    if (!UPDATE_VEHICLE_FORM.parsley().isValid()) {
        return true;
    }
    var vehicleId = $("#vehicleId").val();
    NProgress.start();
    var data = UPDATE_VEHICLE_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/owner-owner-vehicle-partial-update/" + vehicleId + "/",
        type: 'PATCH',
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
        }, 2000);
        NProgress.done();
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
            $.notify(JSON.parse(jqXHR.responseText)['msg'], {
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
