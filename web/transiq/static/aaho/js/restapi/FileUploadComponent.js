
class FileUploadComponent extends React.Component {
    constructor(props) {
        super(props);
        this.fileUploadElement = null;
        this.state = {
            html_string: props.html_string,
            escalateHtml_string: props.escalateBtn_string,
        };
    }
    render() {
        return (
            <div>
                <div className="row fileupload-buttonbar ">
                    <div className="col-lg-3 col-md-3 col-sm-3 col-xs-12 fileuploadButtons">
                        <span className="btn btn-primary fileinput-button fileUpload" >
                            <i className="glyphicon glyphicon-plus"></i>
                            <span>Upload</span>
                            <input type="file" name="file" className="fileUpload" accept="image/jpg, image/jpeg, image/png"
                                multiple />
                        </span><br/>
                        <button type="submit" className="col-lg-5 col-md-5 col-sm-5 col-xs-12 btn btn-md btn-primary btnSubmit start">
                            Submit
                        </button>
                       
                        <div
                            ref={fileUploadElement => (this.fileUploadElement = fileUploadElement)}
                            dangerouslySetInnerHTML={{ __html: this.state.escalateHtml_string }}
                        />
                    </div>
                    {/* <div className="col-lg-3 col-md-3 col-sm-3 col-xs-12 fileupload-progress fade">
                        <div className="progress progress-striped active" role="progressbar"
                            aria-valuemin="0"
                            aria-valuemax="100">
                            <div className="progress-bar progress-bar-success" style={{ width: '0%' }}></div>
                        </div>
                        <div className="progress-extended">&nbsp;</div>
                    </div> */}
                </div>
                <table role="presentation" className="table table-striped">
                    <tbody className="files"></tbody>
                </table>
            </div>
        );
      }
}