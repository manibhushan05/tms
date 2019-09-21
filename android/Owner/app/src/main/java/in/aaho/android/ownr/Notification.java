package in.aaho.android.ownr;

public class Notification {

    private String title;
    private String description;

    public String getTitle() {
        return title!=null?title:"";
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description!=null?description:"";
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
