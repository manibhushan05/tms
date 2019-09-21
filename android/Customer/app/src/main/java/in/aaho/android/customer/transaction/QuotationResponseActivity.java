package in.aaho.android.customer.transaction;

import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

import in.aaho.android.customer.common.BaseActivity;
import in.aaho.android.customer.R;
import in.aaho.android.customer.adapter.QuotationResponseAdapter;
import in.aaho.android.customer.data.QuotationResponseData;
import in.aaho.android.customer.parser.QuotationResponseParser;
import in.aaho.android.customer.requests.CancelTransactionRequest;

public class QuotationResponseActivity extends BaseActivity {
    private RecyclerView recyclerViewQuotaionResponse;
    private LinearLayoutManager layoutManagerQuotationResponse;
    private QuotationResponseAdapter mQuotationResponseAdapter;
    private List<QuotationResponseData> quotationResponseDataList;


    //Basic Transaction Data
    private TextView tvTransactionId;
    private TextView tvPickupFrom;
    private TextView tvDropAt;
    private TextView tvNumberOfTrucks;
    private TextView tvShipmentDate;
    private TextView tvNumberOfQuotes;
    private Button btnCancel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_quotation_response);
        setToolbarTitle("Responses");
        getId();
        try {
            JSONObject jsonObject = new JSONObject(getIntent().getStringExtra("value"));
            setBasicTransactionValue(jsonObject.getJSONObject("transaction_data"));
            QuotationResponseParser quotationResponseParser = new QuotationResponseParser(jsonObject.getJSONArray("responses"));
            SetupRecycleViewQuotationResponse(recyclerViewQuotaionResponse, quotationResponseParser.getQuotationResponseDataArrayList());
        } catch (JSONException e) {
            e.printStackTrace();
        }
        btnCancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                CancelTransactionRequest.cancelTransaction(v, tvTransactionId.getText().toString());
            }
        });
    }

    private void setBasicTransactionValue(JSONObject jsonObject) {
        try {
            tvTransactionId.setText(jsonObject.getString("transaction_id"));
            tvPickupFrom.setText(jsonObject.getString("pickup_city"));
            tvDropAt.setText(jsonObject.getString("drop_at"));
            tvNumberOfTrucks.setText(jsonObject.getString("total_vehicle"));
            tvShipmentDate.setText(jsonObject.getString("shipment_date"));
            tvNumberOfQuotes.setText(jsonObject.getString("no_of_quotes"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void getId() {
        recyclerViewQuotaionResponse = (RecyclerView) findViewById(R.id.recycler_view_quotation_responses);
        tvTransactionId = (TextView) findViewById(R.id.tvQRTransactionID);
        tvPickupFrom = (TextView) findViewById(R.id.tvQRPickupFrom);
        tvDropAt = (TextView) findViewById(R.id.tvQRDropAt);
        tvNumberOfTrucks = (TextView) findViewById(R.id.tvQRNumberOfTruck);
        tvShipmentDate = (TextView) findViewById(R.id.tvQRShipmentDate);
        tvNumberOfQuotes = (TextView) findViewById(R.id.tvQRNumberOfQuotes);
        btnCancel = (Button) findViewById(R.id.btQRCancel);

    }

    void SetupRecycleViewQuotationResponse(RecyclerView recyclerView, List<QuotationResponseData> quotationResponseDataList) {
        recyclerView.setHasFixedSize(true);
        layoutManagerQuotationResponse = new LinearLayoutManager(this);
        layoutManagerQuotationResponse.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(layoutManagerQuotationResponse);


        mQuotationResponseAdapter = new QuotationResponseAdapter(quotationResponseDataList);
        recyclerView.setAdapter(mQuotationResponseAdapter);
    }

}
