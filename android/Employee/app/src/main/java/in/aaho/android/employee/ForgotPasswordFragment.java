package in.aaho.android.employee;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.design.widget.TextInputEditText;
import android.support.design.widget.TextInputLayout;
import android.support.v4.app.Fragment;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.android.volley.Request;
import com.android.volley.VolleyError;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import in.aaho.android.employee.common.ApiResponseListener;
import in.aaho.android.employee.common.EditTextWatcher;
import in.aaho.android.employee.common.MainApplication;
import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.requests.ForgotPasswordRequest;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link OnForgotPasswordSubmitListener} interface
 * to handle interaction events.
 * Use the {@link ForgotPasswordFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class ForgotPasswordFragment extends Fragment implements
        View.OnClickListener {

    private final String TAG = getClass().getSimpleName();

    private Button btnSubmit;
    private TextInputEditText username_editext;
    private TextInputLayout userNameTextInputLayout;

    private ProgressDialog progress;

    private OnForgotPasswordSubmitListener mListener;

    public ForgotPasswordFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     * @return A new instance of fragment ForgotPasswordFragment.
     */
    public static ForgotPasswordFragment newInstance() {
        ForgotPasswordFragment fragment = new ForgotPasswordFragment();
        /*Bundle args = new Bundle();
        fragment.setArguments(args);*/
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {

        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_forgot_password, container, false);
        findViews(view);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        username_editext.addTextChangedListener(new EditTextWatcher() {
            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                if(i == 0) {
                    userNameTextInputLayout.setError(null);
                }
            }
        });
    }

    private void makeOTPRequest() {
        ForgotPasswordRequest forgotPasswordRequest = new ForgotPasswordRequest(
                username_editext.getText().toString(), new ForgotPasswordResponseListener());
        queue(forgotPasswordRequest);
    }

    private class ForgotPasswordResponseListener extends ApiResponseListener {

        @Override
        public void onResponse(JSONObject response) {
            dismissProgress();
            String resp = response.toString();
            try {
                String msg = Utils.get(response,"msg");
                if(response != null && response.getString("status")
                        .equalsIgnoreCase("success")) {
                    onSubmit(msg,username_editext.getText().toString());
                } else {
                    Utils.toast(msg);
                }
            } catch (JSONException e) {
                e.printStackTrace();
                Utils.toast("Could not send OTP! Please try again later.");
                Log.e(TAG,"error reading response data:\n" + resp);
            }
        }

        @Override
        public void onErrorResponse(VolleyError error) {
            super.onErrorResponse(error);
            dismissProgress();
            try {
                if (error != null && error.networkResponse != null
                        && error.networkResponse.data != null) {
                    String errorMsg = new String(error.networkResponse.data, "UTF-8");
                    Utils.toast(errorMsg);
                    Log.i(TAG, errorMsg);
                }
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            } catch (Exception ex) {
                Log.e(TAG,"Exception = "+ex.getLocalizedMessage());
            }
        }
    }

    public void onSubmit(String msg,String username) {
        if (mListener != null) {
            mListener.onForgotPasswordSubmit(msg,username);
        }
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnForgotPasswordSubmitListener) {
            mListener = (OnForgotPasswordSubmitListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnForgotPasswordSubmitListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    void findViews(View view) {
        btnSubmit = view.findViewById(R.id.btnSubmit);
        btnSubmit.setOnClickListener(this);
        username_editext = view.findViewById(R.id.username_editext);
        userNameTextInputLayout = view.findViewById(R.id.userNameTextInputLayout);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.btnSubmit:
                if(isValidInputByUser()) {
                    makeOTPRequest();
                }
                break;
            default:
                break;
        }
    }

    boolean isValidInputByUser() {
        String userName = username_editext.getText().toString();
        if(TextUtils.isEmpty(userName)) {
            userNameTextInputLayout.setError("User Name can not be left blank!");
            return false;
        } else {
            return true;
        }
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnForgotPasswordSubmitListener {
        void onForgotPasswordSubmit(String msg, String username);
    }

    public void queue(Request<?> request) {
        queue(request, true);
    }

    public void queue(Request<?> request, boolean progress) {
        MainApplication.queueRequest(request);
        if (progress) {
            if(!getActivity().isFinishing()) {
                showProgress();
            }
        }
    }

    private void showProgress() {
        progress = new ProgressDialog(getActivity());
        progress.setTitle(R.string.progress_title);
        progress.setMessage(getActivity().getString(R.string.progress_msg));
        progress.setCanceledOnTouchOutside(false);
        progress.show();
    }

    private void dismissProgress() {
        if(progress != null) {
            progress.dismiss();
        }
    }
}
