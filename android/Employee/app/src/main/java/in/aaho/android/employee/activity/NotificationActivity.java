package in.aaho.android.employee.activity;

import android.app.Notification;
import android.os.Bundle;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

import in.aaho.android.employee.R;
import in.aaho.android.employee.adapter.NotificationAdapter;
import in.aaho.android.employee.common.BaseActivity;
import in.aaho.android.employee.notification.MyNotification;

public class NotificationActivity extends BaseActivity {

    private TextView emptyView;
    private ImageView imgMoveToTop;
    private RecyclerView recyclerView;
    private SwipeRefreshLayout refreshLayout;
    private NotificationAdapter notificationAdapter;
    private ArrayList<MyNotification> dataList = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_notification);
        setToolbarTitle("My Notification");

        findViews();
        setClickListeners();
        loadMyNotification(false);
    }

    private void loadMyNotification(boolean isSwiped) {
        if(isSwiped) {
            dataList.clear();
            refreshLayout.setRefreshing(false);
        }
        dataList.addAll(sortList(MyNotification.fromJson()));
        notificationAdapter.notifyDataSetChanged();
        setEmptyViewVisibility();
    }

    private void findViews() {
        emptyView = findViewById(R.id.empty_view);
        recyclerView = findViewById(R.id.recycler_view);
        refreshLayout = findViewById(R.id.swipe_refresh_layout);
        imgMoveToTop = findViewById(R.id.imgMoveToTop);
        notificationAdapter = new NotificationAdapter(this,dataList);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(this);
        linearLayoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(linearLayoutManager);
        recyclerView.setAdapter(notificationAdapter);
    }

    private void setClickListeners() {
        refreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                loadMyNotification(true);
            }
        });
        imgMoveToTop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(recyclerView != null && dataList.size() > 0) {
                    recyclerView.scrollToPosition(0);
                }
            }
        });
    }

    private void setEmptyViewVisibility() {
        if (dataList.size() == 0) {
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
        } else {
            emptyView.setVisibility(View.GONE);
            recyclerView.setVisibility(View.VISIBLE);
        }
    }

    public void setMoveToTopVisibility(int scrollPosition) {
        if(scrollPosition < 12) {
            imgMoveToTop.setVisibility(View.GONE);
        } else {
            imgMoveToTop.setVisibility(View.VISIBLE);
        }
    }

    /* Sorts the given arrayList in descending order */
    private ArrayList<MyNotification> sortList(ArrayList<MyNotification> myNotifications) {
        Collections.sort(myNotifications, new Comparator<MyNotification>() {
            public int compare(MyNotification o1, MyNotification o2) {
                if (o1.receivedTime == null || o2.receivedTime == null)
                    return 0;
                return o2.receivedTime.compareTo(o1.receivedTime);
            }
        });

        return myNotifications;
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
            dataList = gson.fromJson(jsonArray.toString(),type);
            notificationAdapter = new NotificationAdapter(this,dataList);
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
                dataList = gson.fromJson(jsonArray.toString(),type);
                notificationAdapter = new NotificationAdapter(dataList);
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
