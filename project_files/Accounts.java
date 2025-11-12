// // Edited by QualiCode System
 package javaapplication1;

public class Accounts {
    private int accountNumber;
    private String name;
    private float amount;
    
    public void insert(int a, String n, float amt){
        this.accountNumber = a;
        this.name = n;
        this.amount = amt;
    }
    
//     public void deposit(float amt){
//         this.amount = this.amount + amt;
//     }
    
//     public void withDraw(float amt){
//         if(this.amount < amt){
//             System.out.println("Can't proceed");
//         }
//         else{
//             this.amount = this.amount - amt;
//         }
//     }
    
//     public void checkBalance(){
//         System.out.println("Your balance is: " + this.amount);
//     }

//     @Override
//     public String toString() {
//         return "Accounts{" + "accountNumber=" + accountNumber + ", name=" + name + ", amount=" + amount + '}';
//     }
    
}
