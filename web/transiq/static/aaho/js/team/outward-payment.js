/**
 * Created by mani on 17/4/17.
 */
$(document).ready(function () {

    function isInArray(target, array) {
        /* Caching array.length doesn't increase the performance of the for loop on V8 (and probably on most of other major engines) */
        for (var i = 0; i < array.length; i++) {
            if (array[i] === target) {
                return true;
            }
        }
        return false;
    }

    $("#payment_office").select2({
        placeholder: "select aaho payment office",
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
    });

    $('#openOutwardPaymentModal').click(function (e) {
        var form_id = $('#update-full-booking-form');
        if (form_id[0]) {
            form_id.parsley().validate();
            if (!form_id.parsley().isValid()) {
                return true;
            }
            $('#full-booking-outward-payment-form')[0].reset();
            $('#outward-payment-modal').modal('show');
        } else {
            var commissionBookingForm = $('#update-commission-booking-form');
            commissionBookingForm.parsley().validate();
            if (!commissionBookingForm.parsley().isValid()) {
                return true;
            }
            $('#commission-booking-outward-payment-form')[0].reset();
            $('#outward-payment-modal').modal('show');
        }

    });

    var OUTWARD_PAYMENT_MODE_ID = $('#outward_payment_mode');
    var payment_mode_id = $('#payment_mode');
    $("#bank_account_number").select2({
        placeholder: "Select a Bank Account Number",
        // ajax: {
        //     method: "GET",
        //     url: '/api/utils-bank-list/?status=active',
        //     headers: {"Authorization": localStorage.getItem('token')},
        //     delay: 250,
        //     data: function (params) {
        //         return {
        //             search: params.term
        //         };
        //     },
        //     processResults: function (data) {
        //         var officeArray = [];
        //         $.each(data.data, function (key, value) {
        //             officeArray.push({id: value.id, text: value.account_number})
        //         });
        //         return {results: officeArray};
        //     },
        //     error: function (jqXHR, status, error) {
        //         if (jqXHR.status === "401") {
        //             redirectToLogin(error);
        //         }
        //     }
        // },
        allowClear: true

    }).change(function () {
        $(this).parsley().validate();
    });
    $("#pick-booking-lr").select2({
        maximumSelectionLength: 1,
        ajax: {
            method: "GET",
            url: '/api/tiny-manual-booking-list/?queryset=outward_payment',
            headers: {"Authorization": localStorage.getItem('token')},
            delay: 250,
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var officeArray = [];
                $.each(data.data, function (key, value) {
                    officeArray.push({id: value.id, text: value.booking_id + ' (' + value.lr_numbers + ')'})
                });
                return {results: officeArray};
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status === "401") {
                    redirectToLogin(error);
                }
            }
        },
        placeholder: "Please add all associated LR(s)",
        allowClear: true
    }).change(function () {

        $(this).parsley().validate();
        $.ajax({
            url: "/api/manual-booking-retrieve/" + $("#pick-booking-lr").val() + '/',
            type: 'GET',
            dataType: 'json',
            contentType: 'application/json',

            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
            }
        }).done(function (response, status) {

            var bank_accounts = $('#bank_account_number');
            bank_accounts = bank_accounts.empty();
            bank_accounts.append('<option></option>');
            $.each(response['bank_accounts'], function (index, value) {
                bank_accounts.append('<option value=' + value["id"] + '>' + value["name"]+', '+value["account_number"] +', '+value["ifsc"]+ '</option>')
            });


        }).fail(function (jqXHR, status, error) {
            $('#pick-booking-lr').val([]);

        });


    });


    $("#fuel_card_number").select2({
        placeholder: "Select a Fuel Card Number",
        ajax: {
            url: '/api/owner-fuel-card-list/',
            delay: 250,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
            },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var cardArray = [];
                $.each(data.data, function (key, value) {
                    cardArray.push({id: value.id, text: value.text})
                });
                return {results: cardArray};
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


    $("#fuel_card_area").hide();
    $("#cash_mode_area").hide();

    $("#bank_account_area").hide();


    $("#btn_generate_owner_receipt").click(function () {
        $("#submit_type").val("generate_owner_receipt");
    });


    $('#outward_payment_date').click(function () {
        if (OUTWARD_PAYMENT_MODE_ID.val() === '') {
            alert('Please Select Mode of Payment');
        }
    });

    OUTWARD_PAYMENT_MODE_ID.select2({
        placeholder: "Select mode of payment",
        allowClear: true
    }).change(function () {
        $(this).parsley().validate();
        var PAYMENT_DATE = $('#outward_payment_date');
        if ($(this).val() === "fuel_card") {
            $("#bank_account_area").hide();
            $('#bank_account_number').prop('required', false);
            $("#fuel_card_area").show();
            $("#cash_mode_area").hide();
            $('#fuel_card_number').prop('required', true);
            $('#payment_office').prop('required', false);
        } else if ($(this).val() === "bank_transfer") {
            $("#bank_account_area").show();
            $('#bank_account_number').prop('required', true);
            $("#fuel_card_area").hide();
            $("#cash_mode_area").hide();
            $('#fuel_card_number').prop('required', false);
            $('#payment_office').prop('required', false);
        } else if ($(this).val() === "cash") {
            $("#bank_account_area").hide();
            $('#bank_account_number').prop('required', false);
            $("#fuel_card_area").hide();
            $("#cash_mode_area").show();
            $('#fuel_card_number').prop('required', false);
            $('#payment_office').prop('required', true);
        } else {
            $("#fuel_card_area").hide();
            $("#cash_mode_area").hide();
            $("#bank_account_area").hide();
            $('#bank_account_number').prop('required', false);
            $('#fuel_card_number').prop('required', false);
            $('#payment_office').prop('required', false);
        }

        if (OUTWARD_PAYMENT_MODE_ID.val() === 'bank_transfer') {
            PAYMENT_DATE.datepicker("destroy");
            PAYMENT_DATE.datepicker({
                format: "dd-M-yyyy",
                autoclose: true,
                todayHighlight: true,
                startDate: moment().add(0, 'days').format("DD-MMM-YYYY"),
                endDate: moment().add(15, 'days').format("DD-MMM-YYYY"),
                daysOfWeekDisabled: '0'

            }).on("changeDate", function (e) {

                PAYMENT_DATE.parsley().validate();
                if (PAYMENT_DATE.parsley().isValid()) {
                    $.ajax({
                        url: "/api/payment-mode-date-message/",
                        type: 'GET',
                        headers: {"Authorization": localStorage.getItem('token')},
                        data: {
                            'payment_mode': OUTWARD_PAYMENT_MODE_ID.val(),
                            'account_id': $('#bank_account_number').val(),
                            'fuel_card': $("#fuel_card_number").val(),
                            'payment_date': PAYMENT_DATE.val(),
                            'amount': $('#actual_amount').val()
                        }
                    }).done(function (response, status) {
                        payment_mode_id.val(response['data']['mode']);
                        $('#outward_pymt_date_warning').text(response['msg'])
                    }).fail(function (jqXHR, status, error) {
                        if (jqXHR.status === "401") {
                            redirectToLogin(error);
                        }
                    });
                }
            });
        } else if (isInArray(OUTWARD_PAYMENT_MODE_ID.val(), ['cash', 'happay', 'cheque'])) {
            PAYMENT_DATE.datepicker("destroy");
            PAYMENT_DATE.datepicker({
                format: "dd-M-yyyy",
                todayBtn: "linked",
                autoclose: true,
                todayHighlight: true,
                startDate: moment().add(-7, 'days').format("DD-MMM-YYYY"),
                endDate: moment().add(0, 'days').format("DD-MMM-YYYY")
            }).on("changeDate", function (e) {
                PAYMENT_DATE.parsley().validate();
                if (PAYMENT_DATE.parsley().isValid()) {
                    $.ajax({
                        url: "/api/payment-mode-date-message/",
                        type: 'GET',
                        headers: {"Authorization": localStorage.getItem('token')},
                        data: {
                            'payment_mode': OUTWARD_PAYMENT_MODE_ID.val(),
                            'account_id': $('#bank_account_number').val(),
                            'fuel_card': $("#fuel_card_number").val(),
                            'payment_date': PAYMENT_DATE.val(),
                            'amount': $('#actual_amount').val()
                        }
                    }).done(function (response, status) {
                        payment_mode_id.val(response['data']['mode']);
                        $('#outward_pymt_date_warning').text(response['msg'])
                    }).fail(function (jqXHR, status, error) {
                        if (jqXHR.status == "401") {
                            redirectToLogin(error);
                        }
                    });
                }
            });
        } else if (isInArray(OUTWARD_PAYMENT_MODE_ID.val(), ['adjustment'])) {
            PAYMENT_DATE.datepicker("destroy");
            PAYMENT_DATE.datepicker({
                format: "dd-M-yyyy",
                todayBtn: "linked",
                autoclose: true,
                todayHighlight: true,
                startDate: moment().add(0, 'days').format("DD-MMM-YYYY"),
                endDate: moment().add(0, 'days').format("DD-MMM-YYYY")
            }).on("changeDate", function (e) {
                PAYMENT_DATE.parsley().validate();
                payment_mode_id.val('adjustment');
            });
        } else if (isInArray(OUTWARD_PAYMENT_MODE_ID.val(), ['fuel_card'])) {
            PAYMENT_DATE.datepicker("destroy");
            PAYMENT_DATE.datepicker({
                format: "dd-M-yyyy",
                todayBtn: "linked",
                autoclose: true,
                todayHighlight: true,
                startDate: moment().add(-2, 'days').format("DD-MMM-YYYY"),
                endDate: moment().add(10, 'days').format("DD-MMM-YYYY")
            }).on("changeDate", function (e) {
                PAYMENT_DATE.parsley().validate();
                if (PAYMENT_DATE.parsley().isValid()) {
                    $.ajax({
                        url: "/api/payment-mode-date-message/",
                        type: 'GET',
                        headers: {"Authorization": localStorage.getItem('token')},
                        data: {
                            'payment_mode': OUTWARD_PAYMENT_MODE_ID.val(),
                            'account_id': $('#bank_account_number').val(),
                            'fuel_card': $("#fuel_card_number").val(),
                            'payment_date': PAYMENT_DATE.val(),
                            'amount': $('#actual_amount').val()
                        }
                    }).done(function (response, status) {
                        payment_mode_id.val(response['data']['mode']);
                        $('#outward_pymt_date_warning').text(response['msg'])
                    }).fail(function (jqXHR, status, error) {
                        if (jqXHR.status === "401") {
                            redirectToLogin(error);
                        }
                    });
                }
            });
        } else {
            PAYMENT_DATE.datepicker("destroy");
            PAYMENT_DATE.datepicker({
                format: "dd-M-yyyy",
                todayBtn: "linked",
                autoclose: true,
                todayHighlight: true,
                startDate: moment().add(-7, 'days').format("DD-MMM-YYYY"),
                endDate: moment().add(0, 'days').format("DD-MMM-YYYY")
            }).on("changeDate", function (e) {
                PAYMENT_DATE.parsley().validate();
                if (PAYMENT_DATE.parsley().isValid()) {
                    $.ajax({
                        url: "/api/payment-mode-date-message/",
                        type: 'GET',
                        headers: {"Authorization": localStorage.getItem('token')},
                        data: {
                            'payment_mode': OUTWARD_PAYMENT_MODE_ID.val(),
                            'account_id': $('#bank_account_number').val(),
                            'fuel_card': $("#fuel_card_number").val(),
                            'payment_date': PAYMENT_DATE.val(),
                            'amount': $('#actual_amount').val()
                        }
                    }).done(function (response, status) {
                        $('#outward_pymt_date_warning').text(response['msg'])
                    }).fail(function (jqXHR, status, error) {
                        if (jqXHR.status == "401") {
                            redirectToLogin(error);
                        }
                    });
                }
            });
        }

    });

    $('#btn-new-outward-payment').click(function (e) {

        var OUTWARD_PAYMENT_FORM = $('#new-outward-payment-form');
        if (!OUTWARD_PAYMENT_FORM.parsley().isValid()) {
            return true;
        }
        e.preventDefault();
        var data = OUTWARD_PAYMENT_FORM.find(':input').filter(function () {
            return $.trim(this.value).length > 0
        }).serializeJSON();
        $.ajax({
            url: "/api/team-outward-payment-create/",
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
            }, 1000);
        }).fail(function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            } else {
                $.notify('Fail', {
                    position: "top center",
                    autoHideDelay: 1000,
                    clickToHide: true,
                    className: 'error'
                });
            }

            NProgress.done();
        });
    });

    var OUTWARD_PAYMENT_MOBILE_FORM = $('#mobile-outward-payment-form');
    $('#btn-mobile-outward-payment').click(function (e) {
        if (!OUTWARD_PAYMENT_MOBILE_FORM.parsley().isValid()) {
            return true;
        }
        var formData = OUTWARD_PAYMENT_MOBILE_FORM.serialize();
        NProgress.start();
        $.ajax({
            url: "/mobile/outward-payment/",
            type: 'POST',
            data: formData
        }).done(function (response, status) {
            $.notify(response['msg'], {
                position: "top center",
                autoHideDelay: 1000,
                clickToHide: true,
                className: 'success'
            });
            $(OUTWARD_PAYMENT_MOBILE_FORM).each(function () {
                this.reset();
            });
            NProgress.done();
            setTimeout(function () {
                location.reload();
            }, 1000);
        }).fail(function (jqXHR, status) {
            $.notify(JSON.parse(jqXHR.responseText)['msg'], {
                position: "top center",
                autoHideDelay: 1000,
                clickToHide: true,
                className: 'error'
            });
            NProgress.done();
        });
    });
    $('#is_refund_amount').change(function () {
        if (this.checked) {
            $('#send_sms_supplier').attr("disabled", true);

        } else {
            $('#send_sms_supplier').removeAttr("disabled");
        }
    });

    $('#full-booking-outward-submit').click(function () {
        var OUTWARD_PAYMENT_FORM = $('#full-booking-outward-payment-form');
        if (!OUTWARD_PAYMENT_FORM[0]) {
            OUTWARD_PAYMENT_FORM = $('#commission-booking-outward-payment-form');
        }
        if (!OUTWARD_PAYMENT_FORM.parsley().isValid()) {
            return true;
        } else {
            if ($("#is_refund_amount").is(':checked') && (parseInt($('#actual_amount').val()) > (parseInt($('#refundable_amount').val()) - parseInt($('#refundable_paid_amount').val())))) {
                alert("Refundable amount can not exceed " + (parseInt($('#refundable_amount').val()) - parseInt($('#refundable_paid_amount').val())));
                $('#actual_amount').val('');
                return false;
            } else {
                $('#outward_pymt_date_warning').hide();
            }
        }
        var op_balance_display = parseFloat($('#op_balance_display_label').text());
        var actualAmount = parseFloat($('#actual_amount').val());
        if (!$("#is_refund_amount").is(':checked') && actualAmount > op_balance_display) {
            alert("Actual amount can not exceed balance amount ");
            $(this).val('');
            $('#actual_amount').focus();
            return false;
        }
        $('#full-booking-outward-submit').attr('disabled', true);
        var fullBookingDataStatus = save_full_booking_data();
        if (fullBookingDataStatus) {
            $('#outward-payment-modal').modal('hide');
            var data = OUTWARD_PAYMENT_FORM.find(':input').filter(function () {
                return $.trim(this.value).length > 0
            }).serializeJSON();
            $.ajax({
                url: "/api/team-outward-payment-create/",
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
                }, 1000);
                $('#full-booking-outward-submit').attr('disabled', true);

            }).fail(function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                } else {
                    $.notify('Fail', {
                        position: "top center",
                        autoHideDelay: 1000,
                        clickToHide: true,
                        className: 'error'
                    });
                }
                NProgress.done();
                $('#full-booking-outward-submit').attr('disabled', true);

            });
            return false
        }
        $('#full-booking-outward-submit').attr('disabled', true);

    });
    $('button#commission-booking-outward-submit').click(function (e) {
        var OUTWARD_PAYMENT_FORM = $('#commission-booking-outward-payment-form');
        if (!OUTWARD_PAYMENT_FORM.parsley().isValid()) {
            return true;
        }
        var fullBookingDataStatus = save_full_booking_data();
        if (fullBookingDataStatus) {
            $('#outward-payment-modal').modal('hide');
            var data = OUTWARD_PAYMENT_FORM.find(':input').filter(function () {
                return $.trim(this.value).length > 0
            }).serializeJSON();
            $.ajax({
                url: "/api/team-outward-payment-create/",
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
                }, 1000);
                location.reload();
                $('#full-booking-outward-submit').attr('disabled', true);

            }).fail(function (jqXHR, status, error) {
                if (jqXHR.status == "401") {
                    redirectToLogin(error);
                } else {
                    $.notify('Fail', {
                        position: "top center",
                        autoHideDelay: 1000,
                        clickToHide: true,
                        className: 'error'
                    });
                }
                NProgress.done();
                $('#full-booking-outward-submit').attr('disabled', true);

            });
            return false
        }
        $('#full-booking-outward-submit').attr('disabled', true);
    });
});

