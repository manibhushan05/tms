/**
 * Created by mani on 13/5/17.
 */
$(function () {
    $('form').parsley('validate');
});
$('#btn-chnage-password').click(function (e) {
    var CHANGE_PASSWORD_FORM = $('#chnage-password-form');
    if (!CHANGE_PASSWORD_FORM.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = CHANGE_PASSWORD_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/change-password/",
        type: 'PUT',
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
            getAjaxCallFunction('/page/employee-profile/');
        }, 3000);
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