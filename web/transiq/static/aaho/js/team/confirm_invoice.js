$(document).off('click', '.escalateToSales').on('click', '.escalateToSales', function (e) {
    var requestSent = $(this);
    e.preventDefault();
    if (requestSent.data('requestRunning')) {
        return;
    }
    requestSent.data('requestRunning', true);
    var id = $(this).attr('data-id');
    var invoice_number = $(this).attr('data-invoiceid');
    NProgress.start();
    var data = { "booking_status": "party_invoice_sent", "booking_stage": "escalated", "invoice_number": invoice_number };
    $.ajax({
        url: '/api/booking-statuses-mapping-update-invoice-based/',
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {
        requestSent.data('requestRunning', false);
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        NProgress.done();
        //replaced button to text escalated
        $('#fileupload_' + id + ' .escalateBtnDiv').html('<br/><br/><h5 class="escalated" style="margin-left:24px;">Escalated</h5>');
    }).fail(function (jqXHR, status, error) {
        requestSent.data('requestRunning', false);
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
            $.notify(jqXHR['responseJSON']['msg'], {
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

$(document).off('click', '.confirmedByPhone').on('click', '.confirmedByPhone', function (e) {
    var requestSent = $(this);
    e.preventDefault();
    if (requestSent.data('requestRunning')) {
        return;
    }
    requestSent.data('requestRunning', true);
    var id = $(this).attr('data-id')
    var uploadForm = $("#fileupload_" + id);
    var formError = uploadForm.parsley().isValid();
    if (formError !== false) {
        // var data = uploadForm.serialize();
        var data = uploadForm.find(':input').filter(function () {
            return $.trim(this.value).length > 0
        }).serializeJSON();
        console.log(data);
        $.ajax({
            url: '/api/file-upload-invoice-receipt-file-create/',
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(data),
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
            }
        }).done(function (response, status) {
            requestSent.data('requestRunning', false);
            $.notify(response['msg'], {
                position: "top center",
                autoHideDelay: 1000,
                clickToHide: true,
                className: 'success'
            });
            NProgress.done();
            var confirmInvoiceCount = $("#confirm_invoice_badge").text();
            if (parseInt(confirmInvoiceCount) === 1 || isNaN(parseInt(confirmInvoiceCount))) {
                $("#confirm_invoice_badge").text('');
            }
            else {
                $("#confirm_invoice_badge").text(parseInt(confirmInvoiceCount) - 1);
            }
            setTimeout(function () {
                $('.rowUpload_' + id + '').remove();
                noData();
            }, 1000);
        }).fail(function (jqXHR, status, error) {
            requestSent.data('requestRunning', false);
            console.log(jqXHR);
            if (jqXHR.status === "401") {
                redirectToLogin(error);
            }
            else {
                $.notify(jqXHR['responseJSON']['msg'], {
                    position: "top center",
                    autoHideDelay: 2000,
                    clickToHide: true,
                    className: 'error'
                });
            }
            NProgress.done();
        });
    }
    else {
        requestSent.data('requestRunning', false);
    }
});

//toggle collapsable links
$('.collapse-link').click(function () {
    $(this).find('i').toggleClass('fa-chevron-up fa-chevron-down');
    $(this).closest('.x_title').nextAll('.x_content:first').toggle();
});

function noData() {
    var confirmInvoiceCountNoData = $("#confirm_invoice_badge").text();
    if (parseInt(confirmInvoiceCountNoData) == 0 || isNaN(parseInt(confirmInvoiceCountNoData))) {
        var noData_html = "";
        noData_html += '<div class="x_panel">';
        noData_html += '<div class="x_content">';
        noData_html += '<div class="panel-body">';
        noData_html += '<div class="row">';
        noData_html += '<div class="comingSoonContent">No data found...</div>';
        noData_html += '</div>';
        noData_html += '</div>';
        noData_html += '</div>';
        noData_html += '</div>';
        $('#dashboardPages').html(noData_html);
    }
}