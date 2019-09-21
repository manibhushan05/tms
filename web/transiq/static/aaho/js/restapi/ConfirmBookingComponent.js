class ConfirmBookingComponent extends React.Component {
  constructor(props) {
    super(props);
    this.bookingElement = null;
    this.state = {
      color: 'red',
      context: props.context,
      html_string: props.html_string,
    };
  }

  loadScripts = (src) => {
    var jsfile = $("<script type='text/javascript' src='" + src + "'>");
    $('#dashboardPages').append(jsfile);
  }
 //scripts not load from html string need to do following
  componentDidMount() {
    const scriptSrcArr = ["/static/vendor/moment/js/moment.min.js",
      "/static/vendor/icheck-1/icheck.min.js",
      "/static/aaho/jquery.serializejson.js",
      "/static/vendor/datepicker/js/bootstrap-datetimepicker.min.js",
      "/static/vendor/select2/js/select2.min.js",
      "/static/vendor/parsley/js/parsley.min.js",
      "/static/aaho/js/common-dashboard.js",
      "/static/aaho/js/team/create-booking-dashboard.js",
    ];
    var that = this;
    scriptSrcArr.forEach(function (src) {
      that.loadScripts(src);
    });
  }

  render() {
    return (
      <div className='Container'
        ref={bookingElement => (this.bookingElement = bookingElement)}
        dangerouslySetInnerHTML={{ __html: this.state.html_string }}
      />
    );
  }
}