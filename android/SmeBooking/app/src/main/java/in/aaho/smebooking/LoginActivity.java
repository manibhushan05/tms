package in.aaho.smebooking;

import android.content.Intent;
import android.graphics.Paint;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.SpannableString;
import android.text.style.UnderlineSpan;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

public class LoginActivity extends AppCompatActivity {
    EditText etUsername;
    EditText etPassword;
    Button btlogin;
    TextView txtNeedHelp;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        getID();
        txtNeedHelp.setPaintFlags(txtNeedHelp.getPaintFlags()| Paint.UNDERLINE_TEXT_FLAG);
        btlogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                SendLoginData();

            }
        });
        txtNeedHelp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(LoginActivity.this,ContactUs.class));
            }
        });
    }

    private void getID() {
        etUsername = (EditText) findViewById(R.id.input_username);
        etPassword = (EditText) findViewById(R.id.input_password);
        btlogin = (Button) findViewById(R.id.btLogin);
        txtNeedHelp = (TextView)findViewById(R.id.need_help);
    }

    private String getLoginData() {
        getID();
        PreferenceManager.getDefaultSharedPreferences(getApplicationContext())
                .edit()
                .putString("username", etUsername.getText().toString()).commit();
        JSONObject jsonObject = new JSONObject();
        try {
            jsonObject.put("username", etUsername.getText().toString());
            jsonObject.put("password", etPassword.getText().toString());
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jsonObject.toString();
    }

    private void SendLoginData() {


        // Response received from the server
        Response.Listener<String> responseListener = new Response.Listener<String>() {
            @Override
            public void onResponse(String response) {
                try {
                    String success = "success";
                    Log.e("response", response + "    from server");
//                            JSONObject jsonResponse = new JSONObject(response);
//                            boolean success = jsonResponse.getBoolean("success");

                    if (response.equals(success)) {
                        startActivity(new Intent(LoginActivity.this,MainActivity.class));
                        Log.i("SUCCESS", success);
                    } else {

//                        AlertDialog.Builder builder = new AlertDialog.Builder(LocationService.this);
//                        builder.setMessage("Login Failed")
//                                .setNegativeButton("Retry", null)
//                                .create()
//                                .show();
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        };

        LoginRequest gpsDataRequest = new LoginRequest(getLoginData(), responseListener);
        RequestQueue queue = Volley.newRequestQueue(LoginActivity.this);
        queue.add(gpsDataRequest);
    }
}
