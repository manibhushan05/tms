
class VerifyPodComponent extends React.Component {
  constructor(props) {
    super(props);
    this.verifyPodElement = null;
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
      "/static/vendor/parsley/js/parsley.min.js",
      "/static/vendor/notify/notify.min.js",
      "/static/vendor/datepicker/js/bootstrap-datepicker.min.js",
      "/static/vendor/image-viewer/js/viewer.min.js",
      "/static/vendor/moment/js/moment.min.js",
      "/static/aaho/jquery.serializejson.js",
      // "/static/aaho/js/team/verify-docs/verify-pod.js",

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
        ref={verifyPodElement => (this.verifyPodElement = verifyPodElement)}
        dangerouslySetInnerHTML={{ __html: this.state.html_string }}
      />
    );
  }
}