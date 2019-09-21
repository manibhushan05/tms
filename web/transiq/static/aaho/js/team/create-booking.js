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

sourceOffice()
function sourceOffice() {
    $("#source_office").select2({
        placeholder: "Select Source Office",
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
        placeholder: "Select Delivery Office",
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
var BILLING_TYPE_COMMISION = $("#billing_type_commission");
customerWhoMakePayment();
function customerWhoMakePayment() {
    CUSTOMER_WHO_MAKE_PAYMENT.select2({
        placeholder: "Select Customer who will make payment",
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
}

customerWhoPlacedOrder();
function customerWhoPlacedOrder() {
    CUSTOMER_WHO_PLACED_ORDER.select2({
        placeholder: "Select Customer who has placed order",
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
        var sme_id = CUSTOMER_WHO_PLACED_ORDER.val();
        $.ajax({
            url: "/team/contract-customer-data/",
            type: 'GET',
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
        }).fail(function (jqXHR, status) {
            alert('Invalid Customer Selected');
        });
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
            else if (CUSTOMER_WHO_MAKE_PAYMENT.val() === '') {
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

$('#vehicle_number').on("change", function () {
    var vehicle_id = $('#vehicle_number').val();
    if (!$(this).parsley().isValid()) {
        return false;
    }
    $.ajax({
        url: "/owner/vehicle-data/",
        type: 'GET',
        data: {
            'vehicle_id': vehicle_id
        }
    }).done(function (response, status) {
        var owner_key_count = Object.keys(response.msg.owner).length;
        var vehicle_category_key_count = Object.keys(response.msg.vehicle_category).length;
        if (owner_key_count === 3) {
            $('#truck_owner_name').select2({
                placeholder: "Select Truck Owner",
                allowClear: false
            }).append('<option value=' + response.msg.owner.id + ' selected>' + response.msg.owner.name + ', ' + response.msg.owner.phone + '</option>');
        }
        if (vehicle_category_key_count === 2) {
            $('#type_of_vehicle').select2('destroy').select2({
                placeholder: "Select Vehicle",
                allowClear: false
            }).append('<option value=' + response.msg.vehicle_category.id + ' selected>' + response.msg.vehicle_category.vehicle_category + '</option>');
        }
    }).fail(function (jqXHR, status) {
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

$('#btn-booking-reset').click(function () {
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
    window.location.href = '/team/fetch-full-booking-data-page/';
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
        else {
            $.notify(response['msg'], {
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


$('#btn-generate-lr-finish').click(function (e) {
    var generate_lr_and_finish = $('#fetch-generate-lr-form');
    if (!generate_lr_and_finish.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    $('#generate-booking-and-finish').val('quick_full_booking');
    NProgress.start();
    var data = generate_lr_and_finish.serialize();
    $.ajax({
        url: "/team/place-full-booking/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        $.notify({
            title: response['msg'],
            button: 'New Booking'
        }, {
                style: 'foo',
                autoHide: false,
                clickToHide: false,
                position: "top center",
                autoHideDelay: 1000
            });
        NProgress.done();
    }).fail(function (jqXHR, status) {
        $.notify('Failed', {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});

$('#btn-quick-commission-booking').click(function (e) {
    var quick_commission_booking_form = $('#quick-commission-booking-form');
    if (!quick_commission_booking_form.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    $('#generate-booking-and-finish').val('quick_commission_booking');
    NProgress.start();
    var data = quick_commission_booking_form.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/commission-manual-booking-create/",
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
        if (jqXHR.status === 400) {
            redirectToLogin(error);
        }
        else {
            $.notify(response['msg'], {
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


$('#btn-detailed-lr-finish').click(function (e) {
    var generate_lr_and_finish = $('#detailed-booking-form');
    if (!generate_lr_and_finish.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = generate_lr_and_finish.serialize();
    $.ajax({
        url: "/team/place-full-booking/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        $.notify({
            title: response['msg'],
            button: 'New Booking'
        }, {
                style: 'foo',
                autoHide: false,
                clickToHide: false,
                position: "top center",
                autoHideDelay: 1000
            });

        NProgress.done();
        setTimeout(function () {
            window.location.href = '/team/fetch-full-booking-data-page/';
        }, 4000);
    }).fail(function (jqXHR, status) {
        $.notify('Failed', {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});


$('#btn-detailed-commission_booking').click(function (e) {
    var detailed_commission_booking_form = $('#quick-commission-booking-form');
    if (!detailed_commission_booking_form.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = detailed_commission_booking_form.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/page/detailed-commission-booking/",
        type: 'get',
        dataType: 'html',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {
        NProgress.done();
        $('.right_col').html(response);
        $("html, body").animate({ scrollTop: 0 }, "slow");
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === 400) {
            redirectToLogin(error);
        }
        else {
            $.notify(response['msg'], {
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

$('#btn-commision-booking-reset').click(function (e) {
    e.preventDefault();
    resetCommisionBookingForm();
});

function resetCommisionBookingForm() {
    $('#quick-commission-booking-form').parsley().reset();
    $('#quick-commission-booking-form')[0].reset();
    $('#type_of_vehicle').text('');
    $('#truck_driver').text('');
    $('#supplier_name').text('');
    $('#truck_owner_name').text('');
    $('#billing_type_commision').text('');
    $('#delivery_office').text('');
    $('#source_office').text('');
    $('.city').text('');
    $('.customer').text('');
    truckCategory();
    supplierName();
    truckDriver();
    truckOwner();
    aahoOffice();
    city();
    customerWhoPlacedOrderCommision();
    $('#billing_type_commision').append('<option value=""></option>' +
        '<option value="T.B.B.">T.B.B.</option>' +
        '<option value="To Pay">To Pay</option>' +
        '<option value="Paid">Paid</option>');
    commisionBillingType();
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

commisionBillingType();

function commisionBillingType() {
    BILLING_TYPE_COMMISION.select2({
        placeholder: "Select Billing Type",
        allowClear: false
    }).change(function () {
        $(this).parsley().validate();
    });
}