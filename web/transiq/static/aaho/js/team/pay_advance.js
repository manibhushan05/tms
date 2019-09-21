var date = new Date();
var options = {
    weekday: "short", year: "numeric", month: "short",
    day: "numeric", hour: "2-digit", minute: "2-digit"
};
var pay_advance_dt = $('#pay_advance_DataTable').DataTable({
    "serverSide": true,
    "processing": true,
    "DisplayLength": 25,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500, -1],
        ['25 Records', '50 Records', '100 Records', '500 Records', 'All Records']
    ],
    buttons: [
        'pageLength', {
            extend: 'excelHtml5',
            title: 'Generate pay advance List ' + date.toLocaleTimeString("en-US", options)
        },
        {
            extend: 'csvHtml5',
            title: 'Generate pay advance List ' + date.toLocaleTimeString("en-US", options)
        }
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort",
    }],
    "ajax": {
        "type": "GET",
        "serverSide": true,
        "url": "/api/team-manual-booking-list/?booking_data_category=advance_not_paid&format=datatables",
        headers: { "Authorization": localStorage.getItem("token") },
        data: function (d) {
            $.extend(d);
            var dt_params = $('.input-sm').val();
            // Add dynamic parameters to the data object sent to the server
            if (dt_params) {
                $.extend(d, { search: dt_params });
            }
        },
        dataSrc: function (json) {
            return json.data;
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
        }
    },
    columns: [

        { data: "shipment_date" },
        {
            data: "booking_id",
            "render": function (data, type, row) {
                return '<a href="javascript:;" data-id="' + row.id + '" data-url="/api/manual-booking-retrieve/' + row.id + '/"  class="btn btn-default getAjaxPage" style="background: darkgray; color:white">' + data + '</a>'
            }
        },
        {
            data: null,
            "render": function (data, type, row) {
                return '<a href="javascript:;" data-id="' + row.id + '"  class="btn btn-default advancePaid" style="background: darkgray; color:white">Advance Paid</a>';
            }
        },
        { data: "customer_placed_order_data.name" },
        { data: "customer_placed_order_data.code" },
        { data: "supplier_data.name" },
        { data: "from_city_fk_data.name" },
        { data: "to_city_fk_data.name" },
        {
            data: null,
            "render": function (data, type, row) {
                return row.lorry_number + ' ' + row.vehicle_category_data.type;
            }
        },
        { data: "lorry_number", className: 'hidden' },
        { data: "vehicle_category_data.type", className: 'hidden' },
        { data: "id", className: 'hidden' },

    ],
    "language": {
        "processing": "<img  src='/static/aaho/images/loader.gif' />"
    }

});

$(document).off("click", ".advancePaid").on("click", ".advancePaid", function (e) {
    var id = $(this).attr('data-id');
    var payAdvanceCount = $("#pay_advance_badge").text();
    e.preventDefault();
    NProgress.start();
    var data = {
        "booking_status": "advance_paid", "manual_booking_id": id,
        "booking_stage": "in_progress"
    };
    $.ajax({
        url: "/api/booking-statuses-mapping-create-key-based/",
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
            autoHideDelay: 10000,
            clickToHide: true,
            className: 'success'
        });
        NProgress.done();
        pay_advance_dt
            .draw(true);
        if (parseInt(payAdvanceCount) == 1) {
            $("#pay_advance_badge").text('');
        }
        else {
            var notifyCount = parseInt(payAdvanceCount) - 1;
            $("#pay_advance_badge").text(notifyCount);
        }
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status == "401") {
            redirectToLogin(error);
        }
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 10000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});
