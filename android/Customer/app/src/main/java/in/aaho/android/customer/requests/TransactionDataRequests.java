package in.aaho.android.customer.requests;

import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;

/**
 * Created by mani on 28/7/16.
 */
public class TransactionDataRequests  {
//    public TransactionDataRequests(){};
    private void sendRequest(){

        StringRequest stringRequest = new StringRequest(Api.TRANSACTION_DATA_URL,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {

                        //Log.e("jsonResponse",response);
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
//                        Toast.makeText(MainActivity.this,error.getMessage(),Toast.LENGTH_LONG).show();
                    }
                });

//        RequestQueue requestQueue = Volley.newRequestQueue(TransactionDataRequests.this);
//        requestQueue.add(stringRequest);
    }
}
