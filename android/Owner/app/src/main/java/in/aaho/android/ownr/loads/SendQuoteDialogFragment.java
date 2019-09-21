package in.aaho.android.ownr.loads;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import in.aaho.android.ownr.R;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.requests.SendQuoteRequest;

/**
 * Created by mani on 8/8/16.
 */

public class SendQuoteDialogFragment extends BaseDialogFragment {

    private EditText dialogQuoteAmountEdit, dialogQuoteVehicleCount, dialogQuoteCommentsEdit;
    private Button cancelBtn, dialogQuoteCountAddBtn, dialogQuoteCountSubBtn, doneBtn;

    private TextView fromCityTv, fromStateTv, shipmentDateTv, toCityTv, toStateTv, vehicleCountTv;
    private TextView vehicleTypeTv;

    private View dialogView;
    private VehicleRequest vehicleRequest;
    private VehicleRequestQuote vehicleRequestQuote;

    private QuoteSentListener listener;

    public void setVehicleRequest(VehicleRequest vehicleRequest) {
        this.vehicleRequest = vehicleRequest;
        if (vehicleRequest.quote != null) {
            vehicleRequestQuote = VehicleRequestQuote.copy(vehicleRequest.quote);
        } else {
            vehicleRequestQuote = VehicleRequestQuote.newQuote(vehicleRequest.id, 1, 0, null);
        }
    }

    public static void showNewDialog(BaseActivity activity, VehicleRequest vehicleRequest,
                                     QuoteSentListener listener) {
        SendQuoteDialogFragment dialog = new SendQuoteDialogFragment();
        dialog.setVehicleRequest(vehicleRequest);
        dialog.setActivity(activity);
        dialog.setListener(listener);
        dialog.show(activity.getSupportFragmentManager(), "send_quote_fragment");
    }

    public void setListener(QuoteSentListener listener) {
        this.listener = listener;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.send_quote_dialog, container, false);

        setViewVariables();
        setClickListeners();
        updateUI();

        return dialogView;
    }

    private void updateUI() {
        updateRequestUI();
        updateQuoteUI();
    }

    private void updateRequestUI() {
        fromCityTv.setText(Utils.def(vehicleRequest.fromCity, ""));
        fromStateTv.setText(Utils.def(vehicleRequest.fromState, ""));
        toCityTv.setText(Utils.def(vehicleRequest.toCity, ""));
        toStateTv.setText(Utils.def(vehicleRequest.toState, ""));
        shipmentDateTv.setText(Utils.formatDateSimple(vehicleRequest.shipmentDate));
        vehicleTypeTv.setText(Utils.def(vehicleRequest.getName(), ""));
        vehicleCountTv.setText(String.valueOf(vehicleRequest.quantity));
    }

    private void updateQuoteUI() {
        updateQuantityUI();
        dialogQuoteAmountEdit.setText(String.valueOf(vehicleRequestQuote.amount));
        dialogQuoteCommentsEdit.setText(Utils.def(vehicleRequestQuote.comments, ""));
    }

    private void updateQuantityUI() {
        dialogQuoteVehicleCount.setText(String.valueOf(vehicleRequestQuote.quantity));
        dialogQuoteCountSubBtn.setEnabled(vehicleRequestQuote.quantity > 1);
        dialogQuoteCountAddBtn.setEnabled(vehicleRequestQuote.quantity < vehicleRequest.quantity);
    }

    private void setClickListeners() {
        doneBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String amountStr = dialogQuoteAmountEdit.getText().toString().trim();
                if (Utils.not(amountStr)) {
                    dialogQuoteAmountEdit.setText("0");
                    dialogQuoteAmountEdit.setError("No amount entered");
                    return;
                }
                int amount = Integer.parseInt(amountStr);
                if (amount == 0) {
                    dialogQuoteAmountEdit.setText("0");
                    dialogQuoteAmountEdit.setError("No amount entered");
                    return;
                }
                String comments = dialogQuoteCommentsEdit.getText().toString().trim();

                vehicleRequestQuote.comments = comments;
                vehicleRequestQuote.amount = amount;

                try {
                    JSONObject data = vehicleRequestQuote.toJson();
                    makeSendQuoteRequest(data);
                } catch (JSONException e) {
                    e.printStackTrace();
                    toast("Error: unable to form json");
                }

            }
        });
        cancelBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
        dialogQuoteCountAddBtn.setOnClickListener(new QuantityChangeClickListener(1));
        dialogQuoteCountSubBtn.setOnClickListener(new QuantityChangeClickListener(-1));
    }

    private void makeSendQuoteRequest(JSONObject data) {
        SendQuoteRequest request = new SendQuoteRequest(data, new QuoteRequestListener());
        queue(request);
    }

    private void setViewVariables() {
        fromCityTv = dialogView.findViewById(R.id.from_city_tv);
        fromStateTv = dialogView.findViewById(R.id.from_state_tv);
        toCityTv = dialogView.findViewById(R.id.to_city_tv);
        toStateTv = dialogView.findViewById(R.id.to_state_tv);
        shipmentDateTv = dialogView.findViewById(R.id.shipment_date_tv);
        vehicleTypeTv = dialogView.findViewById(R.id.vehicle_type_tv);
        vehicleCountTv = dialogView.findViewById(R.id.vehicle_count_tv);

        cancelBtn = dialogView.findViewById(R.id.cancel_btn);
        doneBtn = dialogView.findViewById(R.id.done_btn);
        dialogQuoteCountAddBtn = dialogView.findViewById(R.id.dialog_quote_count_add_btn);
        dialogQuoteCountSubBtn = dialogView.findViewById(R.id.dialog_quote_count_sub_btn);
        dialogQuoteVehicleCount = dialogView.findViewById(R.id.dialog_quote_vehicle_count);
        dialogQuoteAmountEdit = dialogView.findViewById(R.id.dialog_quote_amount_edit);
        dialogQuoteCommentsEdit = dialogView.findViewById(R.id.dialog_quote_comments_edit);
    }

    private class QuantityChangeClickListener implements View.OnClickListener {
        private int value;

        public QuantityChangeClickListener(int value) {
            this.value = value;
        }

        @Override
        public void onClick(View v) {
            int newQuantity = vehicleRequestQuote.quantity + value;
            if (newQuantity >= 1 && newQuantity <= vehicleRequest.quantity) {
                vehicleRequestQuote.quantity = newQuantity;
                updateQuantityUI();
            }
        }
    }


    private class QuoteRequestListener extends ApiResponseListener {
        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            toast("Quote Sent");

            if (listener != null) {
                try {
                    VehicleRequestQuote quote = getQuote(response);
                    listener.onSuccess(quote);
                } catch (JSONException e) {
                    toast("error reading response");
                    return;
                }
            }
            dismiss();
        }

        @Override
        public void onError() {
            dismissProgress();
            dismiss();
        }
    }

    private VehicleRequestQuote getQuote(JSONObject jsonObject) throws JSONException {
        JSONObject data = jsonObject.getJSONObject("data");
        return VehicleRequestQuote.fromJson(data);
    }

    public interface QuoteSentListener {
        void onSuccess(VehicleRequestQuote quote);
    }

}