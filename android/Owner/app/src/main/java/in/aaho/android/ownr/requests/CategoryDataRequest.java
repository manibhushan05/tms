package in.aaho.android.ownr.requests;

import java.util.Map;

import in.aaho.android.ownr.common.ApiGetRequest;
import in.aaho.android.ownr.common.ApiResponseListener;

public class CategoryDataRequest extends ApiGetRequest {
    public CategoryDataRequest(Map<String, String> params, ApiResponseListener listener) {
        super(Api.CATEGORY_DATA_URL, params, listener);
    }
}
