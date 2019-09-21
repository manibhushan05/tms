package in.aaho.android.ownr;

import android.os.SystemClock;
import android.support.test.annotation.UiThreadTest;
import android.support.test.rule.ActivityTestRule;
import android.test.ActivityTestCase;
import android.util.Log;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import static android.support.test.internal.runner.junit4.statement.UiThreadStatement.runOnUiThread;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

public class LoginActivityTest extends ActivityTestCase {

    private final String TAG = getClass().getSimpleName();

    @Rule
    public ActivityTestRule<LoginActivity> mLoginActivityActivityTestRule
            = new ActivityTestRule<>(LoginActivity.class);

    LoginActivity mActivity = null;

    @Before
    public void setUp() throws Exception {
        Log.i(TAG, "setUp");
        mLoginActivityActivityTestRule.launchActivity(null);
        mActivity = mLoginActivityActivityTestRule.getActivity();
    }

    @Test
    public void isValidInputByUserTest() {
        Log.i(TAG, "testLogin");

        try {
            runOnUiThread(new Runnable() {

                @Override
                public void run() {

                    // Stuff that updates the UI

                    mActivity.setPrerequisites("", "");
                    validateLoginInput(false);

                    mActivity.setPrerequisites("roku", "");
                    validateLoginInput(false);

                    mActivity.setPrerequisites("", "owner");
                    validateLoginInput(false);

                    mActivity.setPrerequisites("roku", "owner");
                    validateLoginInput(true);
                }
            });
        } catch (Throwable throwable) {
            throwable.printStackTrace();
        }
    }

    public void validateLoginInput(boolean expectedResult) {
        assertEquals(mActivity.isValidInputByUserTest(
                mActivity.getmUsernameEditText().toString(),
                mActivity.getmPasswordEditText().toString()), expectedResult);
    }


    @Test
    public void LoginApiTest() {
        Log.i(TAG, "LoginApiTest");
        try {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {

                    validateLoginApi("", "",false);
                    validateLoginApi("roku", "",false);
                    validateLoginApi("", "owner.1900",true);
                    validateLoginApi("rokuuu", "owner.1900",false);
                    validateLoginApi("roku", "owner.1900",true);
                }
            });
        } catch (Throwable throwable) {
            throwable.printStackTrace();
        }
    }

    public void validateLoginApi(String userName,String password,boolean expectedResult) {
        Aaho.setToken(null);
        mActivity.makeLoginRequestTest(userName,password);
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