package in.aaho.android.employee.parser;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;

import in.aaho.android.employee.Aaho;
import in.aaho.android.employee.common.Utils;

/**
 * Created by aaho on 22/04/18.
 */

public class VehicleTypeParser {

    private String text;
    private int id;

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public Integer getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    /*public ArrayList<VehicleTypeParser> getArrayListFromJson(JSONArray jsonArray) {
        if (jsonArray != null && jsonArray.length() > 0) {
            Gson gson = new Gson();
            Type listType = new TypeToken<ArrayList<VehicleTypeParser>>() {
            }.getType();
            return gson.fromJson(jsonArray.toString(), listType);
        } else {
            return null;
        }
    }*/

    public ArrayList<VehicleTypeParser> getArrayListFromJson(JSONArray jsonArray) {
        ArrayList<VehicleTypeParser> vehicleTypeList = new ArrayList<>();
        if (jsonArray != null && jsonArray.length() > 0) {
            for (int i = 0; i < jsonArray.length(); i++) {
                VehicleTypeParser vehicleTypeParser = new VehicleTypeParser();
                JSONObject city = null;
                try {
                    city = jsonArray.getJSONObject(i);
                    if (city != null) {
                        int id = Integer.valueOf(Utils.get(city, "id"));
                        String name = Utils.get(city, "vehicle_type");
                        vehicleTypeParser.setId(id);
                        vehicleTypeParser.setText(name);
                        vehicleTypeList.add(vehicleTypeParser);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }

        return vehicleTypeList;
    }

    public ArrayList<VehicleTypeParser> getCitySuggestionData(String searchQuery) {
        ArrayList<VehicleTypeParser> ListData = new ArrayList<>();
        try {
            URL js = new URL(in.aaho.android.employee.requests.VehicleTypeDataRequest
                    .makeSearchUrl("25", searchQuery));
            URLConnection urlConnection = js.openConnection();
            urlConnection.setRequestProperty("Authorization", "Token " + Aaho.getToken());
            BufferedReader reader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
            String line = reader.readLine();
            String resp = line.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONArray jsonArray = jsonObject.getJSONArray("data");
                /*JSONArray jsonArray = jsonObject.getJSONArray("results");*/
                VehicleTypeParser vehicleTypeParser = new VehicleTypeParser();
                ListData = vehicleTypeParser.getArrayListFromJson(jsonArray);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        } catch (Exception e1) {
            e1.printStackTrace();
        }
        return ListData;
    }

    @Override
    public String toString() {
        return this.getText();
    }

}
