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
 * Created by aaho on 23/04/18.
 */

public class AahoOfficeParser {

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

    /*public ArrayList<AahoOfficeParser> getArrayListFromJson(JSONArray jsonArray) {
        if (jsonArray != null && jsonArray.length() > 0) {
            Gson gson = new Gson();
            Type listType = new TypeToken<ArrayList<AahoOfficeParser>>() {
            }.getType();
            return gson.fromJson(jsonArray.toString(), listType);
        } else {
            return null;
        }
    }*/

    public ArrayList<AahoOfficeParser> getArrayListFromJson(JSONArray jsonArray) {
        ArrayList<AahoOfficeParser> aahoOfficeList = new ArrayList<>();
        if (jsonArray != null && jsonArray.length() > 0) {
            for (int i = 0; i < jsonArray.length(); i++) {
                AahoOfficeParser aahoOfficeParser = new AahoOfficeParser();
                JSONObject office = null;
                try {
                    office = jsonArray.getJSONObject(i);
                    if (office != null) {
                        int id = Integer.valueOf(Utils.get(office, "id"));
                        String name = Utils.get(office, "branch_name");
                        aahoOfficeParser.setId(id);
                        aahoOfficeParser.setText(name);
                        aahoOfficeList.add(aahoOfficeParser);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }

        return aahoOfficeList;
    }

    public ArrayList<AahoOfficeParser> getCitySuggestionData(String searchQuery) {
        ArrayList<AahoOfficeParser> ListData = new ArrayList<>();
        try {
            URL js = new URL(in.aaho.android.employee.requests.AahoOfficeDataRequest
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
                AahoOfficeParser aahoOfficeParser = new AahoOfficeParser();
                ListData = aahoOfficeParser.getArrayListFromJson(jsonArray);
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



