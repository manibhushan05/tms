supplierName();
function supplierName() {
    $(".truck-suppliers").select2({
        placeholder: "Select Supplier Name",
        ajax: {
            url: '/utils/suppliers-data/',
            delay: 250,
            data: function (params) {
                return {
                    search: params.term,
                    page: params.page || 25
                };
            }
        },
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}

city();
function city() {
    $(".city").select2({
        placeholder: "Select City",
        ajax: {
            url: '/api/utils-city-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            delay: 250,
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var cityArray = [];
                $.each(data.data, function (key, value) {
                    cityArray.push({ id: value.id, text: value.name + ',' + value.code + ',' + value.state.name })
                });
                return { results: cityArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
            }
        },
        allowClear: true,
    }).change(function () {
        $(this).parsley().validate();
    });
}

$(".employee").select2({
    placeholder: "Select Employee",
    ajax: {
        url: '/utils/employees-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term,
                page: params.page || 25
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$(".state").select2({
    placeholder: "Select State",
    ajax: {
        url: '/utils/states-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term,
                page: params.page || 25
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".aaho_ofice").select2({
    placeholder: "Select Aaho Office",
    ajax: {
        url: '/utils/aaho-office-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term,
                page: params.page || 25
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

truckCategory();
function truckCategory() {
    $(".truck-category").select2({
        placeholder: "Select Vehicle Category",
        ajax: {
            url: '/utils/vehicle-categories-data/',
            delay: 250,
            data: function (params) {
                return {
                    search: params.term,
                    page: params.page || 50
                };
            }
        },
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}

truckDriver();
function truckDriver() {
    $('.truck-driver').select2({
        placeholder: "Select Truck Driver Name",
        ajax: {
            url: '/utils/drivers-data/',
            delay: 250,
            data: function (params) {
                return {
                    search: params.term,
                    page: params.page || 25
                };
            }
        },
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}

truckOwner();
function truckOwner() {
    $('.truck-owner').select2({
        placeholder: "Select Truck Owner",
        ajax: {
            url: '/utils/owners-data/',
            delay: 250,
            data: function (params) {
                return {
                    search: params.term,
                    page: params.page || 25
                };
            }
        },
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}

$(".vehicle").select2({
    placeholder: "Select Vehicle",
    ajax: {
        url: '/utils/vehicles-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term,
                page: params.page || 25
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$(".customer").select2({
    placeholder: "Select Customer",
    ajax: {
        url: '/utils/customers-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term,
                page: params.page || 25
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".broker").select2({
    placeholder: "Select Supplier",
    ajax: {
        url: '/broker/broker-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term,
                page: params.page || 25
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".datetime").datetimepicker({
    format: "dd-M-yyyy HH:ii P",
    showMeridian: true,
    autoclose: true,
    todayBtn: true,
    onClose: function () {
        $('.custom-datepicker').parsley().validate();
    }
}).change(function () {
    $('.custom-datepicker').parsley().validate();
});