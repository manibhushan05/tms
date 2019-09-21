package in.aaho.android.ownr.requests;
import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

/**
 * Created by aaho on 03/12/18.
 */

public class AWSCredentialsRequest extends ApiGetRequest{
    public AWSCredentialsRequest(ApiResponseListener listener) {
        super(Api.AWS_CRED_URL, ApiGetRequest.NO_HEADER, listener);
    }
}

