public class Test2 {

    public void doSomething(int x){
        int y=0,z=1;
        for(int i=0;i<10;i++){
            if(i%x==0){
                y=y+z;
            }else{
                y=y+i*3+7; // magic numbers everywhere
            }
        }

        System.out.println("Result is: "+y);

        // pointless unused variables
        String a = "hello";
        int b = 55;
        double d = 3.14159;

        if(x>5)
            System.out.println("ok");
        else
            System.out.println("not ok"); // duplicated logic with no reason
    }
}
