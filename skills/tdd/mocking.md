# When to Mock

Mock at **system boundaries** only:

- External APIs (payment, email, etc.)
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Don't mock:

- Your own classes/modules
- Internal collaborators
- Anything you control

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```csharp
// Easy to mock
public decimal ProcessPayment(Order order, IPaymentClient paymentClient)
{
    return paymentClient.Charge(order.Total);
}

// Hard to mock
public decimal ProcessPayment(Order order)
{
    var client = new StripeClient(Environment.GetEnvironmentVariable("STRIPE_KEY"));
    return client.Charge(order.Total);
}
```

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific methods for each external operation instead of one generic method with conditional logic:

```csharp
// GOOD: Each method is independently mockable
public interface IApiClient
{
    Task<User> GetUser(int id);
    Task<IEnumerable<Order>> GetOrders(int userId);
    Task<Order> CreateOrder(CreateOrderRequest data);
}

// BAD: Mocking requires conditional logic inside the mock
public interface IApiClient
{
    Task<HttpResponseMessage> Fetch(string endpoint, HttpMethod? method = null, object? body = null);
}
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Type safety per endpoint
