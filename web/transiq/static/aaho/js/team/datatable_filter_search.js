var filterSearchArr = [];
var customfilterSelectUrl = '';
var choiceOPtions;
var multiChkBoxArr = [];

//append html for filters
function dtFilterHtml(appendHtmlId, customfilterSelectUrl) {
    var filterHtml = '';
    customfilterSelectUrl = customfilterSelectUrl;
    filterHtml += '<div class="col-md-12 col-lg-12 col-sm-12 col-xs-12 ">';
    filterHtml += '<span class="filterText">Filters</span>';
    filterHtml += '<a href="javascript:;" class="clearAll pull-right" aria-label="close">CLEAR ALL</a>';
    filterHtml += '</div>';
    filterHtml += '<br/>';

    filterHtml += '<div class="col-md-12 col-lg-12 col-sm-12 col-xs-12 filterdData wrapper">';
    filterHtml += '</div>';
    filterHtml += '<div class="ln-solid col-md-12 col-lg-12 col-sm-12 col-xs-12"></div>';
    filterHtml += '<div class="item form-group col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>';

    filterHtml += '<div class="col-md-3 col-lg-3 col-sm-3 col-xs-12">';
    filterHtml += '<div class="item form-group">'
    filterHtml += '<select class="form-control" id="customFilterSelect">';
    filterHtml += '<option></option>';
    filterHtml += '</select>';
    filterHtml += '</div>';
    filterHtml += '</div>';

    filterHtml += '<div class="col-md-3 col-lg-3 col-sm-3 col-xs-12 filteredInput" >';
    filterHtml += '<input type="text"  class="form-control" id="inputType"  placeholder="Enter value..." />';
    filterHtml += '</div>';

    filterHtml += '<div class="col-md-6 col-lg-6 col-sm-6 col-xs-12 filteredNumber" style="display:none;">';
    filterHtml += '<div class="col-md-6 col-lg-6 col-sm-6 col-xs-12 " >';
    filterHtml += '<input type="number"  class="form-control" id="minNumber"  placeholder="Enter min value..." />';
    filterHtml += '</div>';
    filterHtml += '<div class="col-md-6 col-lg-6 col-sm-6 col-xs-12 " >';
    filterHtml += '<input type="number"  class="form-control" id="maxNumber"  placeholder="Enter max value..." />';
    filterHtml += '</div>';
    filterHtml += '</div>';

    filterHtml += '<div class="col-md-3 col-lg-3 col-sm-3 col-xs-12 divDateRange" style="display:none;" >';
    filterHtml += '<div id="dateRange" style="background: #fff; cursor: pointer; padding: 5px 10px; border: 1px solid #ccc; width: 100%">';
    filterHtml += ' <i class="fa fa-calendar"></i>&nbsp;';
    filterHtml += '<span class="dataRangeVal"></span> <i class="fa fa-caret-down"></i>';
    filterHtml += '</div>';
    filterHtml += '</div>';

    filterHtml += '<div class="col-md-3 col-lg-3 col-sm-3 col-xs-12 filteredSelect" style="display:none;">';
    filterHtml += '<div class="item form-group">';
    filterHtml += '<select  class="form-control" id="filteredSelect">';
    filterHtml += '</select>';
    filterHtml += '</div>';
    filterHtml += '</div>';

    filterHtml += '<div class="col-md-3 col-lg-3 col-sm-3 col-xs-12 filteredMultiSelect" style="display:none;">';
    filterHtml += '<div class="item form-group">';
    filterHtml += '<select  class="form-control" id="customMultiSelect">';
    filterHtml += '</select>';
    filterHtml += '</div>';
    filterHtml += '</div>';

    filterHtml += '<div class="col-md-3 col-lg-3 col-sm-3 col-xs-12">';
    filterHtml += '<button  class="btn btn-mg btn-success"id="tblSearch">Search</button>';
    filterHtml += '</div>';
    $("#" + appendHtmlId + "").html(filterHtml);
    customFilterSelect(customfilterSelectUrl);
}

