
public class Test3 {
    private int employeeId;
    private String employeeName;
    private float salary;

    public void createEmployee(int id, String name, float salary) {
        this.employeeId = id;
        this.employeeName = name;
        this.salary = salary;
    }

    public void giveBonus(float amount) {
        this.salary += amount;
    }

    public void deduct(float amount) {
        if (this.salary < amount) {
            System.out.println("Insufficient salary amount!");
        } else {
            this.salary -= amount;
        }
    }

    public void showSalary() {
        System.out.println("Current salary: " + this.salary);
    }

    @Override
    public String toString() {
        return "Test3{" + "employeeId=" + employeeId + ", employeeName=" + employeeName + ", salary=" + salary + '}';
    }
}
