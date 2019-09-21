package in.aaho.android.ownr.docs;

import android.content.DialogInterface;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;

import in.aaho.android.ownr.common.BaseActivity;
import in.aaho.android.ownr.common.BaseDialogFragment;
import in.aaho.android.ownr.common.Cache;
import in.aaho.android.ownr.common.ImageReadyListener;
import in.aaho.android.ownr.R;

/**
 * Created by mani on 8/8/16.
 */

public class ImageDialogFragment extends BaseDialogFragment {

    private Button okButton;
    private ImageView imageView;
    private LinearLayout progressView;
    private View dialogView;
    private String key;

    private ImageReadyListener listener;


    public static void showNewDialog(BaseActivity activity, String key) {
        if (key == null || key.trim().isEmpty()) {
            return;
        } else {
            key = key.trim();
        }
        ImageDialogFragment dialog = new ImageDialogFragment();
        dialog.key = key;
        dialog.show(activity.getSupportFragmentManager(), "image_preview_fragment");
    }

    public ImageReadyListener getListener() {
        if (listener == null) {
            listener = new ImageReadyListener() {
                @Override
                public void onReady(Bitmap bitmap) {
                    updateImageUI(bitmap);
                }
            };
        }
        return listener;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        dialogView = inflater.inflate(R.layout.image_preview_dialog, container, false);

        setViewVariables();
        setClickListeners();

        loadImage();
        return dialogView;
    }

    private void setClickListeners() {
        okButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dismiss();
            }
        });
    }

    private void setViewVariables() {
        okButton = dialogView.findViewById(R.id.image_preview_dialog_ok_btn);
        imageView = dialogView.findViewById(R.id.image_preview_dialog_image_view);
        progressView = dialogView.findViewById(R.id.image_preview_dialog_progress);
    }

    private void loadImage() {
        Cache cache = Cache.getInstance(getActivity());
        cache.getImage(key, getListener());
    }

    private void updateImageUI(Bitmap bitmap) {
        if (progressView != null) {
            progressView.setVisibility(View.GONE);
        }
        if (imageView != null) {
            imageView.setVisibility(View.VISIBLE);
            if (bitmap == null) {
                imageView.setImageResource(R.drawable.ic_error_black_24dp);
            } else {
                imageView.setImageBitmap(bitmap);
            }
        }
    }

    @Override
    public void onDismiss(DialogInterface dialog) {
        if (listener != null) {
            listener.cancel();
        }
        super.onDismiss(dialog);
    }
}