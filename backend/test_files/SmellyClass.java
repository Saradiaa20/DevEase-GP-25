public class SmellyClass {

    public int badMethod(int a, int b, int c, int d, int e, int f) {
        return a + b + c + d + e + f;
    }

    public void printStuff() {
        System.out.println("Hello"); // bad practice
    }

    public void longMethod() {
        int x = 0;
        for(int i=0;i<100;i++){
            for(int j=0;j<100;j++){
                for(int k=0;k<100;k++){
                    x++;
                }
            }
        }
    }
}