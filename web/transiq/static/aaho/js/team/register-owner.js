/**
 * Created by Atul on 18/08/18.
 */
$(function () {
    $('form').parsley('validate');
});

function resetOwnerForm() {
    $('#register-owner-form')[0].reset();
    $('#vehicle-number,#city').text('');
}

$(document).off('click', '#resetRegisterOwner').on('click', '#resetRegisterOwner', function (e) {
    e.preventDefault();
    resetOwnerForm();
});

$(document).off('click', '#btn-register-owner').on('click', '#btn-register-owner', function () {
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
                autoHideDelay: 10000,
                clickToHide: true,
                className: 'error'
            });
        }

        NProgress.done();

    });
    return false;
});
