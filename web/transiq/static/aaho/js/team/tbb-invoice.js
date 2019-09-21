function Invoice(data) {
    data = data || {};
    var self = this;
    self.invoice_number = ko.observable(data.invoice_number);
    self.date = ko.observable(new Date(data.date || null));
    self.company = ko.observable(data.company);
    self.address = ko.observable(data.address || '');
    self.city = ko.observable(data.city);
    self.display_address = ko.computed(function() {
        return self.address().split('\n').join('<br>');
    });

    self.service_tax_paid_by = ko.observable(data.service_tax_paid_by);
    self.service_tax_aaho = ko.observable(data.service_tax_aaho);
    self.remarks = ko.observable(data.remarks);

    self.sum_of_amounts = ko.computed(function() {
        var sum = 0;
        ko.utils.arrayForEach(bookings(), function(item) {
            if($.isNumeric(item.total_amount_to_company()) && $.isNumeric(sum))
                sum += parseFloat(item.total_amount_to_company());
            else
                sum = '';
        });
        if($.isNumeric(sum) && self.service_tax_paid_by() == 'aaho') {
            sum *= (1 + parseFloat(self.service_tax_aaho()) / 100.0);
            if(!$.isNumeric(sum))
                sum = '';
        }
        return sum.toFixed ? sum.toFixed(0) : sum;
    });
    self.total_amount = ko.observable();
    var total_automatically_updated = true;
    var updating_total_amount = false;
    var sum_subscription = self.sum_of_amounts.subscribe(function(val) {
        updating_total_amount = true;
        self.total_amount(val);
        updating_total_amount = false;
    });
    var total_amount_subscription = self.total_amount.subscribe(function(val) {
        if(!updating_total_amount) {     // total_amount was manually updated, stop automatic updating now
            sum_subscription.dispose();
            total_amount_subscription.dispose();
            total_automatically_updated = false;
        }
    });
    if(data.total_amount) {     // total_amount was manually updated, stop automatic updating now
        sum_subscription.dispose();
        total_amount_subscription.dispose();
        total_automatically_updated = false;
        self.total_amount(data.total_amount);
    }
    self.total_amount_error = ko.computed(function() {
        if(self.sum_of_amounts() != self.total_amount() && !total_automatically_updated) {
            return 'Total amount should be ' + self.sum_of_amounts();
        }
        return '';
    });

    self.address_editable = ko.observable(false);
    self.company_cache = ko.observable();
    self.address_cache = ko.observable();
    self.city_cache = ko.observable();
    self.edit_address = function() {
        self.company_cache(self.company());
        self.address_cache(self.address());
        self.city_cache(self.city());
        self.address_editable(true);
    };
    self.save_address = function() {
        self.company(self.company_cache());
        self.address(self.address_cache());
        self.city(self.city_cache());
        self.address_editable(false);
    };
}

function Search() {
    var self = this;
    self.lr_number = ko.observable();
    self.lr_error = ko.observable();
    self.mode = MODE;
    self.search_lr = function() {
        var success = function(data) {
            if(data.error) {
                self.lr_error(data.error);
            }
            else {
                self.lr_error('');
                var booking = new Booking(data);
                if(bookings().length === 0 && !invoice.company() && !invoice.address() && !invoice.city()) {
                    booking.choose_for_invoice();
                }
                bookings.push(booking);
            }
        };
        var post_data = {
            lr_number: self.lr_number(),
            csrfmiddlewaretoken: csrf_token
        };
        $.post(LR_DETAILS_URL, post_data, success, 'json');
    };
}

