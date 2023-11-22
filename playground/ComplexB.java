public class Complex {
    // Fields for the real and imaginary parts
    private double real;
    private double imag;

    // Constructor
    public Complex(double real, double imag) {
        this.real = real;
        this.imag = imag;
    }

    // Getter methods
    public double getReal() {
        return real;
    }

    public double getImag() {
        return imag;
    }

    // Method to add two complex numbers
    public static Complex add(Complex a, Complex b) {
        return new Complex(a.real + b.real, a.imag + b.imag);
    }

    // Method to subtract two complex numbers
    public static Complex sub(Complex a, Complex b) {
        return new Complex(a.real - b.real, a.imag - b.imag);
    }

    // Method to multiply two complex numbers
    public static Complex mul(Complex a, Complex b) {
        double real = a.real * b.real - a.imag * b.imag;
        double imag = a.real * b.imag + a.imag * b.real;
        return new Complex(real, imag);
    }

    // Method to divide two complex numbers
    public static Complex div(Complex a, Complex b) {
        double divisor = b.real * b.real + b.imag * b.imag;
        double real = (a.real * b.real + a.imag * b.imag) / divisor;
        double imag = (a.imag * b.real - a.real * b.imag) / divisor;
        return new Complex(real, imag);
    }

    // Method to represent the complex number as a string
    @Override
    public String toString() {
        return "(" + real + " + " + imag + "i)";
    }
}
