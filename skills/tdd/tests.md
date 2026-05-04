# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```csharp
// GOOD: Tests observable behavior
[Fact]
public async Task UserCanCheckoutWithValidCart()
{
    var cart = new Cart();
    cart.Add(product);
    var result = await checkout.Execute(cart, paymentMethod);
    Assert.Equal("confirmed", result.Status);
}
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```csharp
// BAD: Tests implementation details
[Fact]
public async Task CheckoutCallsPaymentServiceProcess()
{
    var mockPayment = Substitute.For<IPaymentService>();
    await checkout.Execute(cart, payment);
    await mockPayment.Received().Process(cart.Total);
}
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```csharp
// BAD: Bypasses interface to verify
[Fact]
public async Task CreateUserSavesToDatabase()
{
    await userService.Create(new CreateUserRequest { Name = "Alice" });
    var row = await db.QuerySingleOrDefaultAsync(
        "SELECT * FROM users WHERE name = @name", new { name = "Alice" });
    Assert.NotNull(row);
}

// GOOD: Verifies through interface
[Fact]
public async Task CreateUserMakesUserRetrievable()
{
    var user = await userService.Create(new CreateUserRequest { Name = "Alice" });
    var retrieved = await userService.GetById(user.Id);
    Assert.Equal("Alice", retrieved.Name);
}
```
