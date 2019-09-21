/**
 * Created by mani on 4/5/17.
 */
$(function () {
    $('form').parsley('validate');
});

$("#city").select2({
    placeholder: "Select City",
    ajax: {
        url: '/api/utils-city-list/',
        headers: { "Authorization": localStorage.getItem('token') },
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var cityArray = [];
            $.each(data.data, function (key, value) {
                cityArray.push({ id: value.id, text: value.name + ',' + value.code + ',' + value.state.name })
            });
            return { results: cityArray };
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status === "401") {
                redirectToLogin(error);
            }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#owner_id").select2({
    placeholder: "Select Owner",
    ajax: {
        url: '/utils/owners-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});


$("#driver_id").select2({
    placeholder: "Select Driver",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});


$("#vehicle_category").select2({
    placeholder: "Select Vehicle Category",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});


$("#vehicle_body_type").select2({
    placeholder: "Select Vehicle Body Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});


$("#gps_enable").select2({
    placeholder: "Select GPS Enable Status",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});


$("#driver_app_user").select2({
    placeholder: "Select Driver App User",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});


$("#vehicle-number").select2({
    maximumSelectionLength: 100,
    placeholder: "Please add Vehicles",
    ajax: {
        url: '/utils/vehicles-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$('#update-vehicle-owner').select2({
    placeholder: 'Please Add vehicle',
    allowClear: true,
    maximumSelectionLength: 100,
}).change(function () {
    $(this).parsley().validate();
});

$('.date').datepicker({
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true
});
$('.year').datepicker({
    autoclose: true,
    format: " yyyy",
    viewMode: "years",
    minViewMode: "years"
});

var VEHICLE_NUMBER = $('#vehicle_number');
$("input").change(function () {
    VEHICLE_NUMBER.val(VEHICLE_NUMBER.val());
});

$('#btn-register-sme').click(function () {
    var REGISTER_SME_FORM = $('#register-sme-form');
    if (!REGISTER_SME_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = REGISTER_SME_FORM.serialize();
    $.ajax({
        url: "/team/register-sme/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        $(REGISTER_SME_FORM).each(function () {
            this.reset();
        });
        NProgress.done();
    }).fail(function (jqXHR, status) {
        $.notify(JSON.parse(jqXHR.responseText)['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});

$('#btn-update-customer').click(function () {
    var UPDATE_CUSTOMER_FORM = $('#update-customer-form');
    if (!UPDATE_CUSTOMER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = UPDATE_CUSTOMER_FORM.serialize();
    $.ajax({
        url: "/team/update-customer-data/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        NProgress.done();
    }).fail(function (jqXHR, status) {
        $.notify(JSON.parse(jqXHR.responseText)['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});

$('#btn-register-vehicle').click(function () {
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


$('#btn-register-owner').click(function () {
    var REGISTER_OWNER_FORM = $('#register-owner-form');
    if (!REGISTER_OWNER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = REGISTER_OWNER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();

    $.ajax({
        url: "/api/owner-owner-create/",
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


$('#btn-update-owner').click(function () {
    var UPDATE_OWNER_FORM = $('#update-owner-form');
    if (!UPDATE_OWNER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = UPDATE_OWNER_FORM.serialize();
    $.ajax({
        url: "/team/update-owner-data/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        NProgress.done();
    }).fail(function (jqXHR, status) {
        $.notify(JSON.parse(jqXHR.responseText)['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});

$('#btn-update-vehicle').click(function () {
    var UPDATE_VEHICLE_FORM = $('#update-vehicle-form');
    if (!UPDATE_VEHICLE_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = UPDATE_VEHICLE_FORM.serialize();
    $.ajax({
        url: "/team/update-vehicle-data/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        NProgress.done();
    }).fail(function (jqXHR, status) {
        $.notify(JSON.parse(jqXHR.responseText)['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});
