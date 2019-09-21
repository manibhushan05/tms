
class PayBalanceComponent extends React.Component {
  constructor(props) {
    super(props);
    this.payBalanceElement = null;
    this.state = {
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
    const scriptSrcArr = ["/static/vendor/datatable/Bootstrap3/DataTables/DataTables-1.10.16/js/jquery.dataTables.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/DataTables-1.10.16/js/dataTables.bootstrap.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Buttons-1.5.1/js/dataTables.buttons.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Buttons-1.5.1/js/buttons.bootstrap.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Buttons-1.5.1/js/buttons.flash.min.js",
      "/static/vendor/datepicker/js/bootstrap-datetimepicker.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Buttons-1.5.1/js/buttons.html5.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Buttons-1.5.1/js/buttons.print.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/FixedHeader-3.1.3/js/dataTables.fixedHeader.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/KeyTable-2.3.2/js/dataTables.keyTable.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Responsive-2.2.1/js/dataTables.responsive.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Responsive-2.2.1/js/responsive.bootstrap.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/Scroller-1.4.4/js/dataTables.scroller.min.js",
      "/static/vendor/datatable/Bootstrap3/DataTables/JSZip-2.5.0/jszip.min.js",
      "/static/vendor/moment/js/moment.min.js",
      "/static/vendor/icheck-1/icheck.min.js",
      "/static/aaho/jquery.serializejson.js",
      "/static/vendor/datepicker/js/bootstrap-datetimepicker.min.js",
      "/static/vendor/select2/js/select2.min.js",
      "/static/vendor/parsley/js/parsley.min.js",
      "/static/aaho/js/team/pay_balance.js",
    ];
    var that = this;
    scriptSrcArr.forEach(function (src) {
      that.loadScripts(src);
    });

    setTimeout(function () {
      const script = document.getElementById('myScript').innerHTML;
      window.eval(script);
    }, 1000);
  }
  render() {
    return (
      <div className='Container'
        ref={payBalanceElement => (this.payBalanceElement = payBalanceElement)}
        dangerouslySetInnerHTML={{ __html: this.state.html_string }}
      />
    );
  }
}