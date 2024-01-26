package net.jsussman.complexnumber;

import net.jsussman.inheritance.MountainBike;

/**
 * @see blah
 */
public class ComplexNumber2 {
  // Fields for the real and imaginary parts
  private double real;
  private double imag;
  private int changeMe;

  // Constructor
  public ComplexNumber2(double real, double imag, int changeMe) {
    this.real = real;
    this.imag = imag;
    this.changeMe = changeMe;

    [x];
  }

  // Getter methods
  public double getReal() {
    // this.getClass();
    return real;
  }

  public double getImag() {
    return imag;
  }

  // Method to add two complex numbers
  public static ComplexNumber2 add(ComplexNumber2 a, ComplexNumber2 b) {
    return new ComplexNumber2(a.real + b.real, a.imag + b.imag);
  }

  // Method to subtract two complex numbers
  public static ComplexNumber2 sub(ComplexNumber2 a, ComplexNumber2 b) {
    return new ComplexNumber2(a.real - b.real, a.imag - b.imag);
  }

  // Method to multiply two complex numbers
  public static ComplexNumber2 mul(ComplexNumber2 a, ComplexNumber2 b) {
    double real = a.real * b.real - a.imag * b.imag;
    double imag = a.real * b.imag + a.imag * b.real;
    return new ComplexNumber2(real, imag);
  }

  // Method to divide two complex numbers
  public static ComplexNumber2 div(ComplexNumber2 a, ComplexNumber2 b) {
    double divisor = b.real * b.real + b.imag * b.imag;
    double real = (a.real * b.real + a.imag * b.imag) / divisor;
    double imag = (a.imag * b.real - a.real * b.imag) / divisor;
    return new ComplexNumber2(real, imag);
  }

  // Method to represent the complex number as a string
  @Override
  public String toString() {
    return "" + real + " + " + imag + "i";
  }
}
