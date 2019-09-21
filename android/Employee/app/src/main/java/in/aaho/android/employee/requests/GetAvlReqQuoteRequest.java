package in.aaho.android.employee.requests;

import java.util.Map;

import in.aaho.android.employee.activity.RequirementQuoteActivity;
import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj.m
 */
public class GetAvlReqQuoteRequest extends ApiGetRequest {

    public GetAvlReqQuoteRequest(Map<String, String> params,
                                 ApiResponseListener listener) {
        super(Api.GET_AVL_REQ_QUOTE, params, listener);
    }

}
