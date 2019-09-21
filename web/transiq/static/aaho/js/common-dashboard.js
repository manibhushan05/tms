supplierName();
function supplierName() {
    $(".truck-suppliers").select2({
        placeholder: "Select Supplier Name",
        ajax: {
            url: '/api/supplier-supplier-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var brokerArray = [];
                $.each(data.data, function (key, value) {
                    brokerArray.push({ id: value.id, text: value.name + ' ' + value.phone })
                });
                return { results: brokerArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
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
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}
$(".state").select2({
    placeholder: "Select State",
    ajax: {
        url: '/utils/states-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term

            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

aahoOffice();
function aahoOffice() {
    $(".aaho-office").select2({
        placeholder: "Select Aaho Office",
        ajax: {
            method: "GET",
            url: '/api/utils-aaho-office-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var catArray = [];
                $.each(data.data, function (key, value) {
                    catArray.push({ id: value.id, text: value.branch_name })
                });
                return { results: catArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
            }
        },
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}


truckCategory();
function truckCategory() {
    $(".truck-category").select2({
        placeholder: "Select Vehicle Category",
        ajax: {
            method: "GET",
            url: '/api/supplier-vehicle-category-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var catArray = [];
                $.each(data.data, function (key, value) {
                    catArray.push({ id: value.id, text: value.vehicle_type })
                });
                return { results: catArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
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
            url: '/api/supplier-supplier-driver-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var driverArray = [];
                $.each(data.data, function (key, value) {
                    driverArray.push({ id: value.id, text: value.name + ' ' + value.phone })
                });
                return { results: driverArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status === "401") {
                    redirectToLogin(error);
                }
            }
        },
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });
}


truckOwner();
function truckOwner() {
    $(".truck-owner").select2({
        placeholder: "Select Truck Owner",
        ajax: {
            url: '/api/supplier-supplier-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var ownerArray = [];
                $.each(data.data, function (key, value) {
                    ownerArray.push({ id: value.id, text: value.name + ',' + value.phone })
                });
                return { results: ownerArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status === "401") {
                    redirectToLogin(error);
                }
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
                search: params.term
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
        url: '/api/sme-sme-list/',
        headers: { "Authorization": localStorage.getItem('token') },
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var custArray = [];
            $.each(data.data, function (key, value) {
                custArray.push({ id: value.id, text: value.sme_profile.name + ' ,' + value.company_code })
            });
            return { results: custArray };
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status === "401") {
                redirectToLogin(error);
            }
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
                search: params.term
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
    pickerPosition: "bottom-left",
    onClose: function () {
        $('.custom-datepicker').parsley().validate();
    }
}).change(function () {
    $('.custom-datepicker').parsley().validate();
});

gpsDevice();
function gpsDevice() {
    $(".gps_device").select2({
        placeholder: "Select GPS Device",
        ajax: {
            method: "GET",
            url: '/api/driver-gps-device-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var gpsArray = [];
                $.each(data.data, function (key, value) {
                    gpsArray.push({ id: value.id, text: value.device_id + ', ' + value.device_provider_data.name })
                });
                return { results: gpsArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
            }
        },
        allowClear: true
    }).change(function () {
    });
}