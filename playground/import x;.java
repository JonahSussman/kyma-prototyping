import x;

public class Complex {
    private int member_variable;

    public static double[] add(double[] a, double[] b) {
        return new double[]{a[0] + b[0], a[1] + b[1]};
    }

    public static double[] sub(double[] a, double[] b) { ... }
    public static double[] mul(double[] a, double[] b) { ... }
    public static double[] div(double[] a, double[] b) { ... }
}
