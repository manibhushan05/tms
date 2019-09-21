/**
 * Created by mani on 5/5/17.
 */
var BANK_ACCOUNT_FORM = $('#register-bank-account-form');

$(function () {
    $('form').parsley('validate');
});
$("#bank_name").select2({
    placeholder: "Select a Bank",
    ajax: {
        method: "GET",
        url: '/api/utils-bank-name-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var officeArray = [];
            $.each(data.data, function (key, value) {
                officeArray.push({id: value.name, text: value.name})
            });
            return {results: officeArray};
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
$("#registered_user").select2({
    placeholder: "Select a User",
    ajax: {
        method: "GET",
        url: '/api/user-list/?is_active=true',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var officeArray = [];
            $.each(data.data, function (key, value) {
                officeArray.push({id: value.username, text: value.profile.name + ', ' + value.profile.phone})
            });
            return {results: officeArray};
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
$(".transaction_type").select2({
    placeholder: "Select Transaction Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$(".account_type").select2({
    placeholder: "Select Account Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$("#is_account_verified").select2({
    placeholder: "Is Account Verified",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$("#account_status").select2({
    placeholder: "Select Account Status",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$('#register-bank-account-button').click(function () {
    var BANK_ACCOUNT_FORM = $("#register-bank-form");
    if (!BANK_ACCOUNT_FORM.parsley().isValid()) {
        return true;
    }
    var data = BANK_ACCOUNT_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/utils-bank-create/",
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
            autoHideDelay: 2000,
            clickToHide: true,
            className: 'success'
        });
        setTimeout(function () {
            getAjaxCallFunction('/page/bank-account-list/');
        }, 5000);
        NProgress.done();
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
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

$('#btn-update-bank-account').click(function (e) {
    var BANK_ACCOUNT_FORM = $("#form-update-bank-account");
    if (!BANK_ACCOUNT_FORM.parsley().isValid()) {
        return true;
    }
    var data = BANK_ACCOUNT_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    var account_id = $("#update_account_id").val();
    e.preventDefault();
    $.ajax({
        url: "/api/utils-bank-partial-update/" + account_id + "/",
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
        }, 3000);
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