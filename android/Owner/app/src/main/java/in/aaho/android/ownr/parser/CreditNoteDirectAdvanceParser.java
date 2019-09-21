package in.aaho.android.ownr.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.ownr.common.Utils;
import in.aaho.android.ownr.model.CreditNoteDirectAdvanceData;

/**
 * Created by Suraj M
 */

public class CreditNoteDirectAdvanceParser {
    private JSONArray jsonArray;
    private ArrayList<CreditNoteDirectAdvanceData> arrayList;

    public CreditNoteDirectAdvanceParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }


    public ArrayList<CreditNoteDirectAdvanceData> getCreditNoteDirectAdvanceList() {
        arrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                CreditNoteDirectAdvanceData data = new CreditNoteDirectAdvanceData();
                data.setPaidTo(Utils.get(jsonObject,"broker_name"));
                data.setAmount(Utils.get(jsonObject,"adjusted_amount"));
                data.setDate(Utils.get(jsonObject,"approved_on"));
                data.setStatus(Utils.get(jsonObject,"reason_text"));
                data.setCreditNoteNo(Utils.get(jsonObject,"remarks"));

                arrayList.add(data);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return arrayList;
    }

}
