package in.aaho.android.customer.adapter;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.support.v4.app.ActivityCompat;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;

import java.util.List;

import in.aaho.android.customer.R;
import in.aaho.android.customer.data.AllocatedVehicleData;

/**
 * Created by mani on 2/8/16.
 */
public class AllocatedVehicleAdapter extends RecyclerView.Adapter<AllocatedVehicleAdapter.MyViewHolder> {
    private List<AllocatedVehicleData> dataList;

    public class MyViewHolder extends RecyclerView.ViewHolder {
        public TextView tvTypeOfVehicle;
        public TextView tvVehicleNumber;
        public TextView tvDriverLicenceNo;
        public TextView tvDriverName;
        public TextView tvDriverContactNumber;
        private ImageButton imageButtonCallDriver;


        public MyViewHolder(View view) {
            super(view);
            tvTypeOfVehicle = (TextView) view.findViewById(R.id.tvAlloctedVehicleTypeOfVehicle);
            tvVehicleNumber = (TextView) view.findViewById(R.id.tvAlloctedVehicleVehicleNumber);
            tvDriverLicenceNo = (TextView) view.findViewById(R.id.tvAlloctedVehicleLicenceNumber);
            tvDriverName = (TextView) view.findViewById(R.id.viDriver);
            tvDriverContactNumber = (TextView) view.findViewById(R.id.viContactNo);
            imageButtonCallDriver = (ImageButton) view.findViewById(R.id.imageButtonCallDriver);
            imageButtonCallDriver.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Intent callIntent = new Intent(Intent.ACTION_CALL);
                    callIntent.setData(Uri.parse("tel:"+tvDriverContactNumber.getText().toString()));
                    if (ActivityCompat.checkSelfPermission(v.getContext(), Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED) {
                        // TODO: Consider calling
                        //    ActivityCompat#requestPermissions
                        // here to request the missing permissions, and then overriding
                        //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                        //                                          int[] grantResults)
                        // to handle the case where the user grants the permission. See the documentation
                        // for ActivityCompat#requestPermissions for more details.
                        return;
                    }
                    v.getContext().startActivity(callIntent);
                }
            });
        }
    }


    public AllocatedVehicleAdapter(List<AllocatedVehicleData> dataList) {
        this.dataList = dataList;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.allocated_vehicle_info_rows, parent, false);

        return new MyViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        AllocatedVehicleData allocatedVehicleData = dataList.get(position);
        holder.tvTypeOfVehicle.setText(allocatedVehicleData.getTypeOfVehicle());
        holder.tvVehicleNumber.setText(allocatedVehicleData.getVehicleNumber());
        holder.tvDriverLicenceNo.setText(allocatedVehicleData.getDriverLicenceNumber());
        holder.tvDriverName.setText(allocatedVehicleData.getDriverName());
        holder.tvDriverContactNumber.setText(allocatedVehicleData.getDriverContactNumber());
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }
}
