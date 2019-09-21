package in.aaho.android.ownr;

import android.os.SystemClock;
import android.support.test.rule.ActivityTestRule;
import android.test.ActivityTestCase;
import android.util.Log;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import in.aaho.android.ownr.vehicles.VehicleListActivity;

import static android.support.test.internal.runner.junit4.statement.UiThreadStatement.runOnUiThread;

public class VehicleListActivityTest extends ActivityTestCase {
    private final String TAG = getClass().getSimpleName();

    @Rule
    public ActivityTestRule<VehicleListActivity> mLoginActivityActivityTestRule
            = new ActivityTestRule<>(VehicleListActivity.class);

    VehicleListActivity mActivity = null;

    @Before
    public void setUp() throws Exception {
        Log.i(TAG, "setUp");
        mLoginActivityActivityTestRule.launchActivity(null);
        mActivity = mLoginActivityActivityTestRule.getActivity();
    }

    @Test
    public void VehicleListApiTest() {
        Log.i(TAG, "LoginApiTest");
        try {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {

                    validateVehicleListApi("", "",false);
                    validateVehicleListApi("roku", "",false);
                    validateVehicleListApi("", "owner.1900",true);
                    validateVehicleListApi("rokuuu", "owner.1900",false);
                    validateVehicleListApi("roku", "owner.1900",true);
                }
            });
        } catch (Throwable throwable) {
            throwable.printStackTrace();
        }
    }

    public void validateVehicleListApi(String userName, String password, boolean expectedResult) {
        Aaho.setToken(null);
        mActivity.makeVehicleListRequestTest();
        String token = Aaho.getToken();
        SystemClock.sleep(2000);    // sleep for given ms to get response
        if(expectedResult){
            assertNotNull(token);
        } else {
            assertNull(token);
        }
    }

    @After
    public void tearDown() throws Exception {
        Log.i(TAG, "tearDown");
        mActivity = null;
    }
}