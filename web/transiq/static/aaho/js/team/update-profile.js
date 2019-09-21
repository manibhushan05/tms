/**
 * Created by mani on 14/5/17.
 */
$(function () {
    $('form').parsley('validate');
});
$('#btn-update-profile').click(function (e) {

    var UPDATE_PROFILE_FORM = $('#update-profile-form');
    if (!UPDATE_PROFILE_FORM.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = UPDATE_PROFILE_FORM.find(':input').filter(function () {
                return $.trim(this.value).length > 0
            }).serializeJSON();
    $.ajax({
        url: "/api/employee-employee-partial-update/" + $('#employee_id').val() + '/',
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