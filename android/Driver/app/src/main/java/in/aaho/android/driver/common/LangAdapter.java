package in.aaho.android.driver.common;

/**
 * Created by shobhit on 6/8/16.
 */

import android.graphics.Color;
import android.graphics.Typeface;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.Arrays;
import java.util.List;

import in.aaho.android.driver.R;


public class LangAdapter extends RecyclerView.Adapter<LangAdapter.MyViewHolder> {


    private List<Lang> langList;
    private LanguageSelectDialogFragment.OnChangeListener listener;
    private LanguageSelectDialogFragment fragment;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView textView;
        private LangClickListener langClickListener;

        public MyViewHolder(View view) {
            super(view);
            textView = (TextView) view;

            langClickListener = new LangClickListener();
            textView.setOnClickListener(langClickListener);
        }

        public void updateListenerPositions(int position) {
            langClickListener.updatePosition(position);
        }

    }

    public LangAdapter(LanguageSelectDialogFragment fragment, LanguageSelectDialogFragment.OnChangeListener listener) {
        this.listener = listener;
        this.fragment = fragment;
        this.langList = Arrays.asList(Lang.getLanguages());
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.lang_list_item, parent, false);

        return new MyViewHolder(itemView);
    }


    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        Lang lang = langList.get(position);
        boolean isCurrent = lang.isCurrent();
        holder.updateListenerPositions(position);
        holder.textView.setText(lang.name);
        holder.textView.setTypeface(null, isCurrent ? Typeface.BOLD : Typeface.NORMAL);
        holder.textView.setBackgroundColor(isCurrent ? Color.GRAY : Color.TRANSPARENT);
    }

    @Override
    public int getItemCount() {
        return langList.size();
    }

    private class LangClickListener extends ListItemListerner implements View.OnClickListener {

        @Override
        public void onClick(View v) {
            Lang selected = langList.get(position);
            if (!selected.isCurrent()) {
                boolean updated = Lang.setLanguage(selected.code);
                if (updated && listener != null) {
                    listener.onChange();
                }
            }
            fragment.dismiss();
        }
    }


}
