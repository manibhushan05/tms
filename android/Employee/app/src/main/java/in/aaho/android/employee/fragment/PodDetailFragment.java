package in.aaho.android.employee.fragment;

import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;

import com.bogdwellers.pinchtozoom.ImageMatrixTouchHandler;
import com.squareup.picasso.Picasso;

import in.aaho.android.employee.R;
import in.aaho.android.employee.other.POD_DOCS;


/**
 * A simple {@link Fragment} subclass.
 */
public class PodDetailFragment extends Fragment {

    private ImageView imageView,imgRotate;
    private POD_DOCS mPod_docs;
    private float angle = 0;

    public PodDetailFragment() {
        // Required empty public constructor
    }

    public static PodDetailFragment newInstance(POD_DOCS pod_docs) {
        PodDetailFragment fragment = new PodDetailFragment();
        Bundle args = new Bundle();
        args.putSerializable("Pod_Docs",pod_docs);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mPod_docs = (POD_DOCS) getArguments().getSerializable("Pod_Docs");
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_pod_detail, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        findViews(view);

        imageView.setOnTouchListener(new ImageMatrixTouchHandler(view.getContext()));

        imgRotate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(angle == 360)
                    angle = 0;
                else {
                    angle = angle + 90;
                }
                imageView.setRotation(angle);
            }
        });

        // load image from here
        Picasso.with(getActivity())
                .load(mPod_docs.getUrl())
                .into(imageView);
    }

    private void findViews(View view) {
        imageView = view.findViewById(R.id.imageView);
        imgRotate = view.findViewById(R.id.imgRotate);
    }

}
