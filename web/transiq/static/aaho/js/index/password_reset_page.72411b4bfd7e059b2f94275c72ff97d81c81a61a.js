// options:
//   minLength
//   requireStrong
function PasswordStrength(e, t) {
    this.user = e, this.rocCache = {}, this.options = t || {}, this.options.minLength = this.options.minLength || 6
}
PasswordStrength.prototype = {
    queryRoc: function (e, t) {
        var n;
        if (n = this.rocCache[e])return $.Deferred().resolve(n);

    }, addRocResponse: function (e, t) {
        this.rocCache[e] = t
    }, sameAs: function (e, t) {
        return t && e.toLowerCase() === ("" + t).toLowerCase()
    }, strength: function (e) {
        var t = this.rocCache[e];
        if (t && !t.pass)return {score: 0, reason: "roc", rocStatus: t};
        if (e.length < this.options.minLength)return {score: e.length, reason: "tooshort"};
        if (this.sameAs(e, this.user.username) || this.sameAs(e, this.user.fullname))return {
            score: 0,
            reason: "obvious"
        };
        var n, r;
        n = 0, n += e.length * 4, n += (this.repeats(1, e).length - e.length) * 1, n += (this.repeats(2, e).length - e.length) * 1, n += (this.repeats(3, e).length - e.length) * 1, n += (this.repeats(4, e).length - e.length) * 1, e.match(/(.*[0-9].*[0-9].*[0-9])/) && (n += 5), e.match(/(.*[!@#$%^&*?_~].*[!@#$%^&*?_~])/) && (n += 5), e.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/) && (n += 10), e.match(/([a-zA-Z])/) && e.match(/([0-9])/) && (n += 15), e.match(/([!@#$%^&*?_~])/) && e.match(/([0-9])/) && (n += 15), e.match(/([!@#$%^&*?_~])/) && e.match(/([a-zA-Z])/) && (n += 15);
        if (e.match(/^\w+$/) || e.match(/^\d+$/)) n -= 10;
        return n < 0 && (n = 0), n > 100 && (n = 100), n < 34 ? r = "weak" : n < 50 ? r = "good" : n < 75 ? r = "strong" : r = "verystrong", {
            score: n,
            reason: r
        }
    }, repeats: function (e, t) {
        var n = "", r = t.length;
        for (var i = 0; i < r; i++) {
            var s = !0;
            for (var o = 0; o < e && o + i + e < t.length; o++)s = s && t.charAt(o + i) == t.charAt(o + i + e);
            o < e && (s = !1), s ? (i += e - 1, s = !1) : n += t.charAt(i)
        }
        return n
    }
};
function PasswordStrengthWidget(e) {
    this.$el = e, this.$input = e.find("input"), this.checker = new PasswordStrength({
        username: this.$input.data("username"),
        fullname: this.$input.data("fullname")
    }), this.status = {score: 0}, this.updateStrengthFeedback(this.$el.find("input").val()), this.authenticity_token = $("input[name=authenticity_token]").val()
}
PasswordStrengthWidget.prototype = {
    onChange: function (e) {
        var t = $(e.target).val();
        this.updateStrengthFeedback(t);
        var n = e.type == "change" && this.strengthValidation().success;
        n && this.checker.queryRoc(t, this.authenticity_token).done(this.handleRocResponse.bind(this, t))
    }, handleRocResponse: function (e, t) {
        this.$input.val() == e && this.strengthValidation().success && !t.pass && this.updateStrengthFeedback(e)
    }, clearStatusClass: function () {
        this.status && this.status.reason && this.$el.removeClass("PasswordStrength--" + this.status.reason)
    }, updateStrengthFeedback: function (e) {
        var t;
        this.clearStatusClass(), this.status = this.checker.strength(e), (t = this.status.rocStatus) && this.$input.siblings(".Form-message").find('span[data-key="roc"]').text(t.message), e.length == 0 ? this.$input.trigger("updateFeedback", {key: "default"}) : (this.$el.addClass("PasswordStrength--" + this.status.reason), this.$input.trigger("updateFeedback", {
            key: this.status.reason,
            isErrored: !this.strengthValidation().success
        }))
    }, strengthValidation: function () {
        var e = this.status.score > this.checker.options.minLength;
        return {message: this.status.reason, success: e}
    }
};
function PasswordFormWidget(e) {
    this.$el = e, this.strengthWidget = new PasswordStrengthWidget(e.find(".PasswordStrength")), this.$confirmationField = this.$el.find('input[name="password_confirmation"]'), this.$confirmationField.trigger("addValidation", $.proxy(this.validPasswordConfirmation, this)), this.$passwordField = this.$el.find('input[name="password"]'), this.$passwordField.trigger("addValidation", $.proxy(this.strengthWidget.strengthValidation, this.strengthWidget)), this.$passwordField.on("keyup focus change", this.strengthWidget.onChange.bind(this.strengthWidget)), this.$passwordField.on("change keyup", function () {
        this.$confirmationField.trigger("clearFeedback")
    }.bind(this)), this.$confirmationField.on("change keyup", function () {
        $(this).trigger("runValidation")
    })
}
PasswordFormWidget.prototype = {
    validPasswordConfirmation: function () {
        var e = this.$el.find('input[name="password"]'), t = e.val(),
            n = this.$el.find('input[name="password_confirmation"]').val(), r = t && t == n;
        return r ? e.hasClass("is-errored") ? {message: "default", success: !1} : {
            message: "default",
            success: !0
        } : {message: "mismatch", success: !1}
    }
};
new PasswordFormWidget($(".Form"));