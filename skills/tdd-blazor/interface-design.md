# Interface Design for Testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them**

   ```csharp
   // Testable
   public decimal ProcessOrder(Order order, IPaymentGateway paymentGateway) { ... }

   // Hard to test
   public decimal ProcessOrder(Order order)
   {
       var gateway = new StripeGateway();
       ...
   }
   ```

2. **Return results, don't produce side effects**

   ```csharp
   // Testable
   public Discount CalculateDiscount(Cart cart) { ... }

   // Hard to test
   public void ApplyDiscount(Cart cart)
   {
       cart.Total -= discount;
   }
   ```

3. **Small surface area**
   - Fewer methods = fewer tests needed
   - Fewer params = simpler test setup
