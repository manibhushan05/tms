package in.aaho.android.ownr.parser;

import java.util.ArrayList;

/**
 * Created by mani on 28/7/16.
 */
public class JsonResponse {
    private ArrayList<PendingTransactionDataParser> pendingArrayList;
    private ArrayList<ConfirmTransaction> confirmArrayList;
    private ArrayList<InTransitTransaction> intransitArrayList;
    private ArrayList<DeliveredTransaction> deliveredArrayList;
    private ArrayList<CancelledTransaction> cancelledArrayList;

    public ArrayList<PendingTransactionDataParser> getPendingArrayList() {
        return pendingArrayList;
    }
    public int getSize(){
        return getPendingArrayList().size();
    }
}
