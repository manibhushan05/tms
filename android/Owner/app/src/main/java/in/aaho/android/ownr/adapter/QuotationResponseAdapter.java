package in.aaho.android.ownr.adapter;

import android.app.ProgressDialog;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.data.QuotationResponseData;
import in.aaho.android.ownr.requests.Api;

/**
 * Created by mani on 10/8/16.
 */
public class QuotationResponseAdapter extends RecyclerView.Adapter<QuotationResponseAdapter.MyViewHolder> {
    private List<QuotationResponseData> quotationResponseDataList;

    public QuotationResponseAdapter(List<QuotationResponseData> quotationResponseDataList) {
        this.quotationResponseDataList = quotationResponseDataList;
    }

    public class MyViewHolder extends RecyclerView.ViewHolder {
        private TextView tvResponseId;
        private TextView tvResponseDateTime;
        private TextView tvVendorName;
        private TextView tvMessage;
        private Button btnAccept;
        private Button btnDecline;
        public MyViewHolder(View view) {
            super(view);
            tvResponseId = view.findViewById(R.id.tvQuotationResponseNumber);
            tvResponseDateTime = view.findViewById(R.id.tvQuotationResponseDatetime);
            tvVendorName = view.findViewById(R.id.tvQuotationResponseVendorName);
            tvMessage = view.findViewById(R.id.tvQuotationResponseMessage);
            btnAccept = view.findViewById(R.id.btQuotationAccept);
            btnDecline = view.findViewById(R.id.btQuotationDecline);
            btnAccept.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    changeResponseStatus(v,tvResponseId.getText().toString(),"accepted");
                }
            });
            btnDecline.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    changeResponseStatus(v,tvResponseId.getText().toString(),"declined");
                }
            });
        }
    }
    public void changeResponseStatus(View v,String responseId, String status){
        final ProgressDialog pDialog = new ProgressDialog(v.getContext());
        pDialog.setMessage("Changing Status to... "+status);
        pDialog.show();
        JSONObject obj = new JSONObject();
        try {
            obj.put("responseId", responseId);
            obj.put("status",status);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, Api.CHANGE_VENDOR_RESPONSE_STATUS, obj,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {

                        pDialog.dismiss();
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e(Api.TAG, error.toString());
                        pDialog.dismiss();
                    }
                });
        RequestQueue requestQueue = Volley.newRequestQueue(v.getContext());
        requestQueue.add(jsonObjectRequest);
        jsonObjectRequest.setRetryPolicy(new DefaultRetryPolicy(10000,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.quotation_response_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        QuotationResponseData quotationResponseData = quotationResponseDataList.get(position);
        holder.tvResponseId.setText(quotationResponseData.getResponseId());
        holder.tvResponseDateTime.setText(quotationResponseData.getResponseDatetime());
        holder.tvVendorName.setText(quotationResponseData.getVendorName());
        holder.tvMessage.setText(quotationResponseData.getMessage());

    }

    @Override
    public int getItemCount() {
        return quotationResponseDataList.size();
    }
}
