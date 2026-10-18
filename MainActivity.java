package com.example.projecttwo;

import android.database.Cursor;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.GridView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {

    DatabaseHelper databaseHelper;

    Button btnAddItem, btnUpdateItem, btnDeleteItem;
    EditText etItemName, etQuantity;
    GridView gridInventory;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        databaseHelper = new DatabaseHelper(this);

        btnAddItem = findViewById(R.id.btnAddItem);
        btnUpdateItem = findViewById(R.id.btnUpdateItem);
        btnDeleteItem = findViewById(R.id.btnDeleteItem);

        etItemName = findViewById(R.id.etItemName);
        etQuantity = findViewById(R.id.etQuantity);

        gridInventory = findViewById(R.id.gridInventory);

        // adds item to inventory
        btnAddItem.setOnClickListener(v -> {

            String itemName = etItemName.getText().toString().trim();
            String qtyText = etQuantity.getText().toString().trim();

            if (itemName.isEmpty() || qtyText.isEmpty()) {
                Toast.makeText(this, "Fill all fields", Toast.LENGTH_SHORT).show();
                return;
            }

            int quantity = Integer.parseInt(qtyText);

            if (databaseHelper.addItem(itemName, quantity)) {
                Toast.makeText(this, "Item added", Toast.LENGTH_SHORT).show();
                loadInventory();
            } else {
                Toast.makeText(this, "Add failed", Toast.LENGTH_SHORT).show();
            }
        });

        // updates inventory items
        btnUpdateItem.setOnClickListener(v -> {

            String itemName = etItemName.getText().toString().trim();
            String qtyText = etQuantity.getText().toString().trim();

            if (itemName.isEmpty() || qtyText.isEmpty()) {
                Toast.makeText(this, "Fill all fields", Toast.LENGTH_SHORT).show();
                return;
            }

            int quantity = Integer.parseInt(qtyText);

            if (databaseHelper.updateItem(itemName, quantity)) {
                Toast.makeText(this, "Item updated", Toast.LENGTH_SHORT).show();
                loadInventory();
            } else {
                Toast.makeText(this, "Update failed", Toast.LENGTH_SHORT).show();
            }
        });

        // deletes inventory items
        btnDeleteItem.setOnClickListener(v -> {

            String itemName = etItemName.getText().toString().trim();

            if (itemName.isEmpty()) {
                Toast.makeText(this, "Enter item name", Toast.LENGTH_SHORT).show();
                return;
            }

            if (databaseHelper.deleteItem(itemName)) {
                Toast.makeText(this, "Item deleted", Toast.LENGTH_SHORT).show();
                loadInventory();
            } else {
                Toast.makeText(this, "Delete failed", Toast.LENGTH_SHORT).show();
            }
        });

        loadInventory();
    }

    private void loadInventory() {

        Cursor cursor = databaseHelper.getAllItems();
        ArrayList<String> items = new ArrayList<>();

        while (cursor.moveToNext()) {

            String item =
                    "ID: " + cursor.getInt(0) +
                            "\nItem: " + cursor.getString(1) +
                            "\nQty: " + cursor.getInt(2);

            items.add(item);
        }

        cursor.close();

        ArrayAdapter<String> adapter =
                new ArrayAdapter<>(
                        this,
                        android.R.layout.simple_list_item_1,
                        items
                );

        gridInventory.setAdapter(adapter);
    }
}