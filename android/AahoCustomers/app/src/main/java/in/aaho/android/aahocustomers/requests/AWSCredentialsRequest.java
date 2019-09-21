package in.aaho.android.aahocustomers.requests;
import in.aaho.android.aahocustomers.common.ApiGetRequest;
import in.aaho.android.aahocustomers.common.ApiResponseListener;

/**
 * Created by aaho on 03/12/18.
 */

public class AWSCredentialsRequest extends ApiGetRequest{
    public AWSCredentialsRequest(ApiResponseListener listener) {
        super(Api.AWS_CRED_URL, ApiGetRequest.NO_HEADER, listener);
    }
}