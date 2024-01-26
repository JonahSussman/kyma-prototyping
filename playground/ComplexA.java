import x;

public class Complex {
    private int member_variable;

    // Method to add two complex numbers
    public static double[] add(double[] a, double[] b) {
        return new double[]{a[0] + b[0], a[1] + b[1]};
    }

    // Method to subtract two complex numbers
    public static double[] sub(double[] a, double[] b) {
        return new double[]{a[0] - b[0], a[1] - b[1]};
    }

    // Method to multiply two complex numbers
    public static double[] mul(double[] a, double[] b) {
        double real = a[0] * b[0] - a[1] * b[1];
        double imag = a[0] * b[1] + a[1] * b[0];
        return new double[]{real, imag};
    }

    // Method to divide two complex numbers
    public static double[] div(double[] a, double[] b) {
        double divisor = b[0] * b[0] + b[1] * b[1];
        double real = (a[0] * b[0] + a[1] * b[1]) / divisor;
        double imag = (a[1] * b[0] - a[0] * b[1]) / divisor;
        return new double[]{real, imag};
    }
}
