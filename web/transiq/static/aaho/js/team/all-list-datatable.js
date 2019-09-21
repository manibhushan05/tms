var date = new Date();
var options = {
    weekday: "short", year: "numeric", month: "short",
    day: "numeric", hour: "2-digit", minute: "2-digit"
};
var vehicleListDataTable = $('#vehicleListDataTable').DataTable({
    "serverSide": true,
    "processing": true,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500],
        ['25 Records', '50 Records', '100 Records', '500 Records']
    ],
    buttons: [
        'pageLength', {
            extend: 'excelHtml5',
            title: 'Vehcles Data ' + date.toLocaleTimeString("en-US", options)
        },
        {
            extend: 'csvHtml5',
            title: 'Vehicles Data ' + date.toLocaleTimeString("en-US", options)
        }
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort"
    }],
    "ajax": {
        "serverSide": true,
        "url": "/api/supplier-vehicle-list/?format=datatables",
        headers: {"Authorization": localStorage.getItem("token")},
        data: function (d) {
            $.extend(d);
            $.extend(d, {columns: ''});
            var dt_params = $('.input-sm').val();
            // Add dynamic parameters to the data object sent to the server
            if (dt_params) {
                $.extend(d, {search: dt_params});
            }
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
        }
    },
    columns: [
        {
            data: "id",
            "render": function (data) {
                return '<a href="javascript:;" data-url="/api/supplier-vehicle-retrieve/' + data + '/" class="btn btn-default getAjaxPage"><i class="fa fa-edit"></i></a>';
            }
        },
        {data: "vehicle_number_display"},
        {data: "driver_data.name"},
        {data: "driver_data.phone"},
        {data: "owner_data.name"},
        {data: "owner_data.phone"},
        {data: "vehicle_type_data.name"},
        {data: "vehicle_type_data.truck_body_type"},
        {data: "created_on"}
    ],
    "language": {
        "processing": "<div class='datatable_overlay'><img  src='/static/aaho/images/loader_gif.gif' /> </div>"
    }
});

var ownerListDataTable = $('#ownerListDataTable').DataTable({
    "serverSide": true,
    "processing": true,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500],
        ['25 Records', '50 Records', '100 Records', '500 Records']
    ],
    buttons: [
        'pageLength', {
            extend: 'excelHtml5',
            title: 'Owner ' + date.toLocaleTimeString("en-US", options)
        },
        {
            extend: 'csvHtml5',
            title: 'Owner ' + date.toLocaleTimeString("en-US", options)
        }
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort"
    }],
    "ajax": {
        "serverSide": true,
        "url": "/api/owner-owner-list/?format=datatables",
        headers: {"Authorization": localStorage.getItem("token")},
        data: function (d) {
            $.extend(d);
            $.extend(d, {columns: ''});
            var dt_params = $('.input-sm').val();
            // Add dynamic parameters to the data object sent to the server
            if (dt_params) {
                $.extend(d, {search: dt_params});
            }
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
        }
    },
    columns: [
        {
            data: "id",
            "render": function (data) {
                return '<a href="javascript:;" data-url="/api/owner-owner-retrieve/' + data + '/" class="btn btn-default getAjaxPage"><i class="fa fa-edit"></i></a>';
            }
        },
        {data: "owner_profile.name"},
        {
            data: "vehicle_list",
            "render": function (data, type, row, meta) {
                var veh = '';
                data.forEach(function (vehicle) {
                    veh += vehicle['vehicle_number'] + '<br/>';
                });
                return veh;
            }
        },
        {data: "pan"},
        {data: "owner_profile.phone"},
        {data: "owner_profile.contact_person_name"},
        {data: "owner_profile.contact_person_phone"},
        {data: "owner_profile.comment"},
        {data: "created_on"}
    ],
    "language": {
        "processing": "<div class='datatable_overlay'><img  src='/static/aaho/images/loader_gif.gif' /> </div>"
    }
});

var supplierListDataTable = $('#supplierListDataTable').DataTable({
    "serverSide": true,
    "processing": true,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500],
        ['25 Records', '50 Records', '100 Records', '500 Records']
    ],
    buttons: [
        'pageLength', {
            extend: 'excelHtml5',
            title: 'Suppliers ' + date.toLocaleTimeString("en-US", options),
            className: "excelButtonsToHide"
        },
        {
            extend: 'csvHtml5',
            title: 'Suppliers ' + date.toLocaleTimeString("en-US", options),
            className: "csvButtonsToHide"
        }
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort"
    }],
    "ajax": {
        "serverSide": true,
        "url": "/api/supplier-supplier-list/?format=datatables&broker_data_category=web_brokers_records",
        headers: {"Authorization": localStorage.getItem("token")},
        data: function (d) {
            $.extend(d);
            $.extend(d, {columns: ''});
            var dt_params = $('.input-sm').val();
            // Add dynamic parameters to the data object sent to the server
            if (dt_params) {
                $.extend(d, {search: dt_params});
            }
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
        }
    },
    columns: [
        {
            data: "id", "render": function (data) {
                return '<a href="javascript:;" data-url="/api/supplier-supplier-retrieve/' + data + '/" class="btn btn-default getAjaxPage"><i class="fa fa-edit"></i></a>';
            }
        },
        {data: "name"},
        {data: "code"},
        {
            data: "vehicles_data",
            "render": function (data) {
                return data.split("\n").join("<br/>");
            }
        },
        {data: "pan"},
        {data: "phone"},
        {data: "city_data.name"},
        {data: "created_on"}
    ],
    "language": {
        "processing": "<div class='datatable_overlay'><img  src='/static/aaho/images/loader_gif.gif' /> </div>",
    }
});

