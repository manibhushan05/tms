package in.aaho.android.employee.adapter;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.employee.R;
import in.aaho.android.employee.models.BookingDetailsRateData;

/**
 * Created by mani on 16/12/16.
 */

public class BookingDetailsRateAdapter extends RecyclerView.Adapter<BookingDetailsRateAdapter.MyViewHolder> {
    private List<BookingDetailsRateData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder{
        private TextView tvRateLabel;
        private TextView tvRateValue;


        public MyViewHolder(View view) {
            super(view);
            tvRateLabel = view.findViewById(R.id.tv_rate_label);
            tvRateValue = view.findViewById(R.id.tv_rate_value);

        }

    }
    public BookingDetailsRateAdapter(List<BookingDetailsRateData> dataList) {
        this.dataList = dataList;
    }
    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.payment_details_rows, parent, false);

        return new MyViewHolder(itemView);
    }
    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        BookingDetailsRateData bookingDetailsRateData = dataList.get(position);
        holder.tvRateLabel.setText(bookingDetailsRateData.getRateLabel());
        holder.tvRateValue.setText(bookingDetailsRateData.getRateValue());
    }
    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
