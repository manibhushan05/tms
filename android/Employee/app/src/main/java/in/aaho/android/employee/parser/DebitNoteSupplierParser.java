package in.aaho.android.employee.parser;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import in.aaho.android.employee.common.Utils;
import in.aaho.android.employee.models.DebitNoteSupplierData;

/**
 * Created by Suraj M
 */

public class DebitNoteSupplierParser {
    private JSONArray jsonArray;
    private ArrayList<DebitNoteSupplierData> arrayList;

    public DebitNoteSupplierParser(JSONArray jsonArray) {
        this.jsonArray = jsonArray;
    }


    public ArrayList<DebitNoteSupplierData> getDebitNoteSupplierList() {
        arrayList = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            try {
                JSONObject jsonObject = (JSONObject) jsonArray.get(i);
                DebitNoteSupplierData data = new DebitNoteSupplierData();
                data.setPaidTo(Utils.get(jsonObject,"broker_name"));
                data.setAmount(Utils.get(jsonObject,"adjusted_amount"));
                data.setDate(Utils.get(jsonObject,"approved_on"));
                data.setStatus(Utils.get(jsonObject,"reason_text"));
                data.setDebitNoteNo(Utils.get(jsonObject,"remarks"));

                arrayList.add(data);

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        return arrayList;
    }

}
