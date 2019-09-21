/**
 * Created by mani on 18/5/17.
 */

$(function () {
    $('form').parsley('validate');
});
var dateFormat = {
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true
};
$('#dl_validity').datepicker(dateFormat);

$(document).off('click', '#btn-update-driver').on('click', '#btn-update-driver', function () {
    var UPDATE_DRIVER_FORM = $('#update-driver-form');
    if (!UPDATE_DRIVER_FORM.parsley().isValid()) {
        return true;
    }
    var driverId = $("#driverId").val();
    NProgress.start();
    var data = UPDATE_DRIVER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/driver-driver-partial-update/" + driverId + "/",
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
            $.notify('ERROR', {
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