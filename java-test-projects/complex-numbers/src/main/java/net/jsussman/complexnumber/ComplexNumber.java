package net.jsussman.complexnumber;

import net.jsussman.inheritance.Bicycle;

/**
 * @see blah
 */
public class ComplexNumber {
  // Fields for the real and imaginary parts
  private double real;
  private double imag;
  private double removeMe;
  private double changeMe;

  // Constructor
  public ComplexNumber(double real, double imag, double removeMe, double changeMe) {
    this.real = real;
    this.imag = imag;
    this.removeMe = removeMe;
    this.changeMe = changeMe;

    (x);
  }

  // Getter methods
  public double getReal() {
    // this.getClass();
    return real;
  }

  public double getImag() {
    Bicycle b = new Bicycle(0, 0);
    return imag;
  }

  public double getRemoveMe() {
    return removeMe;
  }

  // Method to add two complex numbers
  public static ComplexNumber add(ComplexNumber a, ComplexNumber b) {
    return new ComplexNumber(a.real + b.real, a.imag + b.imag, 0, 0);
  }

  // Method to subtract two complex numbers
  public static ComplexNumber sub(ComplexNumber a, ComplexNumber b) {
    return new ComplexNumber(a.real - b.real, a.imag - b.imag, 0, 0);
  }

  // Method to multiply two complex numbers
  public static ComplexNumber mul(ComplexNumber a, ComplexNumber b) {
    double real = a.real * b.real - a.imag * b.imag;
    double imag = a.real * b.imag + a.imag * b.real;
    return new ComplexNumber(real, imag, 0, 0);
  }

  // Method to divide two complex numbers
  public static ComplexNumber div(ComplexNumber a, ComplexNumber b) {
    double divisor = b.real * b.real + b.imag * b.imag;
    double real = (a.real * b.real + a.imag * b.imag) / divisor;
    double imag = (a.imag * b.real - a.real * b.imag) / divisor;
    return new ComplexNumber(real, imag, 0, 0);
  }

  // Method to represent the complex number as a string
  @Override
  public String toString() {
    return "" + real + " + " + imag + "i";
  }
}
