package com.example.projecttwo;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DatabaseHelper extends SQLiteOpenHelper {

    private static final String DATABASE_NAME = "InventoryDB";
    private static final int DATABASE_VERSION = 1;

    public DatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {

        db.execSQL(
                "CREATE TABLE users (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                        "username TEXT UNIQUE," +
                        "password TEXT)"
        );

        db.execSQL(
                "CREATE TABLE inventory (" +
                        "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                        "itemName TEXT," +
                        "quantity INTEGER)"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db,
                          int oldVersion,
                          int newVersion) {

        db.execSQL("DROP TABLE IF EXISTS users");
        db.execSQL("DROP TABLE IF EXISTS inventory");
        onCreate(db);
    }

    // ================= USERS =================

    public boolean registerUser(String username, String password) {
        SQLiteDatabase db = this.getWritableDatabase();

        ContentValues values = new ContentValues();
        values.put("username", username);
        values.put("password", password);

        long result = db.insert("users", null, values);
        return result != -1;
    }

    public boolean loginUser(String username, String password) {
        SQLiteDatabase db = this.getReadableDatabase();

        Cursor cursor = db.rawQuery(
                "SELECT * FROM users WHERE username=? AND password=?",
                new String[]{username, password}
        );

        boolean exists = cursor.getCount() > 0;
        cursor.close();
        return exists;
    }

    // ================= INVENTORY CRUD =================

    public boolean addItem(String itemName, int quantity) {
        SQLiteDatabase db = this.getWritableDatabase();

        ContentValues values = new ContentValues();
        values.put("itemName", itemName);
        values.put("quantity", quantity);

        long result = db.insert("inventory", null, values);
        return result != -1;
    }

    public Cursor getAllItems() {
        SQLiteDatabase db = this.getReadableDatabase();

        return db.rawQuery("SELECT * FROM inventory", null);
    }

    public boolean updateItem(String itemName, int quantity) {
        SQLiteDatabase db = this.getWritableDatabase();

        ContentValues values = new ContentValues();
        values.put("quantity", quantity);

        int rowsAffected = db.update(
                "inventory",
                values,
                "itemName=?",
                new String[]{itemName}
        );

        return rowsAffected > 0;
    }

    public boolean deleteItem(String itemName) {
        SQLiteDatabase db = this.getWritableDatabase();

        int rowsDeleted = db.delete(
                "inventory",
                "itemName=?",
                new String[]{itemName}
        );

        return rowsDeleted > 0;
    }
}