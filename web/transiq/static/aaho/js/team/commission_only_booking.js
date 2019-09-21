/**
 * Created by mani on 10/10/16.
 */
$(document).ready(function () {
    $('#lrdate').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $('#shipmentdate').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $('#party_invoice_date').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $('#insurance_date').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $(".select2_single").select2({
        placeholder: "Select a city",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".username").select2({
        placeholder: "Select a Customer",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".vehicle_number_fetch").select2({
        placeholder: "Select a Vehicle",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".source_office").select2({
        placeholder: "Select Source Office",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".delivery_office").select2({
        placeholder: "Select Delivery Office",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".billing_type").select2({
        placeholder: "Select a Billing Type",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".consignor_city").select2({
        placeholder: "Select a Consignor City",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".consignee_city").select2({
        placeholder: "Select a Consignee City",
        allowClear: true
    });
    $(".select2_group").select2({});
});

$('.form_datetime').datetimepicker({
    language: 'en',
    weekStart: 1,
    todayBtn: 1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 2,
    forceParse: 0,
    showMeridian: 1
});


$(".form_datetime").datetimepicker({
    format: "dd MM yyyy - HH:ii P",
    showMeridian: true,
    autoclose: true,
    todayBtn: true
});

$(document).ready(function () {
    $('#dl_validity').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $(".truck_type").select2({
        placeholder: "Select a Truck Type",
        allowClear: true
    });
    $(".select2_group").select2({});
});


$(document).ready(function () {
    $(".pod_status").select2({
        placeholder: "Select a POD Status",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".outward_payment_status").select2({
        placeholder: "Select a outward payment status",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".inward_payment_status").select2({
        placeholder: "Select a inward payment status",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$("#type_of_vehicle").change(function () {
    $(this).parsley().validate();
});
$("#billing_type").change(function () {
    $(this).parsley().validate();
});
$("#pod_status").change(function () {
    $(this).parsley().validate();
});
$("#outward_payment_status").change(function () {
    $(this).parsley().validate();
});
$("#inward_payment_status").change(function () {
    $(this).parsley().validate();
});
$("#source_office_fetch").change(function () {
    $(this).parsley().validate();
});
$("#destination_office_fetch").change(function () {
    $(this).parsley().validate();
});
$("#shipment_datetime").change(function () {
    $(this).parsley().validate();
});
$("#username_sme").change(function () {
    $(this).parsley().validate();
});
$("#vehicle_number_fetch").change(function () {
    $(this).parsley().validate();
});
$(document).ready(function () {
    $("input").change(function () {
        var additional_charges_passed_on = parseInt($('#loading_charges').val()) + parseInt($('#unloading_charges').val()) + parseInt($('#detention_charges').val()) + parseInt($('#other_charges_for_company').val());
        var deductions = parseInt($('#commission').val()) + parseInt($('#lr_cost').val()) + parseInt($('#deduction_for_advance').val()) + parseInt($('#deduction_for_balance').val()) + parseInt($('#any_other_deduction').val());
        var party_charged_weight = parseFloat($('#charged_weight').val());
        var supplier_charged_weight = parseFloat($('#supplier_charged_weight').val());
        var supplier_rate = parseInt($('#supplier_rate').val());
        var party_rate = parseInt($('#party_rate').val());
        var freight_to_owner = supplier_rate * supplier_charged_weight;
        var freight_from_company = party_rate * party_charged_weight;
        $("#additional_charge_passed_on").val(additional_charges_passed_on);
        $("#freight_owner").val(freight_to_owner);
        $("#freight_from_company").val(freight_from_company);
        $("#total_amount_to_owner").val(freight_to_owner + additional_charges_passed_on - deductions);
        $("#total_amount_to_party").val(freight_from_company);
    });
});
