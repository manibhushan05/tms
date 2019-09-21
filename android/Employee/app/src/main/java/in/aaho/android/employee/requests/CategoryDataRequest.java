package in.aaho.android.employee.requests;

import java.util.Map;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

public class CategoryDataRequest extends ApiGetRequest {
    public CategoryDataRequest(Map<String, String> params, ApiResponseListener listener) {
        super(Api.CATEGORY_DATA_URL, params, listener);
    }
}
