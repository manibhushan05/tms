
class SendInvoiceComponent extends React.Component {
  constructor(props) {
    super(props);
    this.sendInvoiceElement = null;
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
    const scriptSrcArr = [
      "/static/vendor/notify/notify.min.js",
      "/static/vendor/fileupload/js/vendor/jquery.ui.widget.js",
      "/static/vendor/fileupload/js/tmpl.min.js",
      "/static/vendor/fileupload/js/load-image.min.js",
      "/static/vendor/fileupload/js/canvas-to-blob.min.js",
      "/static/vendor/fileupload/js/bootstrap.min.js",
      "/static/vendor/fileupload/js/jquery.blueimp-gallery.min.js",
      "/static/vendor/fileupload/js/jquery.iframe-transport.js",
      "/static/vendor/fileupload/js/jquery.fileupload.js",
      "/static/vendor/fileupload/js/jquery.fileupload-process.js",
      "/static/vendor/fileupload/js/jquery.fileupload-image.js",
      "/static/vendor/fileupload/js/jquery.fileupload-audio.js",
      "/static/vendor/fileupload/js/jquery.fileupload-video.js",
      "/static/vendor/fileupload/js/jquery.fileupload-validate.js",
      "/static/vendor/fileupload/js/jquery.fileupload-ui.js",
      // "/static/vendor/fileupload/js/main.js",
      "/static/vendor/fileupload/js/locale.js",
      "/static/vendor/fileupload/js/csrf.js",
      "/static/vendor/parsley/js/parsley.min.js",
      "/static/vendor/datepicker/js/bootstrap-datepicker.min.js",

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
        ref={sendInvoiceElement => (this.sendInvoiceElement = sendInvoiceElement)}
        dangerouslySetInnerHTML={{ __html: this.state.html_string }}
      />
    );
  }
}