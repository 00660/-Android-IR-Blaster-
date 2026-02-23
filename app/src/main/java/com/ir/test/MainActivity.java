package com.ir.test;
import android.app.Activity;
import android.hardware.ConsumerIrManager;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final ConsumerIrManager ir = (ConsumerIrManager) getSystemService(CONSUMER_IR_SERVICE);
        findViewById(R.id.send).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    int f = Integer.parseInt(((EditText)findViewById(R.id.freq)).getText().toString());
                    String[] pStr = ((EditText)findViewById(R.id.pattern)).getText().toString().split(",");
                    int[] p = new int[pStr.length];
                    for (int i=0; i<pStr.length; i++) p[i] = Integer.parseInt(pStr[i].trim());
                    ir.transmit(f, p);
                    Toast.makeText(MainActivity.this, "发送成功", Toast.LENGTH_SHORT).show();
                } catch (Exception e) { Toast.makeText(MainActivity.this, "错误", Toast.LENGTH_SHORT).show(); }
            }
        });
    }
}
