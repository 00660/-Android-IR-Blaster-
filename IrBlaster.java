import android.os.IBinder;
import java.lang.reflect.Method;

public class IrBlaster {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: irblaster <freq> <pattern>");
            return;
        }
        try {
            int freq = Integer.parseInt(args[0]);
            String[] patternStr = args[1].split(",");
            int[] pattern = new int[patternStr.length];
            for (int i = 0; i < patternStr.length; i++) {
                pattern[i] = Integer.parseInt(patternStr[i].trim());
            }

            Class<?> smClass = Class.forName("android.os.ServiceManager");
            Method getService = smClass.getMethod("getService", String.class);
            IBinder binder = (IBinder) getService.invoke(null, "consumer_ir");
            
            if (binder == null) {
                System.err.println("Error: No IR service!");
                return;
            }

            Class<?> stubClass = Class.forName("android.hardware.IConsumerIrService$Stub");
            Method asInterface = stubClass.getMethod("asInterface", IBinder.class);
            Object irService = asInterface.invoke(null, binder);

            Method transmit = irService.getClass().getMethod("transmit", String.class, int.class, int[].class);
            transmit.invoke(irService, "com.android.shell", freq, pattern);

            System.out.println("Success! Freq: " + freq);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
