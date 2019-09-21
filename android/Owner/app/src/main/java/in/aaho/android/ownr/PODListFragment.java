package in.aaho.android.ownr;

import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import java.util.ArrayList;

import in.aaho.android.ownr.adapter.PODListAdapter;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * to handle interaction events.
 * Use the {@link PODListFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class PODListFragment extends Fragment {

    private final String TAG = getClass().getSimpleName();
    ArrayList<POD_DOCS> pod_docsArrayList;
    private RecyclerView recyclerView;
    private LinearLayoutManager layoutManager;
    private PODListAdapter podListAdapter;
    IOnListItemSelectionListener iOnListItemSelectionListener;

    public PODListFragment() {
        // Required empty public constructor
    }

    public interface IOnListItemSelectionListener {
        void onListItemSelected(POD_DOCS pod_docs);
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     * @return A new instance of fragment ForgotPasswordFragment.
     */
    public static PODListFragment newInstance(ArrayList<POD_DOCS> pod_docsArrayList) {
        PODListFragment fragment = new PODListFragment();
        /*Bundle args = new Bundle();
        args.putSerializable("Pod_Docs_List",pod_docsArrayList);
        fragment.setArguments(args);*/
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setRetainInstance(true);
        if (getArguments() != null) {
            //pod_docsArrayList = (ArrayList<POD_DOCS>) getArguments().getSerializable("Pod_Docs_List");
            //Toast.makeText(getActivity(), pod_docsArrayList.toString() , Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_pod_list, container, false);
        findViews(view);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        ObjectFileUtil<ArrayList<POD_DOCS>> objectFileUtil = new ObjectFileUtil<>(
                getActivity(),"PodDocList");
        pod_docsArrayList = objectFileUtil.get();

        podListAdapter = new PODListAdapter(pod_docsArrayList,iOnListItemSelectionListener);
        recyclerView.setAdapter(podListAdapter);
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if(context instanceof IOnListItemSelectionListener) {
            iOnListItemSelectionListener = (IOnListItemSelectionListener) context;
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        if(iOnListItemSelectionListener != null) {
            iOnListItemSelectionListener = null;
        }
    }

    void findViews(View view) {
        recyclerView = view.findViewById(R.id.recycler_view);
        layoutManager = new LinearLayoutManager(getActivity());
        layoutManager.setOrientation(LinearLayoutManager.VERTICAL);
        recyclerView.setLayoutManager(layoutManager);
    }

}
