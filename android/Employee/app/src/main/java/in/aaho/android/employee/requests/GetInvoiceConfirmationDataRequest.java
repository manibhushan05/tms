package in.aaho.android.employee.requests;

import android.text.TextUtils;

import in.aaho.android.employee.common.ApiGetRequest;
import in.aaho.android.employee.common.ApiResponseListener;

/**
 * Created by Suraj M
 */
public class GetInvoiceConfirmationDataRequest extends ApiGetRequest {

    public GetInvoiceConfirmationDataRequest(String url, ApiResponseListener listener) {
        super(generateUrl(url), ApiGetRequest.NO_HEADER, listener);
    }

    private static String generateUrl(String url) {
        String newUrl = "";
        if(TextUtils.isEmpty(url)) {
            newUrl = Api.GET_INVOICE_CONFIRMATION_URL;
        } else {
            newUrl = url;
        }

        return newUrl;
    }

}
