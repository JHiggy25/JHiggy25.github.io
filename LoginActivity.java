package com.example.projecttwo;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class LoginActivity extends AppCompatActivity {

    private EditText etUsername;
    private EditText etPassword;
    private Button btnLogin;
    private Button btnRegister;

    private DatabaseHelper databaseHelper;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        databaseHelper = new DatabaseHelper(this);

        etUsername = findViewById(R.id.etUsername);
        etPassword = findViewById(R.id.etPassword);

        btnLogin = findViewById(R.id.btnLogin);
        btnRegister = findViewById(R.id.btnRegister);

        // Login existing user
        btnLogin.setOnClickListener(v -> {

            String username = etUsername.getText().toString().trim();
            String password = etPassword.getText().toString().trim();

            if (databaseHelper.loginUser(username, password)) {

                Toast.makeText(
                        LoginActivity.this,
                        "Login successful",
                        Toast.LENGTH_SHORT
                ).show();

                Intent intent =
                        new Intent(LoginActivity.this,
                                MainActivity.class);

                startActivity(intent);
                finish();

            } else {

                Toast.makeText(
                        LoginActivity.this,
                        "Invalid username or password",
                        Toast.LENGTH_SHORT
                ).show();
            }
        });

        // Create new account
        btnRegister.setOnClickListener(v -> {

            String username = etUsername.getText().toString().trim();
            String password = etPassword.getText().toString().trim();

            if (username.isEmpty() || password.isEmpty()) {

                Toast.makeText(
                        LoginActivity.this,
                        "Enter username and password",
                        Toast.LENGTH_SHORT
                ).show();

                return;
            }

            boolean success =
                    databaseHelper.registerUser(
                            username,
                            password
                    );

            if (success) {

                Toast.makeText(
                        LoginActivity.this,
                        "Account created successfully",
                        Toast.LENGTH_SHORT
                ).show();

            } else {

                Toast.makeText(
                        LoginActivity.this,
                        "Username already exists",
                        Toast.LENGTH_SHORT
                ).show();
            }
        });
    }
}