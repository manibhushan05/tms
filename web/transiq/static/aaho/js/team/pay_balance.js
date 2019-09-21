var date = new Date();
var options = {
    weekday: "short", year: "numeric", month: "short",
    day: "numeric", hour: "2-digit", minute: "2-digit"
};
var pay_balance_dt = $('#pay_balance_DataTable').DataTable({
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
            title: 'Generate pay balance List ' + date.toLocaleTimeString("en-US", options)
        },
        {
            extend: 'csvHtml5',
            title: 'Generate pay balance List ' + date.toLocaleTimeString("en-US", options)
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
        "url": "/api/team-manual-booking-list/?booking_data_category=pay_balance&format=datatables",
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
