package in.aaho.android.ownr.transaction;

import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;

import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.R;
import in.aaho.android.ownr.adapter.QuotationResponseAdapter;
import in.aaho.android.ownr.data.QuotationResponseData;
import in.aaho.android.ownr.parser.QuotationResponseParser;
import in.aaho.android.ownr.requests.CancelTransactionRequest;

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
        recyclerViewQuotaionResponse = findViewById(R.id.recycler_view_quotation_responses);
        tvTransactionId = findViewById(R.id.tvQRTransactionID);
        tvPickupFrom = findViewById(R.id.tvNumberOfBookingsValue);
        tvDropAt = findViewById(R.id.tvTotalAmountValue);
        tvNumberOfTrucks = findViewById(R.id.tvQRNumberOfTruck);
        tvShipmentDate = findViewById(R.id.tvQRShipmentDate);
        tvNumberOfQuotes = findViewById(R.id.tvQRNumberOfQuotes);
        btnCancel = findViewById(R.id.btQRCancel);

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
