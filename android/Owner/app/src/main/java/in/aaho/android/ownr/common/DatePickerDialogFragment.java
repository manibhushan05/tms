package in.aaho.android.ownr.common;

import android.annotation.SuppressLint;
import android.app.DatePickerDialog;
import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.DialogFragment;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import in.aaho.android.ownr.R;

/**
 * Created by mani on 7/2/18.
 */

public class DatePickerDialogFragment  extends DialogFragment implements View.OnClickListener {

    FilterDialogListener filterDialogListener;
    EditText fromDateEditText,toDateEditText;
    Button btnFilter;
    int id;
    final int FROM_DATE = 1;
    final int TO_DATE = 2;
    String fromDate,toDate;

    // Defines the listener interface
    public interface FilterDialogListener {
        void onFinishFilterDialog(String fromDate,String toDate);
    }

    public DatePickerDialogFragment() {
        // Empty constructor is required for DialogFragment
        // Make sure not to add arguments to the constructor
        // Use `newInstance` instead as shown below
    }

    @SuppressLint("ValidFragment")
    public DatePickerDialogFragment(FilterDialogListener listener) {
        filterDialogListener = listener;
    }

    /*public static DatePickerDialogFragment newInstance(String title) {
        DatePickerDialogFragment frag = new DatePickerDialogFragment();
        Bundle args = new Bundle();
        args.putString("title", title);
        frag.setArguments(args);
        return frag;
    }*/

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return getActivity().getLayoutInflater().inflate(R.layout.dialog_fragment_date_picker, container,false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        findViews(view);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.fromDateEditText:
                id = FROM_DATE;
                setError(fromDateEditText,"");
                pickDate();
                break;
            case R.id.toDateEditText:
                id = TO_DATE;
                setError(toDateEditText,"");
                pickDate();
                break;
            case R.id.btnFilter:
                fromDate = fromDateEditText.getText().toString();
                toDate = toDateEditText.getText().toString();
                if(isValidInputByUser()) {
                    filterDialogListener.onFinishFilterDialog(fromDate,toDate);
                    dismiss();
                }
                break;
            default:
                break;
        }
    }

    private void findViews(View view) {
        fromDateEditText = view.findViewById(R.id.fromDateEditText);
        fromDateEditText.setOnClickListener(this);
        toDateEditText = view.findViewById(R.id.toDateEditText);
        toDateEditText.setOnClickListener(this);
        btnFilter = view.findViewById(R.id.btnFilter);
        btnFilter.setOnClickListener(this);
    }

    private boolean isValidInputByUser() {
        if(TextUtils.isEmpty(fromDate)) {
            setError(fromDateEditText,"This filed can not be left blank!");
            return false;
        } else if(TextUtils.isEmpty(toDate)) {
            setError(toDateEditText,"This filed can not be left blank!");
            return false;
        } else {
            return true;
        }
    }

    private void setError(EditText editText,String errMsg) {
        if(TextUtils.isEmpty(errMsg)) {
            editText.setError(null);
        } else {
            editText.setError(errMsg);
        }
    }

    private void pickDate() {
        final Calendar c = Calendar.getInstance();
        int year  = c.get(Calendar.YEAR);
        int month = c.get(Calendar.MONTH);
        int day   = c.get(Calendar.DAY_OF_MONTH);
        DatePickerDialog datePickerDialog = new DatePickerDialog(getActivity(),
                datePickerListener, year, month,day);
        datePickerDialog.show();
    }

    private DatePickerDialog.OnDateSetListener datePickerListener = new DatePickerDialog.OnDateSetListener() {

        // when dialog box is closed, below method will be called.
        public void onDateSet(DatePicker view, int selectedYear, int selectedMonth, int selectedDay) {
            String year1 = String.valueOf(selectedYear);
            String month1 = String.valueOf(selectedMonth + 1);
            String day1 = String.valueOf(selectedDay);
            String pickedDate = day1+"-"+month1+"-"+year1;

            SimpleDateFormat shipmentDateFormat = new SimpleDateFormat("dd-MMM-yyyy");
            SimpleDateFormat pickerDateFormat = new SimpleDateFormat("dd-MM-yyyy");

            try {
                Date dtPickedDate = pickerDateFormat.parse(pickedDate);
                pickedDate = shipmentDateFormat.format(dtPickedDate);
                if(id == FROM_DATE) {
                    fromDateEditText.setText(pickedDate);
                } else if(id == TO_DATE) {
                    toDateEditText.setText(pickedDate);
                } else {
                    // do nothing
                }

            } catch (ParseException e) {
                e.printStackTrace();
            }
        }
    };

}
