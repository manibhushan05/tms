class InwardEntryComponent extends React.Component {
  constructor(props) {
    super(props);
    this.inwardEntryElement = null;
    this.state = {
      context: props.context,
      html_string: props.html_string,
    };
  }
  loadScripts = (src) => {
    var jsfile = $("<script type='text/javascript' src='" + src + "'>");
    $('#dashboardPages').append(jsfile);
  }
  componentDidMount() {
    //scripts not load from html string need to do following
    const scriptSrcArr = [
      "/static/vendor/parsley/js/parsley.min.js",
      "/static/vendor/notify/notify.min.js",
      "/static/vendor/select2/js/select2.min.js",
      "/static/vendor/moment/js/moment.min.js",
      "/static/aaho/jquery.serializejson.js",
    ];
    var that = this;
    scriptSrcArr.forEach(function (src) {
      that.loadScripts(src);
    });
    //to work scripts inside page first find that script tag by id and then evaluate 
    setTimeout(function () {
      const script = document.getElementById('myScript').innerHTML;
      window.eval(script);
    }, 1000);
  }
  render() {
    return (
      <div className='Container'
        ref={inwardEntryElement => (this.inwardEntryElement = inwardEntryElement)}
        dangerouslySetInnerHTML={{ __html: this.state.html_string }}
      />
    );
  }
}