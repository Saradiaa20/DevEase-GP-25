public class Test1 {
    private int studentId;
    private String name;
    private float gpa;

    public void register(int id, String n, float gpa){
        this.studentId = id;
        this.name = n;
        this.gpa = gpa;
    }

    public void updateGPA(float newGpa){
        if(newGpa < 0 || newGpa > 4){
            System.out.println("Invalid GPA");
        } else {
            this.gpa = newGpa;
        }
    }

    public void showInfo(){
        System.out.println("Student: " + name + ", GPA: " + gpa);
    }

    @Override
    public String toString() {
        return "Test1{" + "studentId=" + studentId + ", name=" + name + ", gpa=" + gpa + '}';
    }
}