var driverListDataTable = $('#driverListDataTable').DataTable({
    "serverSide": true,
    "processing": true,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500],
        ['25 Records', '50 Records', '100 Records', '500 Records']
    ],
    buttons: [
        'pageLength', {
            extend: 'excelHtml5',
            title: 'Driver ' + date.toLocaleTimeString("en-US", options)
        },
        {
            extend: 'csvHtml5',
            title: 'Driver ' + date.toLocaleTimeString("en-US", options)
        }
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort"
    }],
    "ajax": {
        "serverSide": true,
        "url": "/api/supplier-supplier-driver-list/?format=datatables",
        headers: {"Authorization": localStorage.getItem("token")},
        data: function (d) {
            $.extend(d);
            $.extend(d, {columns: ''});
            var dt_params = $('.input-sm').val();
            // Add dynamic parameters to the data object sent to the server
            if (dt_params) {
                $.extend(d, {search: dt_params});
            }
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
        }
    },
    columns: [
        {
            data: "id", "render": function (data) {
                return '<a href="javascript:;" data-url="/api/supplier-supplier-driver-retrieve/' + data + '/" class="btn btn-default getAjaxPage"><i class="fa fa-edit"></i></a>';
            }
        },
        {data: "name"},
        {data: "phone"},
        {data: "driving_licence_number"},
        {data: "driving_licence_validity"},
        {data: "created_on"}
    ],
    "language": {
        "processing": "<div class='datatable_overlay'><img  src='/static/aaho/images/loader_gif.gif' /> </div>",
    }
});

var customerListDataTable = $('#customerListDataTable').DataTable({
    "serverSide": true,
    "processing": true,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500],
        ['25 Records', '50 Records', '100 Records', '500 Records']
    ],
    buttons: [
        'pageLength', {
            extend: 'excelHtml5',
            title: 'Customers ' + date.toLocaleTimeString("en-US", options),
            className: "excelButtonsToHide"
        },
        {
            extend: 'csvHtml5',
            title: 'Customers ' + date.toLocaleTimeString("en-US", options),
            className: "csvButtonsToHide"
        }
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort"
    }],
    "ajax": {
        "serverSide": true,
        "url": "/api/sme-sme-list/?format=datatables&sme_data_category=web_customers_records",
        headers: {"Authorization": localStorage.getItem("token")},
        data: function (d) {
            $.extend(d);
            $.extend(d, {columns: ''});
            var dt_params = $('.input-sm').val();
            // Add dynamic parameters to the data object sent to the server
            if (dt_params) {
                $.extend(d, {search: dt_params});
            }
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status === "401") {
                redirectToLogin(error);
            }
        }
    },
    columns: [
        {
            data: "id", "render": function (data) {
                return '<a href="javascript:;" data-url="/api/sme-sme-retrieve/' + data + '/" class="btn btn-default getAjaxPage"><i class="fa fa-edit"></i></a>';
            }
        },
        {data: "company_code"},
        {data: "sme_profile.name"},
        {data: "gstin"},
        {data: "pan_number"},
        {data: "sme_profile.contact_person_name"},
        {data: "sme_profile.contact_person_phone"},
        {data: "sme_profile.email"},
        {data: "customer_address"},
        {data: "city_data.city"},
        {data: "aaho_poc_data.name"},
        {data: "aaho_office_branch.branch_name"},
        {data: "created_on"}
    ],
    "language": {
        "processing": "<div class='datatable_overlay'><img  src='/static/aaho/images/loader_gif.gif' /> </div>"
    }
});
$.ajax({
    url: "/api/employee-roles-mapping-data/",
    type: 'GET',
    dataType: 'json',
    contentType: 'application/json',
    beforeSend: function (xhr, settings) {
        xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
    }
}).done(function (response, status) {
    if (!(response.includes('tech') || response.includes('management') || response.includes('accounts_payable') || response.includes('accounts_receivable'))) {
        customerListDataTable.column(0).visible(false);
        customerListDataTable.buttons('.excelButtonsToHide').nodes().addClass('hidden');
        customerListDataTable.buttons('.csvButtonsToHide').nodes().addClass('hidden');
    }
    if (!(response.includes('tech') || response.includes('management') || response.includes('accounts_payable') || response.includes('accounts_receivable') || response.includes('office_data_entry'))) {
        supplierListDataTable.column(0).visible(false);
        supplierListDataTable.buttons('.excelButtonsToHide').nodes().addClass('hidden');
        supplierListDataTable.buttons('.csvButtonsToHide').nodes().addClass('hidden');
    }
}).fail(function (jqXHR, status, error) {

});