//dropdown for fields for filter
function customFilterSelect(customfilterSelectUrl) {
    $.ajax({
        url: customfilterSelectUrl,
        headers: { "Authorization": localStorage.getItem('token') },
        dataType: 'json',
    }).done(function (data) {
        var filterArray = [];
        $.each(data.data.criteria, function (key, value) {
            let obj = filterSearchArr && filterSearchArr.find(x => x.name === value.field_name);
            let index = filterSearchArr && filterSearchArr.indexOf(obj);
            if (index < 0) {
                filterArray.push({ id: value.field_name, text: value.display_name, other_data: value })
            }
        });
        $("#customFilterSelect").select2({
            placeholder: "Select Field",
            data: filterArray,
            allowClear: true,
            templateSelection: function (data, container) {
                // Add custom attributes to the <option> tag for the selected option
                if (data.other_data) {
                    if (data.other_data.input_type == 'text') {
                        $(data.element).attr('data-inputtype', data.other_data.input_type);
                        $(data.element).attr('data-fieldname', data.id);
                        $(data.element).attr('data-displayname', data.other_data.display_name);
                        $("#inputType").each(function () {
                            var attributes = $.map(this.attributes, function (item) {
                                return item.name;
                            });
                            var ele = $(this);
                            $.each(attributes, function (i, item) {
                                if (item == 'id' || item == 'class') {
                                }
                                else {
                                    ele.removeAttr(item);
                                }
                            });
                        });
                        $("#inputType").attr('placeholder', data.other_data.placeholder);
                        $("#inputType").attr('type', data.other_data.input_type);
                        $(".filteredInput").show();
                        $(".filteredSelect").hide();
                        $(".filteredMultiSelect").hide();
                        $(".divDateRange").hide();
                        $(".filteredNumber").hide();

                    }
                    else if (data.other_data.input_type == 'number') {
                        $(data.element).attr('data-inputtype', data.other_data.input_type);
                        $(data.element).attr('data-fieldname', data.id);
                        $(data.element).attr('data-displayname', data.other_data.display_name);
                        $("#minNumber").each(function () {
                            var attributes = $.map(this.attributes, function (item) {
                                return item.name;
                            });
                            var ele = $(this);
                            $.each(attributes, function (i, item) {
                                if (item == 'id' || item == 'class' || item == 'placeholder') {
                                }
                                else {
                                    ele.removeAttr(item);
                                }
                            });
                        });
                        $("#minNumber,#maxNumber").attr('type', data.other_data.input_type);
                        $("#minNumber,#maxNumber").attr('data-min', data.other_data.min);
                        $("#minNumber,#maxNumber").attr('data-max', data.other_data.max);
                        $(".filteredInput").hide();
                        $(".filteredSelect").hide();
                        $(".filteredMultiSelect").hide();
                        $(".divDateRange").hide();
                        $(".filteredNumber").show();
                    }
                    else if (data.other_data.input_type == 'select') {
                        $(data.element).attr('data-inputtype', data.other_data.input_type);
                        $(data.element).attr('data-fieldname', data.id);
                        $(data.element).attr('data-displayname', data.other_data.display_name);
                        $(data.element).attr('data-placeholder', data.other_data.placeholder);
                        $(data.element).attr('data-parse', data.other_data.data_parse);
                        $(data.element).attr('data-url', data.other_data.url);
                        $(".filteredInput").hide();
                        $(".filteredSelect").show();
                        $(".divDateRange").hide();
                        $(".filteredNumber").hide();
                        $(".filteredMultiSelect").hide();
                    }
                    else if (data.other_data.input_type == 'multiselect') {
                        $(data.element).attr('data-inputtype', data.other_data.input_type);
                        $(data.element).attr('data-fieldname', data.id);
                        $(data.element).attr('data-displayname', data.other_data.display_name);
                        $(data.element).attr('data-placeholder', data.other_data.placeholder);
                        $(data.element).attr('data-parse', data.other_data.data_parse);
                        $(data.element).attr('data-url', data.other_data.url);
                        $(".filteredInput").hide();
                        $(".filteredSelect").show();
                        $(".divDateRange").hide();
                        $(".filteredNumber").hide();
                        $(".filteredMultiSelect").show();
                        $(".filteredSelect").hide();
                        multiChkBoxArr = [];


                    }
                    else if (data.other_data.input_type == 'choices') {
                        $(data.element).attr('data-inputtype', data.other_data.input_type);
                        $(data.element).attr('data-fieldname', data.id);
                        $(data.element).attr('data-displayname', data.other_data.display_name);
                        $(data.element).attr('data-placeholder', data.other_data.placeholder);
                        $(".filteredInput").hide();
                        $(".filteredSelect").show();
                        $(".filteredMultiSelect").hide();
                        $(".divDateRange").hide();
                        $(".filteredNumber").hide();
                        choiceOPtions = data.other_data.options;

                    }
                    else if (data.other_data.input_type == 'date') {
                        $(data.element).attr('data-inputtype', data.other_data.input_type);
                        $(data.element).attr('data-fieldname', data.id);
                        $(data.element).attr('data-displayname', data.other_data.display_name);
                        $(data.element).attr('data-placeholder', data.other_data.placeholder);
                        $(data.element).attr('data-parse', data.other_data.data_parse);
                        $(data.element).attr('data-url', data.other_data.url);
                        $(".filteredInput").hide();
                        $(".filteredSelect").hide();
                        $(".filteredMultiSelect").hide();
                        $(".divDateRange").show();
                        $(".filteredNumber").hide();
                        selectDaterange()

                    }
                }
                //  $(data.element).attr('data-custom-attribute', data.type);
                return data.text;
            }
        }).change(function (e) {
            $("#inputType").val('');
            $("#inputType").attr('placeholder', 'Enter value...');
            $("#filteredSelect").text('');
            $("#customMultiSelect").text('');

            $('#minNumber').val('');
            $('#maxNumber').val('');
            var inputType = $("#customFilterSelect option:selected").attr('data-inputtype');
            if (inputType == 'select') {
                var url = $("#customFilterSelect option:selected").attr('data-url');
                var placeholder = $("#customFilterSelect option:selected").attr('data-placeholder');
                var data_parse = $("#customFilterSelect option:selected").attr('data-parse');
                var fieldname = $("#customFilterSelect option:selected").attr('data-fieldname');
                filteredSelect(url, placeholder, data_parse, fieldname);
            }
            else if (inputType == 'multiselect') {
                var url = $("#customFilterSelect option:selected").attr('data-url');
                var placeholder = $("#customFilterSelect option:selected").attr('data-placeholder');
                var data_parse = $("#customFilterSelect option:selected").attr('data-parse');
                var fieldname = $("#customFilterSelect option:selected").attr('data-fieldname');
                let obj = filterSearchArr && filterSearchArr.find(x => x.name === fieldname);
                if (obj) {
                    var valArr = filterSearchArr[0].value.split(',');
                    var txtArr = filterSearchArr[0].selectDisplayName.split(',');
                    for (var i = 0; i < valArr.length; ++i) {
                        multiChkBoxArr.push({ text: txtArr[i], value: valArr[i] })
                    }
                }
                filteredMultiSelect(url, placeholder, data_parse, fieldname);
            }
            else if (inputType == 'choices') {
                var placeholder = $("#customFilterSelect option:selected").attr('data-placeholder');
                filteredSelectChoices(placeholder, choiceOPtions);
            }

        });
    });


}

