package in.aaho.android.ownr.vehicles;

import android.util.Log;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import in.aaho.android.ownr.common.Utils;

/**
 * Created by shobhit on 16/11/16.
 */

public class VehicleNumber {
    public static final Pattern PATTERN = Pattern.compile(
            "([A-Za-z]{2})[ \\-,.]*([0-9]{1,2})[ \\-,.]*([A-Za-z]{1,3})[ \\-,.]*([0-9]{1,4})"
    );

    public static String displayFormat(String number) {
        if (number == null) {
            return null;
        }
        number = number.trim();
        Matcher matcher = PATTERN.matcher(number);
        if (matcher.find()) {
            number = matcher.group(1) + matcher.group(2) + " " + matcher.group(3) + " " + matcher.group(4);
        }
        return number.toUpperCase();
    }

    public static String compareFormat(String number) {
        if (number == null) {
            return null;
        }
        number = number.trim();
        Matcher matcher = PATTERN.matcher(number);
        if (matcher.find()) {
            number = matcher.group(1) + matcher.group(2) + matcher.group(3) + matcher.group(4);
        } else {
            number = number.replace("-", "").replace(",", "").replace(",", "").replace(" ", "");
        }
        return number.toLowerCase();
    }

    public static boolean equal(String num1, String num2) {
        num1 = compareFormat(num1);
        num2 = compareFormat(num2);
        return Utils.equals(num1, num2);
    }
}
