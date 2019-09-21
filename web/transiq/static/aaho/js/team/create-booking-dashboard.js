/**
 * Created by mani on 9/5/17.
 */

/**
 * Created by mani on 10/5/17.
 */
//Fetch Booking Data
var GST_LIABILITY_ID = $('#gst_liability');
var CUSTOMER_WHO_MAKE_PAYMENT = $('#input-customer-make-payment');
var CUSTOMER_MAKE_PAYMENT_LABEL = $('#label-customer-make-payment');

sourceOffice();
function sourceOffice() {
    $("#source_office").select2({
        placeholder: "Select Source Office",
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
                var officeArray = [];
                $.each(data.data, function (key, value) {
                    officeArray.push({ id: value.id, text: value.branch_name })
                });
                return { results: officeArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
            }
        },
        allowClear: true
    }).change(function () {
        if ($.inArray($("#delivery_office").val(), ['2', '3']) !== -1 || $.inArray($("#source_office").val(), ['2', '3']) !== -1) {
            $('#is_print_payment_mode_instruction_div').show();
            $('#is_print_payment_mode_instruction').prop('required', true);
        }
        else {
            $('#is_print_payment_mode_instruction_div').hide();
            $('#is_print_payment_mode_instruction').removeAttr('required');
        }
        $(this).parsley().validate();
    });
}

deliveryOffice()
function deliveryOffice() {
    $("#delivery_office").select2({
        placeholder: "Select Source Office",
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
                var officeArray = [];
                $.each(data.data, function (key, value) {
                    officeArray.push({ id: value.id, text: value.branch_name })
                });
                return { results: officeArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
            }
        },
        allowClear: true
    }).change(function () {
        if ($.inArray($("#delivery_office").val(), ['2', '3']) !== -1 || $.inArray($("#source_office").val(), ['2', '3']) !== -1) {
            $('#is_print_payment_mode_instruction_div').show();
            $('#is_print_payment_mode_instruction').prop('required', true);
        }
        else {
            $('#is_print_payment_mode_instruction_div').hide();
            $('#is_print_payment_mode_instruction').removeAttr('required');
        }
        $(this).parsley().validate();
    });
}

GSTLiability();
function GSTLiability() {
    GST_LIABILITY_ID.select2({
        placeholder: "Select GST Liable",
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
        if (GST_LIABILITY_ID.val() === 'consignor' || GST_LIABILITY_ID.val() === 'consignee') {
            CUSTOMER_MAKE_PAYMENT_LABEL.text('Customer who will make payment *');
            CUSTOMER_WHO_MAKE_PAYMENT.prop('required', true);
        }
        else {
            CUSTOMER_MAKE_PAYMENT_LABEL.text('Customer who will make payment');
            CUSTOMER_WHO_MAKE_PAYMENT.removeAttr('required');
        }
    });
}

var CUSTOMER_WHO_PLACED_ORDER = $("#customer_name");
var BILLING_TYPE = $("#billing_type");
var BILLING_TYPE_COMMISION = $("#billing_type_commision");

customerWhoMakePayment();
function customerWhoMakePayment() {
    CUSTOMER_WHO_MAKE_PAYMENT.select2({
        placeholder: "Select Customer who will make payment",
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

customerWhoPlacedOrder();
function customerWhoPlacedOrder() {
    CUSTOMER_WHO_PLACED_ORDER.select2({
        placeholder: "Select Customer who has placed order",
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
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                }
            }
        },
        allowClear: true
    }).change(function () {
        var sme_id = CUSTOMER_WHO_PLACED_ORDER.val();
        $.ajax({
            url: "/api/customer-contract-data/",
            type: 'GET',
            headers: { "Authorization": localStorage.getItem('token') },
            data: {
                'sme_id': sme_id
            }
        }).done(function (response, status) {
            if (response['is_contract'] === true) {
                BILLING_TYPE.empty().append('<option value="contract">Contract</option>');
                CUSTOMER_WHO_MAKE_PAYMENT.select2('destroy').select2({
                    placeholder: "Select Customer who has placed order",
                    allowClear: false
                }).append('<option value=' + response['id'] + ' selected>' + response['name'] + '</option>');
                $('#party_rate').val(0).prop('readonly', true);
            } else {
                $('#party_rate').prop('readonly', false);
            }
        }).fail(function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
            alert('Invalid Customer Selected');
        });
        $(this).parsley().validate();
    });
}

customerWhoPlacedOrderCommision();

