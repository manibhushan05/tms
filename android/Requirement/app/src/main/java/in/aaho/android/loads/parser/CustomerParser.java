package in.aaho.android.loads.parser;

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

/**
 * Created by aaho on 22/04/18.
 */

public class CustomerParser {

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

    public ArrayList<CustomerParser> getArrayListFromJson(JSONArray jsonArray) {
        if (jsonArray != null && jsonArray.length() > 0) {
            Gson gson = new Gson();
            Type listType = new TypeToken<ArrayList<CustomerParser>>() {
            }.getType();
            return gson.fromJson(jsonArray.toString(), listType);
        } else {
            return null;
        }
    }

    public ArrayList<CustomerParser> getCitySuggestionData(String searchQuery) {
        ArrayList<CustomerParser> ListData = new ArrayList<>();
        try {
            URL js = new URL(in.aaho.android.loads.requests.CustomerDataRequest
                    .makeSearchUrl("25", searchQuery));
            URLConnection jc = js.openConnection();
            BufferedReader reader = new BufferedReader(new InputStreamReader(jc.getInputStream()));
            String line = reader.readLine();
            String resp = line.toString();
            try {
                JSONObject jsonObject = new JSONObject(resp);
                JSONArray jsonArray = jsonObject.getJSONArray("results");
                CustomerParser customerParser = new CustomerParser();
                ListData = customerParser.getArrayListFromJson(jsonArray);
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

