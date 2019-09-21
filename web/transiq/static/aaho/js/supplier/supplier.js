$(function () {
    $('form').parsley('validate');
});

function validate_phone_pan() {
    var phone_id = $('#phone-primary');
    var pan_id = $('#pan');
    if ($.trim(phone_id.val()) === '' && $.trim(pan_id.val()) === '') {
        phone_id.prop('required', true);
    } else if (phone_id.parsley().isValid() || pan_id.parsley().isValid()) {
        phone_id.prop('required', false);
    } else {
        phone_id.prop('required', true);
    }
}

$(document).off('click', '#btn-register-supplier').on('click', '#btn-register-supplier', function () {
    var REGISTER_SUPPLIER_FORM = $('#register-supplier-form');
    $("#pan").on('change  paste', function () {
        validate_phone_pan();
        $("#primary_phone").parsley().validate();
        $("#pan").parsley().validate();
    });

    if (!REGISTER_SUPPLIER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = REGISTER_SUPPLIER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/supplier-supplier-create/",
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
            autoHideDelay: 5000,
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


$(document).off('click', '#btn-update-supplier').on('click', '#btn-update-supplier', function () {
    var UPDATE_SUPPLIER_FORM = $('#update-supplier-form');
    $("#pan").on('change  paste', function () {
        validate_phone_pan();
        $("#primary_phone").parsley().validate();
        $("#pan").parsley().validate();
    });

    if (!UPDATE_SUPPLIER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = UPDATE_SUPPLIER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/supplier-supplier-partial-update/" + $('#sup_id').val() + '/',
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
            autoHideDelay: 5000,
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
    } else if ($(this).attr('id').startsWith("email")) {
        data = {'email': $(this).val()}
    } else if ($(this).attr('id').startsWith("supplier_name")) {
        data = {'supplier_name': $(this).val()}
    } else if ($(this).attr('id') === 'vehicle-number') {
        data = {'vehicle': $(this).val()};
    } else if ($(this).attr('id') === 'pan') {
        data = {'pan': $(this).val()};
    }
    $.ajax({
        url: "/api/supplier-data-validation/",
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