function customerWhoPlacedOrderCommision() {
    $('#customer_name_commision').select2({
        placeholder: "Select Customer who has placed order",
        ajax: {
            url: '/api/sme-sme-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            processResults: function (data) {
                var custArray = [];
                $.each(data.data, function (key, value) {
                    custArray.push({ id: value.id, text: value.sme_profile.name + ' ,' + value.company_code })
                });
                return { results: custArray };
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

billingType();

function billingType() {
    BILLING_TYPE.select2({
        placeholder: "Select Billing Type",
        allowClear: false
    }).change(function () {
        if (BILLING_TYPE.val() === 'contract') {
            CUSTOMER_WHO_MAKE_PAYMENT.prop('required', true);
            if (CUSTOMER_WHO_PLACED_ORDER.val() === '') {
                alert('Please select customer who has placed order');
                BILLING_TYPE.val('').trigger('change');
                CUSTOMER_WHO_PLACED_ORDER.val('').trigger('change');
            }
            else if (CUSTOMER_WHO_MAKE_PAYMENT.val() === '' || CUSTOMER_WHO_MAKE_PAYMENT.val() === null || CUSTOMER_WHO_MAKE_PAYMENT.val() === undefined) {
                alert('Please select customer who will make payment');
                BILLING_TYPE.val('').trigger('change');
                CUSTOMER_WHO_MAKE_PAYMENT.val('').trigger('change');
            } else if (CUSTOMER_WHO_MAKE_PAYMENT.val() !== CUSTOMER_WHO_PLACED_ORDER.val()) {
                CUSTOMER_WHO_PLACED_ORDER.val('').trigger('change');
                CUSTOMER_WHO_MAKE_PAYMENT.val('').trigger('change');
                BILLING_TYPE.val('').trigger('change');
                alert('For contract billing both customer must be same');
            }
            $('#party_rate').val(0).prop('readonly', true);
        } else {
            CUSTOMER_WHO_MAKE_PAYMENT.removeAttr('required');
            $('#party_rate').val('').prop('readonly', false);
        }
        $(this).parsley().validate();
    });
}

commisionBillingType();

function commisionBillingType() {
    BILLING_TYPE_COMMISION.select2({
        placeholder: "Select Billing Type",
        allowClear: false
    }).change(function () {
        $(this).parsley().validate();
    });
}

$('#vehicle_number').on("change", function () {
    if (!$(this).parsley().isValid()) {
        return false
    }
    var vehicle_id = $('#vehicle_number').val();
    $.ajax({
        url: "/api/supplier-vehicle-list/",
        type: 'GET',
        headers: { "Authorization": localStorage.getItem('token') },
        data: {
            'vehicle_number': vehicle_id.replace(/[\W_]/g, "")
        }
    }).done(function (response, status) {
        console.log(response);
        var owner_data;
        var vehicle_category_data;
        if (response.count > 0) {
            owner_data = response.data[0].owner_data;
            vehicle_category_data = response.data[0].vehicle_type_data;
        }

        if (owner_data && owner_data['id'] !== -1) {
            $('#truck_owner_name').select2({
                placeholder: "Select Truck Owner",
                allowClear: false
            }).append('<option value=' + owner_data.id + ' selected>' + owner_data.name + ', ' + owner_data.phone + '</option>');
        }
        else {
            $('.truck-owner').text('');
            truckOwner();
        }
        if (vehicle_category_data) {
            $('#type_of_vehicle').select2('destroy').select2({
                placeholder: "Select Vehicle",
                allowClear: false
            }).append('<option value=' + vehicle_category_data.id + ' selected>' + vehicle_category_data.name + '</option>');
        }
        else {
            $(".truck-category").text('');
            truckCategory();
        }
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status == "401") {
            redirectToLogin(error);
        }
        console.log(jqXHR);
    });
});

function resetBookingForm() {
    $('#fetch-generate-lr-form').parsley().reset();
    $('#fetch-generate-lr-form')[0].reset();
    $('#type_of_vehicle').text('');
    $('#supplier_name').text('');
    $('#truck_driver').text('');
    $('#truck_owner_name').text('');
    $('#delivery_office').text('');
    $('#source_office').text('');
    $('.city').text('');
    $('#billing_type').text('');
    $('#gst_liability').text('');
    $('#customer_name').text('');
    $("#customer_name").val('');
    $('#input-customer-make-payment').text('');
    $('#input-customer-make-payment').val('');
    truckCategory();
    supplierName();
    truckDriver();
    truckOwner();
    sourceOffice();
    deliveryOffice();
    city();
    customerWhoMakePayment();
    customerWhoPlacedOrder();
    $('#gst_liability').append('<option value=""></option>' +
        '<option value="consignor">Consignor</option>' +
        '<option value="consignee">Consignee</option>' +
        '<option value="carrier">Transporter</option>' +
        '<option value="exempted">Exempted</option>');

    $('#billing_type').append('<option value=""></option>' +
        '<option value="T.B.B.">T.B.B.</option>' +
        '<option value="To Pay">To Pay</option>' +
        '<option value="Paid">Paid</option>' +
        '<option value="contract">Contract</option>');
    GSTLiability();
    billingType();
    $("#is_print_payment_mode_instruction_div").hide()
}

$('#btn-booking-reset_dashboard').click(function (e) {
    e.preventDefault();
    resetBookingForm();
});

$('#is_print_payment_mode_instruction_div').hide();
$('input').change(function () {
    var supplier_rate = parseInt($('#supplier_rate').val());
    var supplier_weight = parseFloat($('#supplier_charged_weight').val());
    var party_rate = parseInt($('#party_rate').val());
    var party_weight = parseFloat($('#charged_weight').val());
    $('#total_amount_to_party').val(Math.round(party_rate * party_weight));
    $('#total_amount_to_owner').val(Math.round(supplier_rate * supplier_weight));
});

//add a new style 'foo'
$.notify.addStyle('foo', {
    html:
        "<div>" +
        "<div class='clearfix'>" +
        "<div class='title' data-notify-html='title'/>" +
        "<div class='buttons'>" +
        "<button class='yes' data-notify-text='button'></button>" +
        "</div>" +
        "</div>" +
        "</div>"
});

$(document).on('click', '.notifyjs-foo-base .yes', function () {
    //show button text
    // window.location.href = '/team/fetch-full-booking-data-page/';
    //hide notification
    $(this).trigger('notify-hide');
});

$('#btn-generate-lr-finish-dashboard').click(function (e) {
    var generate_lr_and_finish = $('#fetch-generate-lr-form');
    if (!generate_lr_and_finish.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    //  $('#generate-booking-and-finish').val('quick_full_booking');
    NProgress.start();
    var data = generate_lr_and_finish.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/team-manual-booking-create/",
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
        resetBookingForm();
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status == "401") {
            redirectToLogin(error);
        }
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});




