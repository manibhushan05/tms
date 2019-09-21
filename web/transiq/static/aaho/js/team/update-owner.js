/**
 * Created by Atul on 20/08/18.
 */
$(function () {
    $('form').parsley('validate');
});

$(document).off('click', '#btn-update-owner').on('click', '#btn-update-owner', function () {
    var UPDATE_OWNER_FORM = $('#update-owner-form');
    if (!UPDATE_OWNER_FORM.parsley().isValid()) {
        return true;
    }
    var ownerId = $("#ownerId").val();
    NProgress.start();
    var data = UPDATE_OWNER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/owner-owner-partial-update/" + ownerId + "/",
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