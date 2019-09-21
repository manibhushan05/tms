package in.aaho.android.aahocustomers.loads;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import in.aaho.android.aahocustomers.common.Utils;

/**
 * Created by mani on 6/8/16.
 */
public class VehicleRequestQuote {

    public long id;
    public long transactionId;
    public long vehicleRequestId;
    public int quantity;
    public int amount;
    public String comments;
    public Date createdOn;
    public Date updatedOn;

    private static final String ID_KEY = "id";
    private static final String TRANSACTION_ID_KEY = "transaction_id";
    private static final String VEHICLE_REQUEST_ID_KEY = "vehicle_request_id";
    private static final String QUANTITY_KEY = "quantity";
    private static final String AMOUNT_KEY = "amount";
    private static final String COMMENTS_KEY = "comments";
    private static final String CREATED_ON_KEY = "created_on";
    private static final String UPDATED_ON_KEY = "updated_on";


    public VehicleRequestQuote(long id, long transactionId, long vehicleRequestId, int quantity,
                               int amount, String comments, Date createdOn, Date updatedOn) {
        this.id = id;
        this.transactionId = transactionId;
        this.vehicleRequestId = vehicleRequestId;
        this.quantity = quantity;
        this.amount = amount;
        this.comments = comments;
        this.createdOn = createdOn;
        this.updatedOn = updatedOn;
    }

    public static VehicleRequestQuote newQuote(long vehicleRequestId, int quantity, int amount, String comments) {
        return new VehicleRequestQuote(0, 0, vehicleRequestId, quantity, amount, comments, null, null);
    }

    public static VehicleRequestQuote fromJson(JSONObject jsonObject) throws JSONException {
        if (jsonObject == null || jsonObject.length() == 0) {
            return null;
        }
        return new VehicleRequestQuote(
                Utils.getLong(jsonObject, ID_KEY),
                Utils.getLong(jsonObject, TRANSACTION_ID_KEY),
                Utils.getLong(jsonObject, VEHICLE_REQUEST_ID_KEY),
                jsonObject.getInt(QUANTITY_KEY),
                jsonObject.getInt(AMOUNT_KEY),
                Utils.get(jsonObject, COMMENTS_KEY),
                Utils.getDate(jsonObject, CREATED_ON_KEY),
                Utils.getDate(jsonObject, UPDATED_ON_KEY)
        );
    }

    public JSONObject toJson() throws JSONException {
        JSONObject obj = new JSONObject();
        obj.put(VEHICLE_REQUEST_ID_KEY, vehicleRequestId);
        obj.put(QUANTITY_KEY, quantity);
        obj.put(AMOUNT_KEY, amount);
        obj.put(COMMENTS_KEY, comments == null ? JSONObject.NULL : comments);
        return obj;
    }

    public static List<VehicleRequestQuote> fromJson(JSONArray jsonArray) throws JSONException {
        List<VehicleRequestQuote> vehicles = new ArrayList<>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            VehicleRequestQuote vehicle = fromJson(obj);
            vehicles.add(vehicle);
        }
        return vehicles;
    }


    public static VehicleRequestQuote copy(VehicleRequestQuote other) {
        if (other == null) {
            return null;
        }
        return new VehicleRequestQuote(
                other.id, other.transactionId, other.vehicleRequestId, other.quantity,
                other.amount, other.comments, other.createdOn, other.updatedOn
        );
    }

    public String getQuoteText() {
        return quantity + " Vehicles for \u20B9 " + amount;
    }

}
