package in.aaho.android.aahocustomers.transaction;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import in.aaho.android.aahocustomers.R;
import in.aaho.android.aahocustomers.common.Utils;

/**
 * Created by aaho on 11/07/18.
 */

public class FinancialPaidFragment extends Fragment implements View.OnClickListener{

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View root_view = inflater.inflate(R.layout.fragment_confirmed, container, false);
        //setHasOptionsMenu(true);
//        rootView = root_view;
//        findViews(root_view);
//        SetupRecycleView(root_view);
        return root_view;
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.filterImageButton:
//                showFilterDialog();
                break;
            default:
                break;
        }
    }

}
