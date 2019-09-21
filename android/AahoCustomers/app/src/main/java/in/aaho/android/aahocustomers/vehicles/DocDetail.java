package in.aaho.android.aahocustomers.vehicles;

import java.util.Arrays;
import java.util.List;

/**
 * Created by shobhit on 17/11/16.
 */

public class DocDetail {
    private static final List<String> TYPES = Arrays.asList(
            "rc", "perm", "fit", "in", "puc", "pan", "dec", "dl", "ac"
    );

    private String type;
    private String title, docId;
    private boolean send;

    public DocDetail(String type, String title, String docId, boolean send) {
        if (!TYPES.contains(type)) {
            throw new RuntimeException("wrong type");
        }
        this.type = type;
        this.title = title;
        this.docId = docId;
        this.send = send;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        if (!TYPES.contains(type)) {
            throw new RuntimeException("wrong type");
        }
        this.type = type;
    }

    public boolean shouldSend() {
        return send;
    }

    public void setSend(boolean send) {
        this.send = send;
    }

    public String getDocId() {
        return docId;
    }

    public void setDocId(String docId) {
        this.docId = docId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }
}
