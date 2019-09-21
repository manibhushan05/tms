package in.aaho.android.employee.activity;

import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentTransaction;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.MenuItem;

import in.aaho.android.employee.R;
import in.aaho.android.employee.fragment.PODListFragment;
import in.aaho.android.employee.fragment.PodDetailFragment;
import in.aaho.android.employee.other.POD_DOCS;

public class ViewPODActivity extends AppCompatActivity implements
        PODListFragment.IOnListItemSelectionListener {

    FragmentManager mFragmentManager;
    FragmentTransaction mFragmentTransaction;
    final int MI_POD_LIST_FRAGMENT = 1;
    final int MI_POD_DETAIL_FRAGMENT = 2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_pod);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("POD");
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setDisplayShowHomeEnabled(true);

        mFragmentManager = getSupportFragmentManager();

        new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {
                loadFragment(MI_POD_LIST_FRAGMENT,null);
            }
        },100);
    }

    @Override
    public void onBackPressed() {
        processBackStack();
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            onBackPressed();
            return true;
        }
        return false;
    }

    void processBackStack() {
        int count = mFragmentManager.getBackStackEntryCount();
        if(count == 1) {
            mFragmentManager.popBackStack();
        } else {
            super.onBackPressed();
        }
    }

    private void loadFragment(int id,Bundle bundle) {
        switch (id) {
            case MI_POD_LIST_FRAGMENT:
                addFragment(new PODListFragment(),
                        "frag_pod_list", false);
                break;
            case MI_POD_DETAIL_FRAGMENT:
                POD_DOCS pod_docs = null;
                if (bundle != null) {
                    pod_docs = (POD_DOCS) bundle.getSerializable("Pod_Docs");
                }
                addFragment(PodDetailFragment.newInstance(pod_docs),
                        "frag_pod_details", true);
                break;
            default:
                break;
        }
    }

    public void addFragment(Fragment fragment, String tag, boolean isAddToBackStack) {
        mFragmentTransaction = mFragmentManager.beginTransaction();
        mFragmentTransaction.add(R.id.container,fragment,tag);
        if(isAddToBackStack)
            mFragmentTransaction.addToBackStack(tag);
        mFragmentTransaction.commit();
    }

    @Override
    public void onListItemSelected(POD_DOCS pod_docs) {
        // load the view pod detail fragment from here
        Bundle bundle = new Bundle();
        bundle.putSerializable("Pod_Docs",pod_docs);
        loadFragment(MI_POD_DETAIL_FRAGMENT,bundle);
    }
}
