package in.aaho.android.employee.requests;

import android.text.TextUtils;

import java.util.Map;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by aaho on 28/02/19.
 */

public class PendingPaymentCommentsRequest extends ApiGetRequest {

    public PendingPaymentCommentsRequest(Integer id, ApiResponseListener listener) {
        super(Api.GET_PENDING_PAYMENT_COMMENTS_URL+id+"/", ApiGetRequest.NO_HEADER, listener);
    }



}