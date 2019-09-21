package in.aaho.android.ownr.booking;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.R;

/**
 * Created by mani on 8/8/16.
 */

public class BookingResultDialogFragment extends BaseDialogFragment {

    private Button requestButton;
    private Button cancelButton;

    private View dialogView;

    private BookingActivity bookingActivity;
    private long bookingId;

    public void setBookingActivity(BookingActivity bookingActivity) {
        this.bookingActivity = bookingActivity;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.booking_result_dialog, container, false);

        setViewVariables();
        setClickListeners();

        return dialogView;
    }

    private void setClickListeners() {
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                BookingResultDialogFragment.this.dismiss();
            }
        });
        requestButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendRequestToVendors();
            }
        });
    }

    private void setViewVariables() {
        requestButton = dialogView.findViewById(R.id.booking_result_request_btn);
        cancelButton = dialogView.findViewById(R.id.booking_result_cancel_btn);
    }

    private void sendRequestToVendors() {
        bookingActivity.showVendorDialog(bookingId);
        dismiss();
    }

    public void setBookingId(long bookingId) {
        this.bookingId = bookingId;
    }
}