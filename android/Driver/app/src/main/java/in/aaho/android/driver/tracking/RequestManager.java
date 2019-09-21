package in.aaho.android.driver.tracking;

import android.os.AsyncTask;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import in.aaho.android.driver.CompressionUtils;
import in.aaho.android.driver.requests.Api;

public class RequestManager {

    private static final int TIMEOUT = 30 * 1000;

    public interface RequestHandler {
        void onComplete(boolean success);
    }

    private static class RequestAsyncTask extends AsyncTask<String, Void, Boolean> {

        private RequestHandler handler;

        public RequestAsyncTask(RequestHandler handler) {
            this.handler = handler;
        }

        @Override
        protected Boolean doInBackground(String... data) {
            return sendRequest(data[0]);
        }

        @Override
        protected void onPostExecute(Boolean result) {
            handler.onComplete(result);
        }
    }

    public static boolean sendRequest(String data) {
        InputStream inputStream = null;
        try {
            URL url = new URL(Api.TRACCAR_LOCATION_UPDATE_URL);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setReadTimeout(TIMEOUT);
            connection.setConnectTimeout(TIMEOUT);
            connection.setDoOutput(true);
            connection.setRequestMethod("POST");

            OutputStream outputStream = connection.getOutputStream();
            outputStream.write(CompressionUtils.compress(data.getBytes()));
            outputStream.flush();
            outputStream.close();

            inputStream = connection.getInputStream();
            while (inputStream.read() != -1);
            return true;
        } catch (IOException error) {
            return false;
        } finally {
            try {
                if (inputStream != null) {
                    inputStream.close();
                }
            } catch (IOException secondError) {
                return false;
            }

        }
    }

    public static void sendRequestAsync(String data, RequestHandler handler) {
        RequestAsyncTask task = new RequestAsyncTask(handler);
        task.execute(data);
    }

}