function Booking(data) {
    var self = this;
    self.id = data.id;
    self.lr_number = data.lr_number;
    self.from_city = data.from_city;
    self.to_city = data.to_city;

    self.company = data.company;
    self.address = data.address || '';
    self.display_address = self.address.split('\n').join('<br>');
    self.city = data.city;

    self.rate = ko.observable(data.rate);
    self.charged_weight = ko.observable(data.charged_weight);
    self.loaded_weight = ko.observable(data.loaded_weight);
    self.amount_charged = ko.computed(function() {
        if(self.rate() && self.charged_weight()) {
            var amount = self.rate() * self.charged_weight();
            if(typeof amount === "number" && !isNaN(amount)) {
                return amount;
            }
        }
        return '';
    });

    self.total_amount_to_company = ko.observable(data.total_amount_to_company);
    self.additional_charges_for_company = ko.observable(data.additional_charges_for_company || 0);
    self.note_for_additional_company_charges = ko.observable(data.note_for_additional_company_charges);
    self.total_amount_error = ko.computed(function() {
        if(!$.isNumeric(self.total_amount_to_company())) {
            if(self.total_amount_to_company() == "") return "";
            else return "Value should be a number"
        }
        if($.isNumeric(self.amount_charged()) && $.isNumeric(self.additional_charges_for_company())) {
            if(self.total_amount_to_company() == parseFloat(self.amount_charged()) + parseFloat(self.additional_charges_for_company()))
                return '';
            else return "Total amount does not equal the sums";
        }
    });

    self.invoice_comment = ko.observable(data.invoice_comment);

    self.details_visible = ko.observable(false);
    self.toggle_details = function() {
        self.details_visible(!self.details_visible());
    };
    self.remove = function() {
        bookings.remove(self);
    };
    self.choose_for_invoice = function() {
        invoice.company(self.company);
        invoice.address(self.address);
        invoice.city(self.city);
    };
}

function format_date(date) {
    return date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
}

function send_data() {
    data = {};
    data.invoice_number = ko.unwrap(invoice.invoice_number);
    data.company = ko.unwrap(invoice.company);
    data.address = ko.unwrap(invoice.address);
    data.city = ko.unwrap(invoice.city);
    data.date = format_date(ko.unwrap(invoice.date));
    data.service_tax_paid_by = ko.unwrap(invoice.service_tax_paid_by);
    data.service_tax_aaho = ko.unwrap(invoice.service_tax_aaho);
    data.total_amount = ko.unwrap(invoice.total_amount);
    data.remarks = ko.unwrap(invoice.remarks);
    data.bookings = [];
    for(var i = 0; i < bookings().length; i++) {
        var booking = bookings()[i];
        data.bookings.push({
            'lr_number': ko.unwrap(booking.lr_number),
            'id': ko.unwrap(booking.id),
            'lorry_number': ko.unwrap(booking.lorry_number),
            'from_city': ko.unwrap(booking.from_city),
            'to_city': ko.unwrap(booking.to_city),
            'company': ko.unwrap(booking.company),
            'address': ko.unwrap(booking.address),
            'city': ko.unwrap(booking.city),
            'loaded_weight': ko.unwrap(booking.loaded_weight),
            'charged_weight': ko.unwrap(booking.charged_weight),
            'rate': ko.unwrap(booking.rate),
            'total_amount_to_company': ko.unwrap(booking.total_amount_to_company),
            'additional_charges_for_company': ko.unwrap(booking.additional_charges_for_company),
            'note_for_additional_company_charges': ko.unwrap(booking.note_for_additional_company_charges),
            'invoice_comment': ko.unwrap(booking.invoice_comment),
        })
    }
    var post_data = {
        data: ko.toJSON(data),
        csrfmiddlewaretoken: csrf_token
    };
    var success = function(res) {
        if(res.redirect_url)
            window.location = res.redirect_url;
    };
    $.post(TBB_INVOICE_URL, post_data, success, 'json');
}

var bookings = ko.observableArray();
if(DATA.bookings) {
    for(var i = 0; i < DATA.bookings.length; i++) {
        var booking = new Booking(DATA.bookings[i]);
        bookings.push(booking);
    }
}
var invoice = new Invoice(DATA);
var search = new Search();

ko.applyBindings({
    invoice: invoice,
    search: search,
    bookings: bookings,
});
