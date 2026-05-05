# Frontend TDD with Blazor + bUnit

## Setup

```xml
<!-- Add to test project -->
<PackageReference Include="bunit" Version="*" />
```

```csharp
// Inherit from TestContext or use it directly
public class MyComponentTests : TestContext { }
```

## What to Test in Components

Focus on **observable behavior** — what the user sees and can do:

- Text rendered to the page
- Elements appearing/disappearing based on state
- User interactions (clicks, form input, keyboard)
- EventCallback outputs (what gets emitted when user acts)
- Navigation triggered by user actions

Do **not** test:
- Specific HTML structure or tag nesting
- CSS class names (implementation detail)
- Child component internals (test the child separately)
- How state is stored internally (use public parameters/interface)
- Render counts or lifecycle calls

## Good vs. Bad Component Tests

```csharp
// GOOD: Tests what the user sees
[Fact]
public void ShowsValidationErrorWhenEmailIsEmpty()
{
    var cut = RenderComponent<LoginForm>();
    cut.Find("button[type=submit]").Click();
    Assert.Contains("Email is required", cut.Markup);
}

// BAD: Tests markup structure (breaks on any HTML change)
[Fact]
public void RendersEmailErrorInSpan()
{
    var cut = RenderComponent<LoginForm>();
    cut.Find("button[type=submit]").Click();
    cut.Find("div.field > span.validation-message").MarkupMatches(
        "<span class=\"validation-message\">Email is required</span>");
}
```

```csharp
// GOOD: Tests user interaction outcome
[Fact]
public void SubmittingValidFormCallsOnSubmitCallback()
{
    var submitted = false;
    var cut = RenderComponent<LoginForm>(p => p
        .Add(x => x.OnSubmit, () => submitted = true));

    cut.Find("input[name=email]").Change("user@example.com");
    cut.Find("button[type=submit]").Click();

    Assert.True(submitted);
}

// BAD: Tests internal component state field
[Fact]
public void SubmitSetsIsLoadingToTrue()
{
    var cut = RenderComponent<LoginForm>();
    cut.Find("button[type=submit]").Click();
    // Accessing private field — breaks on any refactor
    Assert.True(cut.Instance._isLoading);
}
```

## Mocking Injected Services

Use `Services.AddSingleton` (or `AddMockHttpClient`) to swap real services:

```csharp
[Fact]
public async Task DisplaysUserNameAfterLoad()
{
    var fakeUserService = Substitute.For<IUserService>();
    fakeUserService.GetCurrentAsync().Returns(new User { Name = "Alice" });

    Services.AddSingleton(fakeUserService);

    var cut = RenderComponent<UserProfile>();
    await cut.WaitForStateAsync(() => cut.Markup.Contains("Alice"));

    Assert.Contains("Alice", cut.Markup);
}
```

Only mock at system boundaries — external services, HTTP clients, time. Do not mock your own services unless they involve real I/O.

## Testing Async / Loading States

```csharp
[Fact]
public async Task ShowsLoadingThenContent()
{
    var tcs = new TaskCompletionSource<IEnumerable<Product>>();
    var fakeService = Substitute.For<IProductService>();
    fakeService.GetAllAsync().Returns(tcs.Task);

    Services.AddSingleton(fakeService);
    var cut = RenderComponent<ProductList>();

    // Loading state visible before data arrives
    Assert.Contains("Loading", cut.Markup);

    // Complete the task
    tcs.SetResult([new Product { Name = "Widget" }]);
    await cut.WaitForStateAsync(() => cut.Markup.Contains("Widget"));

    Assert.Contains("Widget", cut.Markup);
    Assert.DoesNotContain("Loading", cut.Markup);
}
```

## EventCallback Testing

```csharp
[Fact]
public void DeleteButtonEmitsOnDeleteWithCorrectId()
{
    int? deletedId = null;
    var cut = RenderComponent<ProductRow>(p => p
        .Add(x => x.Product, new Product { Id = 42, Name = "Widget" })
        .Add(x => x.OnDelete, (int id) => deletedId = id));

    cut.Find("button.delete").Click();

    Assert.Equal(42, deletedId);
}
```

## Form Input Patterns

```csharp
[Fact]
public void FormSubmitsWithEnteredValues()
{
    CreateUserRequest? submitted = null;
    var cut = RenderComponent<CreateUserForm>(p => p
        .Add(x => x.OnSubmit, (CreateUserRequest req) => submitted = req));

    cut.Find("input[name=name]").Change("Alice");
    cut.Find("input[name=email]").Change("alice@example.com");
    cut.Find("button[type=submit]").Click();

    Assert.NotNull(submitted);
    Assert.Equal("Alice", submitted!.Name);
    Assert.Equal("alice@example.com", submitted.Email);
}
```

## Component TDD Loop

The red-green-refactor loop applies to components exactly like services:

```
RED:   Write test for one piece of UI behavior → test fails (component may not exist yet)
GREEN: Add minimal markup/code to pass → test passes
       Repeat for next behavior
REFACTOR: Extract child components, clean up markup, deepen logic
```

Start with the tracer bullet: render the component and assert it mounts without error, then layer in behavior tests one at a time.

## When to Use bUnit vs. Integration Tests

| Scenario | Approach |
|---|---|
| Component renders correctly | bUnit |
| User interactions (click, type) | bUnit |
| EventCallback outputs | bUnit |
| Multiple components wired together | bUnit with real child components |
| Full page with routing + auth | Integration test (WebApplicationFactory) |
| API endpoints returning correct data | Integration test (WebApplicationFactory) |
