package in.aaho.android.employee.notification;

import android.text.TextUtils;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.Utils;

public class MyNotification {
    private static String TAG = "MyNotification";
    private static final String NOTIFICATION_DATE_KEY = "notification_date";
    private static final String TITLE_KEY = "title";
    private static final String BODY_KEY = "body";
    private static final String DATA_KEY = "data";
    private static final String RECEIVED_TIME_KEY = "received_time";

    public String notificationDate = "";
    public String title = "";
    public String body = "";
    public String receivedTime = "";

    public MyNotification(String notificationDate, String title, String body, String receivedTime) {
        this.notificationDate = notificationDate;
        this.title = title;
        this.body = body;
        this.receivedTime = receivedTime;
    }

    public String toJson(MyNotification myNotification) {
        /* check if myNotification has data
        *  check
         * if prefs has prev data
        *   if yes check for notification_date
        *       if diff then delete prev prefs and insert new one
        *       if not diff then append data
        *  else insert new data to prefs*/
        JSONObject jsonObject = null;
        try {
            if(myNotification == null)
                return null;

            String jsonNotification = Aaho.getMyNotificationJson();
            JSONArray jsonDataArray = null;
            if (TextUtils.isEmpty(jsonNotification)) {
                jsonObject = new JSONObject();
                jsonDataArray = new JSONArray();
                jsonObject.put(NOTIFICATION_DATE_KEY, myNotification.notificationDate);
            } else {
                jsonObject = new JSONObject(jsonNotification);
                String notificationDate = Utils.get(jsonObject,NOTIFICATION_DATE_KEY);
                if(notificationDate.equalsIgnoreCase(myNotification.notificationDate)) {
                    // append data here
                    jsonDataArray = jsonObject.getJSONArray(DATA_KEY);
                } else {
                    // clear prev data here and add new data
                    Aaho.setMyNotification("");
                    jsonDataArray = new JSONArray();
                    jsonObject.put(NOTIFICATION_DATE_KEY, myNotification.notificationDate);
                }
            }
            JSONObject jsonData = new JSONObject();
            jsonData.put(TITLE_KEY, myNotification.title);
            jsonData.put(BODY_KEY, myNotification.body);
            jsonData.put(RECEIVED_TIME_KEY, myNotification.receivedTime);
            jsonDataArray.put(jsonData);

            jsonObject.put(DATA_KEY, jsonDataArray);
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG, "Error while converting to json! ex=" + e.getLocalizedMessage());
        }
        return jsonObject.toString();
    }

    public static ArrayList<MyNotification> fromJson() {
        ArrayList<MyNotification> myNotificationsList = new ArrayList<>();
        try {
            /* Get the notification json from prefs
            *  If not null then retrieve data from prefs */
            String jsonNotification = Aaho.getMyNotificationJson();
            if(!TextUtils.isEmpty(jsonNotification)) {
                JSONObject jsonObject = new JSONObject(jsonNotification);
                if (jsonObject != null) {
                    String notificationDate = Utils.get(jsonObject, NOTIFICATION_DATE_KEY);
                    // Check if today's notification if not reset data & return null
                    if (notificationDate.equalsIgnoreCase(getTodayDate("ddMMyyyy"))) {
                        if (jsonObject.has(DATA_KEY)) {
                            JSONArray jsonDataArray = jsonObject.getJSONArray(DATA_KEY);
                            if (jsonDataArray != null & jsonDataArray.length() > 0) {
                                for (int count = 0; count < jsonDataArray.length(); count++) {
                                    JSONObject jsonData = jsonDataArray.getJSONObject(count);

                                    MyNotification myNotification = new MyNotification(
                                            notificationDate, Utils.get(jsonData, TITLE_KEY),
                                            Utils.get(jsonData, BODY_KEY),
                                            Utils.get(jsonData, RECEIVED_TIME_KEY));
                                    myNotificationsList.add(myNotification);
                                }
                            }
                        }
                    } else {
                        Aaho.setMyNotification("");
                    }
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG, "Error while converting from json! ex=" + e.getLocalizedMessage());
        }
        return myNotificationsList;
    }

    /* To get the my notification count from prefs */
    public static int getMyNotificationCount(String jsonNotification) {
        int count = 0;
        try {
            if(jsonNotification != null){
                JSONObject jsonObject = new JSONObject(jsonNotification);
                String notificationDate = Utils.get(jsonObject,NOTIFICATION_DATE_KEY);
                // Check if today's notification if not reset data & return null
                if (notificationDate.equalsIgnoreCase(getTodayDate("ddMMyyyy"))) {
                    if (jsonObject.has(DATA_KEY)) {
                        JSONArray jsonDataArray = jsonObject.getJSONArray(DATA_KEY);
                        if(jsonDataArray != null) {
                            count = jsonDataArray.length();
                        }
                    }
                } else {
                    Aaho.setMyNotification("");
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            Log.e(TAG, "Error while getting count from json! ex=" + e.getLocalizedMessage());
        }
        return count;
    }

    public static String getTodayDate(String formatDate) {
        SimpleDateFormat dateFormat = new SimpleDateFormat(formatDate);
        String today = dateFormat.format(Calendar.getInstance().getTime());
        return today;
    }
}
