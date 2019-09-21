package in.aaho.android.aahocustomers.data;

/**
 * Created by aaho on 14/06/18.
 */

public class PODData {
    String url;
    String thumbUrl;
    String bucketname;
    String foldername;
    String filename;
    String uuid;
    String displayUrl;

    public PODData(String url, String thumbUrl, String bucketname,
                   String foldername, String filename, String uuid, String displayUrl) {
        this.url = url;
        this.thumbUrl = thumbUrl;
        this.bucketname = bucketname;
        this.foldername = foldername;
        this.filename = filename;
        this.uuid = uuid;
        this.displayUrl = displayUrl;
    }

    public String getUrl() {
        return url;
    }

    public String getThumbUrl() {
        return thumbUrl;
    }

    public String getBucketname() {
        return bucketname;
    }

    public String getFoldername() {
        return foldername;
    }

    public String getFilename() {
        return filename;
    }

    public String getUuid() {
        return uuid;
    }

    public String getDisplayUrl() {
        return displayUrl;
    }
}
