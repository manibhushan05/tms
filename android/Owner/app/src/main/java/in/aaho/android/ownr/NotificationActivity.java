package in.aaho.android.ownr;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.text.TextUtils;
import android.util.Log;

import com.android.volley.VolleyError;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.lang.reflect.Type;
import java.util.ArrayList;

import in.aaho.android.ownr.adapter.NotificationAdapter;
import in.aaho.android.ownr.common.ApiResponseListener;
import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.requests.GetNotificationCountRequest;
import in.aaho.android.ownr.requests.GetNotificationDataRequest;

public class NotificationActivity extends BaseActivity {

    private RecyclerView recyclerView;
    private NotificationAdapter notificationAdapter;
    private ArrayList<Notification> notificationArrayList = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_notification);
        setToolbarTitle("Notification");

        findViews();
        getNotificationDataFromServer();
    }

    private void findViews() {
        recyclerView = findViewById(R.id.recycler_view);
        notificationAdapter = new NotificationAdapter(notificationArrayList);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(this);
        linearLayoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(linearLayoutManager);
        recyclerView.setAdapter(notificationAdapter);
    }

    // call api to get notification count
    private void getNotificationDataFromServer() {
        String jsonResponse = "{\n" +
                "\"notifications\": [ {\n" +
                "    \"title\": \"New Notification\",\n" +
                "    \"description\": \"This is description\"\n" +
                "},\n" +
                "{\n" +
                "    \"title\": \"New Notification\",\n" +
                "    \"description\": \"This is description\"\n" +
                "},\n" +
                "{\n" +
                "    \"title\": \"New Notification\",\n" +
                "    \"description\": \"This is description\"\n" +
                "}\n" +
                " ]\n" +
                "}";

        try {
            Gson gson = new Gson();
            JSONObject jsonObject = new JSONObject(jsonResponse);
            JSONArray jsonArray = jsonObject.getJSONArray("notifications");
            Type type = new TypeToken<ArrayList<Notification>>(){}.getType();
            notificationArrayList = gson.fromJson(jsonArray.toString(),type);
            notificationAdapter = new NotificationAdapter(notificationArrayList);
            recyclerView.setAdapter(notificationAdapter);
            notificationAdapter.notifyDataSetChanged();
        } catch (JSONException e) {
            Log.e("NotificationActivity","Error parsing json");
        }



        /*GetNotificationDataRequest request = new GetNotificationDataRequest(new ApiResponseListener() {
            @Override
            public void onResponse(JSONObject response) {
                Gson gson = new Gson();
                JSONArray jsonArray = response.optJSONArray("notifications");
                Type type = new TypeToken<ArrayList<Notification>>(){}.getType();
                notificationArrayList = gson.fromJson(jsonArray.toString(),type);
                notificationAdapter = new NotificationAdapter(notificationArrayList);
                recyclerView.setAdapter(notificationAdapter);
                notificationAdapter.notifyDataSetChanged();
            }

            @Override
            public void onErrorResponse(VolleyError error) {
                super.onErrorResponse(error);
                dismissProgress();
            }
        });

        queue(request);*/
    }
}
