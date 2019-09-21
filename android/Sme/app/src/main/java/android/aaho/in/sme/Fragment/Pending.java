package android.aaho.in.sme.Fragment;

import android.aaho.in.sme.Adapter.ListViewAdapter;
import android.aaho.in.sme.Model.Model;
import android.content.Context;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import android.aaho.in.sme.R;
import android.widget.AdapterView;
import android.widget.ListView;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;


public class Pending extends Fragment {
    View rootView;
    private ArrayList<Model> productList;

    public Pending() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        rootView = inflater.inflate(R.layout.fragment_pending, container, false);
        productList = new ArrayList<Model>();
        ListView lview = (ListView) rootView.findViewById(R.id.listview);
        ListViewAdapter adapter = new ListViewAdapter(getActivity(), productList);
        lview.setAdapter(adapter);

        populateList();

        adapter.notifyDataSetChanged();

        lview.setOnItemClickListener(new AdapterView.OnItemClickListener() {

            @Override
            public void onItemClick(AdapterView<?> parent, View view,
                                    int position, long id) {
                String sno = ((TextView)view.findViewById(R.id.sNo)).getText().toString();
                String product = ((TextView)view.findViewById(R.id.product)).getText().toString();
                String category = ((TextView)view.findViewById(R.id.category)).getText().toString();
                String price = ((TextView)view.findViewById(R.id.price)).getText().toString();

                Toast.makeText(getActivity().getApplicationContext(), "S no : " + sno +"\n"
                        +"Product : " + product +"\n"
                        +"Category : " +category +"\n"
                        +"Price : " +price, Toast.LENGTH_SHORT).show();
            }
        });

        return rootView;
    }


    private void populateList() {

        Model item1, item2, item3, item4, item5;

        item1 = new Model("234533", "United Ocean Ship Management Pte Ltd ", "United Ocean Ship Management Pte Ltd ", "15/05/2016");
        productList.add(item1);

        item2 = new Model("287688", "United Ocean Ship Management Pte Ltd ", "United Ocean Ship Management Pte Ltd ", "15/05/2016");
        productList.add(item2);

        item3 = new Model("287588", "United Ocean Ship Management Pte Ltd ", "United Ocean Ship Management Pte Ltd ", "15/05/2016");
        productList.add(item3);

        item4 = new Model("287648", "United Ocean Ship Management Pte Ltd ","United Ocean Ship Management Pte Ltd ", "15/05/2016");
        productList.add(item4);

        item5 = new Model("287689", "United Ocean Ship Management Pte Ltd ", "United Ocean Ship Management Pte Ltd ","15/05/2016");
        productList.add(item5);
    }
}