function filteredSelect(url, placeholder, data_parse, fieldname) {
    $("#filteredSelect").select2({
        placeholder: placeholder,
        ajax: {
            url: url,
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                $("#filteredSelect").text('')
                var custArray = [];
                var id = data_parse.split('?')[0].split(':')[1];
                var text = data_parse.split('?')[1].split(':')[1];

                $.each(data.data, function (key, value) {
                    custArray.push({ id: eval(id), text: eval(text) })
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
    }).change(function (e) {
    });

}

function filteredMultiSelect(url, placeholder, data_parse, fieldname) {
    $("#customMultiSelect").select2({
        placeholder: placeholder,
        closeOnSelect: false,
        multiple: true,
        ajax: {
            url: url,
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                $("#customMultiSelect").text('')
                var custArray = [];
                var id = data_parse.split('?')[0].split(':')[1];
                var text = data_parse.split('?')[1].split(':')[1];

                $.each(data.data, function (key, value) {
                    custArray.push({ id: eval(id), text: eval(text) })
                });
                return { results: custArray };
            },
            error: function (jqXHR, status, error) {
                if (jqXHR.status === "401") {
                    redirectToLogin(error);
                }
            }
        },
        templateResult: formatOption,
        allowClear: true
    }).change(function (e) {
    });
}


function formatOption(data, element) {
    $("#select2-customMultiSelect-results li").attr('disabled', true)
    var fieldName = $("#customFilterSelect option:selected").attr('data-fieldname');
    let objIndex = filterSearchArr.findIndex((obj => obj.name == fieldName));
    let obj = filterSearchArr && filterSearchArr.find(x => x.name === fieldName);
    if (objIndex >= 0) {
        if (obj.value.indexOf(data.id) >= 0) {
            $data = $(
                '<span><input type="checkbox" class="multiSelectChkBox" checked name="multiOption" value="' + data.id + '" data-text="' + data.text + '"> ' + data.text + '</span>'
            );
        }
        else {
            $data = $(
                '<span><input type="checkbox" class="multiSelectChkBox" name="multiOption" value="' + data.id + '" data-text="' + data.text + '"> ' + data.text + '</span>'
            );
        }
    }
    else {
        $data = $(
            '<span><input type="checkbox" class="multiSelectChkBox" name="multiOption" value="' + data.id + '" data-text="' + data.text + '"> ' + data.text + '</span>'
        );
    }
    return $data;
};

$(document).off('change', '#customMultiSelect').on('change', '#customMultiSelect', function (e) {
    e.preventDefault()
    $("#customMultiSelect").text(''); //to clear selected options
 //added to scroll up an down so that multiselect dropdown not overlap the selectbox
    if ($(window).scrollTop() == 0) {
        $('html, body').animate({ scrollTop: 1 }, 700);
    }
    else {
        $('html, body').animate({ scrollTop: 0 }, 700);
    }
});

$(document).off('change', '.multiSelectChkBox').on('change', '.multiSelectChkBox', function (e) {
    var fieldName = $("#customFilterSelect option:selected").attr('data-fieldname');
    if (fieldName) {
        var inputType = $("#customFilterSelect option:selected").attr('data-inputtype');
        var display_name = $("#customFilterSelect option:selected").attr('data-displayname');
        let objIndex = filterSearchArr.findIndex((obj => obj.name == fieldName));
        var displaySelectedVal = [];
        var displaySelectedText = [];
        if (this.checked) {
            multiChkBoxArr.push({ text: $(this).attr('data-text'), value: $(this).val() })
        }
        else {
            let objIndex = multiChkBoxArr.findIndex((obj => obj.value == $(this).val()));
            multiChkBoxArr.splice(objIndex, 1);
        }

        multiChkBoxArr.filter(function (obj) {
            displaySelectedVal.push(obj.value)
            displaySelectedText.push(obj.text)
            return obj;
        });

        if (multiChkBoxArr.length <= 0) {
            filterSearchArr.splice(objIndex, 1);
            filteredDataHtml();
            return;
        }
        if (objIndex < 0) {
            filterSearchArr.push({
                name: fieldName,
                value: displaySelectedVal.toString(),
                displayName: display_name,
                inputType: inputType,
                selectDisplayName: displaySelectedText.toString()
            });
        }
        else {
            filterSearchArr[objIndex].value = displaySelectedVal.toString(),
                filterSearchArr[objIndex].selectDisplayName = displaySelectedText.toString()
        }
        filteredDataHtml();
    }

});

function filteredSelectChoices(placeholder, options) {
    $("#filteredSelect").text('')
    var optionHtml = '<option value=""></option>';
    $.each(options, function (i, item) {
        optionHtml += '<option value="' + item.value + '">' + item.text + '</option>'
    });
    $('#filteredSelect').append(optionHtml);
    $("#filteredSelect").select2({

        placeholder: placeholder,
        allowClear: true
    }).change(function () {
    });
}

$(document).off('change', '#filteredSelect').on('change', '#filteredSelect', function (e) {
    var customSelectVal = $("#filteredSelect option:selected").val();
    onchangeSelect(customSelectVal)
});

$(document).off('blur', '#inputType').on('blur', '#inputType', function (e) {
    var val = $(this).val();
    var fieldName = $("#customFilterSelect option:selected").attr('data-fieldname');
    //add/replace values to array for input text
    if (val && fieldName) {
        var inputType = $("#customFilterSelect option:selected").attr('data-inputtype');
        var display_name = $("#customFilterSelect option:selected").attr('data-displayname');
        let objIndex = filterSearchArr.findIndex((obj => obj.name == fieldName));
        if (objIndex < 0) {
            filterSearchArr.push({
                name: fieldName,
                value: val,
                displayName: display_name
            });
        }
        else {
            filterSearchArr[objIndex].value = val
        }
        //call function to display selected filters
        filteredDataHtml();
    }
});

$(document).off('change', '#minNumber').on('change', '#minNumber', function (e) {
    e.preventDefault()
    var minVal = parseInt($('#minNumber').val());
    var maxVal = parseInt($('#maxNumber').val());
    var dataMinVal = parseInt($('#minNumber').attr('data-min'));
    var dataMaxVal = parseInt($('#maxNumber').attr('data-max'));

    var fieldName = $("#customFilterSelect option:selected").attr('data-fieldname');
    if (isNaN(maxVal)) {
        maxVal = 0;
    }
    if (isNaN(minVal)) {
        minVal = 0;
    }
    if (minVal < dataMinVal || minVal < 0 || maxVal < 0) {
        alert("Value should be greater than equal to " + dataMinVal);
        return true;
    }
    else if (minVal > dataMaxVal) {
        if (minVal > maxVal) {
            alert("Value should be less than equal to " + maxVal);
            return true;
        }
        else {
            alert("Value should be less than equal to " + dataMaxVal);
            return true;
        }
    }
    else {
        if ($('#maxNumber').val() == '' || $('#minNumber').val() == '') {
            return true;
        }
        if (!isNaN(minVal) && !isNaN(maxVal) && fieldName) {
            var inputType = $("#customFilterSelect option:selected").attr('data-inputtype');
            var display_name = $("#customFilterSelect option:selected").attr('data-displayname');
            let objIndex = filterSearchArr.findIndex((obj => obj.name == fieldName));
            if (objIndex < 0) {
                filterSearchArr.push({
                    name: fieldName,
                    value: minVal + '-' + maxVal,
                    inputType: inputType,
                    displayName: display_name
                });
            }
            else {
                filterSearchArr[objIndex].value = minVal + '-' + maxVal
            }
            filteredDataHtml();
        }
    }
});

$(document).off('change', '#maxNumber').on('change', '#maxNumber', function (e) {
    e.preventDefault()
    var minVal = parseInt($('#minNumber').val());
    var maxVal = parseInt($('#maxNumber').val());
    var dataMinVal = parseInt($('#minNumber').attr('data-min'));
    var dataMaxVal = parseInt($('#maxNumber').attr('data-max'));

    if (isNaN(maxVal)) {
        maxVal = 0;
    }
    if (isNaN(minVal)) {
        minVal = 0;
    }

    var fieldName = $("#customFilterSelect option:selected").attr('data-fieldname');
    if (minVal < 0 || maxVal < 0) {
        alert("Value should be greater than equal to 0 ");
        return true;
    }
    else if (maxVal > dataMaxVal) {
        alert("Value should be less than equal to " + dataMaxVal);
        return true;
    }
    else if (maxVal < dataMinVal || maxVal < minVal) {
        if (maxVal < minVal) {
            alert("Value should be greater than equal to " + minVal);
            return true;
        }
        else {
            alert("Value should be greater than equal to " + dataMinVal);
            return true;
        }
    }
    else {
        if ($('#maxNumber').val() == '' || $('#minNumber').val() == '') {
            return true;
        }
        if (!isNaN(minVal) && !isNaN(maxVal) && fieldName) {

            var inputType = $("#customFilterSelect option:selected").attr('data-inputtype');
            var display_name = $("#customFilterSelect option:selected").attr('data-displayname');
            let objIndex = filterSearchArr.findIndex((obj => obj.name == fieldName));
            if (objIndex < 0) {
                filterSearchArr.push({
                    name: fieldName,
                    value: minVal + '-' + maxVal,
                    inputType: inputType,
                    displayName: display_name
                });
            }
            else {
                filterSearchArr[objIndex].value = minVal + '-' + maxVal
            }
            filteredDataHtml();
        }
    }
});


$(document).off('click', '.removeFilteredData').on('click', '.removeFilteredData', function (e) {
    $("#customFilterSelect").val('').trigger('change')
    $("#inputType").val('');
    $("#inputType").attr('placeholder', 'Enter value...');
    $("#filteredSelect").val('').trigger('change');
    $("#customMultiSelect").val('').trigger('change');
    $('.dataRangeVal').text('');
    $('#minNumber').val('');
    $('#maxNumber').val('');
    multiChkBoxArr = [];
    var dataName = $(this).attr('data-name');
    let objIndex = filterSearchArr.findIndex((obj => obj.name == dataName));
    filterSearchArr.splice(objIndex, 1);
    filteredDataHtml();
    $("#tblSearch").trigger('click');
});

//to display selected filters 
function filteredDataHtml() {
    var filteredDataHtml = "";
    $.each(filterSearchArr, function (index, value) {
        filteredDataHtml += '<div class="col-md-12 col-lg-12 col-sm-12 col-xs-12 filterDiv">';
        filteredDataHtml += '<a href="javascript:;" class="close removeFilteredData" data-name="' + value.name + '"  aria-label="close">&times;</a>';
        if (value.inputType == 'select' || value.inputType == 'choices' || value.inputType == 'multiselect') {
            filteredDataHtml += '<strong>' + value.displayName + ': </strong> ' + value.selectDisplayName + ' ';
        }
        else {
            filteredDataHtml += '<strong>' + value.displayName + ': </strong> ' + value.value + ' ';
        }
        filteredDataHtml += '</div>';
    });
    $('.filterdData').html(' ');
    $('.filterdData').html(filteredDataHtml);
    if (filterSearchArr.length > 0) {
        $('.clearAll').show();
    }
    else {
        $('.clearAll').hide();
    }
}

//to add filters after change of dropdown
function onchangeSelect(selectedVal) {
    var val = selectedVal;
    var fieldName = $("#customFilterSelect option:selected").attr('data-fieldname');
    if (val && fieldName) {
        var inputType = $("#customFilterSelect option:selected").attr('data-inputtype');
        var display_name = $("#customFilterSelect option:selected").attr('data-displayname');
        var selectedText = $("#filteredSelect option:selected").text();
        let objIndex = filterSearchArr.findIndex((obj => obj.name == fieldName));
        if (objIndex < 0) {
            filterSearchArr.push({
                name: fieldName,
                value: val,
                displayName: display_name,
                inputType: inputType,
                selectDisplayName: selectedText
            });
        }
        else {
            if (filterSearchArr[objIndex].inputType == 'select' || filterSearchArr[objIndex].inputType == 'choices') {
                filterSearchArr[objIndex].value = val
                filterSearchArr[objIndex].selectDisplayName = selectedText
            }
            else {
                filterSearchArr[objIndex].value = val
            }
        }
        filteredDataHtml();
    }
}

function selectDaterange() {
    $('#dateRange span').html('');
    var start = moment().subtract(29, 'days');
    var end = moment();
    function cb(start, end) {
        var fieldName = $("#customFilterSelect option:selected").attr('data-fieldname');
        if (fieldName) {
            var display_name = $("#customFilterSelect option:selected").attr('data-displayname');

            let objIndex = filterSearchArr.findIndex((obj => obj.name == fieldName));
            var val = start.format('YYYY-MM-DD') + ' To ' + end.format('YYYY-MM-DD');
            if (objIndex < 0) {
                filterSearchArr.push({
                    name: fieldName,
                    value: val,
                    displayName: display_name,
                    date: true
                });
            }
            else {
                filterSearchArr[objIndex].value = val
            }
            filteredDataHtml();
            $('#dateRange span').html(start.format('YYYY-MM-DD') + ' To ' + end.format('YYYY-MM-DD'));
        }
    }

    $('#dateRange').daterangepicker({
        startDate: moment().startOf('hour'),
        endDate: moment().startOf('hour').add(1, 'days'),
        ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Current Financial Year': [moment().month(3).startOf('month'), moment()],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        "showDropdowns": true,
        "minDate": "01/01/2010",
        "maxDate": moment()
    }, cb);
}

$(document).off("click", ".clearAll").on("click", ".clearAll", function (e) {
    filterSearchArr = [];
    multiChkBoxArr = [];
    $("#inputType").val('');
    $("#inputType").attr('placeholder', 'Enter value...');
    $("#filteredSelect").val('').trigger('change');
    $('.dataRangeVal').text('');
    $('#minNumber').val('');
    $('#maxNumber').val('');
    $("#customFilterSelect").val('').trigger('change');
    $("#customMultiFilterSelect").val('').trigger('change');
    filteredDataHtml();
    $("#tblSearch").trigger('click');
});