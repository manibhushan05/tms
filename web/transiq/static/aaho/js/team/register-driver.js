/**
 * Created by mani on 10/5/17.
 */
$(function () {
    $('form').parsley('validate');
});
var dateFormat = {
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true,
    startDate: moment().add(0, 'days').format("DD-MMM-YYYY")
};
$('#dl_validity').datepicker(dateFormat);

function resetDriverForm() {
    $('#register-driver-form')[0].reset();
    $('#city').text('');
}

$(document).off('click', '#resetRegisterDriver').on('click', '#resetRegisterDriver', function (e) {
    e.preventDefault();
    resetDriverForm();
});

$(document).off('click', '#btn-register-driver').on('click', '#btn-register-driver', function () {
    var REGISTER_DRIVER_FORM = $('#register-driver-form');
    if (!REGISTER_DRIVER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = REGISTER_DRIVER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/driver-driver-create/",
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
        }, 3000);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
            $.notify(jqXHR['msg'], {
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