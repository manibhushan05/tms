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
        url: "/api/supplier-vehicle-create/",
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
        }, 4000);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        } else {
            $.notify(JSON.parse(jqXHR.responseText)['msg'], {
                position: "top center",
                autoHideDelay: 10000,
                clickToHide: true,
                className: 'error'
            });
        }

        NProgress.done();
    });
    return false;
});

$(document).off('click', '#btn-update-vehicle').on('click', '#btn-update-vehicle', function () {
    var UPDATE_VEHICLE_FORM = $('#update-vehicle-form');
    if (!UPDATE_VEHICLE_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = UPDATE_VEHICLE_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/supplier-vehicle-partial-update/" + $('#vehicle_id').val() + '/',
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
        NProgress.done();
        setTimeout(function () {
            location.reload();
        }, 4000);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        } else {
            $.notify(JSON.parse(jqXHR.responseText)['msg'], {
                position: "top center",
                autoHideDelay: 10000,
                clickToHide: true,
                className: 'error'
            });
        }

        NProgress.done();
    });
    return false;
});

$('.validate_data').on('change', function () {
    data = {};
    var attr_id = $(this).attr('id');
    $('#' + attr_id).parsley().reset();

    $.ajax({
        url: "/api/vehicle-data-validation/",
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        contentType: 'application/json',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {

    }).fail(function (jqXHR, status, error) {
        $('#' + attr_id).parsley().addError('customValidationId', {message: JSON.parse(jqXHR.responseText)['msg']});
    });
    return false;
});


$('#vehicle_body_type').append('<option value=""></option>' +
    '<option value="open">Open</option>' +
    '<option value="closed">Closed</option>' +
    '<option value="semi">Semi</option>' +
    '<option value="half">Half</option>' +
    '<option value="containerized">Containerized</option>');

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