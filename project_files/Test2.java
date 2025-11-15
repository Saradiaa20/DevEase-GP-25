public class Test2 {
    private int productId;
    private String productName;
    private int quantity;

    public void addProduct(int id, String name, int qty){
        this.productId = id;
        this.productName = name;
        this.quantity = qty;
    }

    public void increaseStock(int qty){
        this.quantity += qty;
    }

    public void decreaseStock(int qty){
        if(this.quantity < qty){
            System.out.println("Not enough stock!");
        } else {
            this.quantity -= qty;
        }
    }

    public void checkStock(){
        System.out.println("Current stock: " + this.quantity);
    }

    @Override
    public String toString() {
        return "Test2{" + "productId=" + productId + ", productName=" + productName + ", quantity=" + quantity + '}';
    }
}
