$(document).off('click', '#btn-register-driver').on('click', '#btn-register-driver', function () {
    var REGISTER_DRIVER_FORM = $('#register-driver-form');
    $("#pan").on('change  paste', function () {
        $("#primary_phone").parsley().validate();
        $("#pan").parsley().validate();
    });

    if (!REGISTER_DRIVER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = REGISTER_DRIVER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/supplier-supplier-driver-create/",
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
                autoHideDelay: 5000,
                clickToHide: true,
                className: 'error'
            });
        }

        NProgress.done();
    });
    return false;
});

$(document).off('click', '#btn-update-driver').on('click', '#btn-update-driver', function () {
    var UPDATE_DRIVER_FORM = $('#update-driver-form');
    if (!UPDATE_DRIVER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = UPDATE_DRIVER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/supplier-supplier-driver-partial-update/" + $('#driver_id').val() + '/',
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
                autoHideDelay: 5000,
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
    if ($(this).attr('id').startsWith("phone")) {
        data = {'phone': $(this).val()}
    }
    $.ajax({
        url: "/api/supplier-driver-data-validation/",
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        contentType: 'application/json',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {
        if (attr_id === 'phone-primary' || attr_id === 'pan') {
            validate_phone_pan();
            $('#phone-primary').parsley().validate();
            $("#pan").parsley().validate();
        }
    }).fail(function (jqXHR, status, error) {
        console.log(attr_id);
        $('#' + attr_id).parsley().addError('customValidationId', {message: JSON.parse(jqXHR.responseText)['msg']});
    });
    return false;
});

$('#dl_validity').datepicker({
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true,
    startDate: moment().add(0, 'days').format("DD-MMM-YYYY")
});
