package net.jsussman.inheritance;

public class Bicycle {
  // the Bicycle class has two fields
  public int gear;
  public int speed;

  // the Bicycle class has one constructor
  public Bicycle(int gear, int speed)
  {
    this.gear = gear;
    this.speed = speed;
  }

  // the Bicycle class has three methods
  public void applyBrake(int decrement)
  {
    speed -= decrement;
  }

  public void speedUp(int increment)
  {
    speed += increment;
  }

  public void callMethod() {
    speedUp(1);
  }

  // toString() method to print info of Bicycle
  public String toString()
  {
    return ("No of gears are " + gear + "\n"
        + "speed of bicycle is " + speed);
  }
}
