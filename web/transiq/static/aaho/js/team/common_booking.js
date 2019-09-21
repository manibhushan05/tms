/**
 * Created by shobhit on 18/4/17.
 */

$(document).ready(function () {

    $('.outward-payment-id').change(function () {
        var atLeastOneIsChecked = $('input[name="bill_ids[]"]:checked').length > 0;
        if (atLeastOneIsChecked) {
            $("#btn-outward-bill").attr("disabled", false);
        }
        else {
            $("#btn-outward-bill").attr("disabled", true);
        }
    });

    $("#outward-payment-bill").submit(function (e) {
        e.preventDefault(e);
        var checkedValues = $('input[name="bill_ids[]"]:checked').map(function () {
            return this.value;
        }).get();
        if (checkedValues.length < 1) {
            alert("Please Select at least one payment");
        } else {
            $("#bill-numbers").val(checkedValues);
            $.ajax({
                url: "/api/team-outward-payment-bill-doc/",
                type: "POST",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify($(this).serializeJSON()),
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
                },
                success: function (response, status) {
                    $.notify(response['msg'], {
                        position: "top center",
                        autoHideDelay: 1000,
                        clickToHide: true,
                        className: 'success'
                    });
                    window.open(response['msg'], "_self", "");
                    setTimeout(function () {
                        location.reload();
                    }, 1000);
                    NProgress.done();
                },
                error: function (xhr, status, error) {
                    if (xhr.status == "401") {
                        redirectToLogin(error);
                    }
                    else {
                        try {
                            var data = JSON.parse(xhr.responseText);
                            alert(data.msg);
                        } catch (e) {
                            alert('Unknown Exception, http status code = ' + status);
                        }
                    }
                }
            });
        }
    });
});