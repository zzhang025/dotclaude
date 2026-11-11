# UI Prototype

Generate **several radically different UI variations** on a single Blazor route, switchable from a floating bottom bar. The user flips between variants in the browser, picks one (or steals bits from each), then throws the rest away.

If the question is about logic/state rather than what something looks like — wrong branch. Use [LOGIC.md](LOGIC.md).

## When this is the right shape

- "What should this page look like?"
- "I want to see a few options for this dashboard before committing."
- "Try a different layout for the settings screen."
- Any time the user would otherwise spend a day picking between three vague mockups in their head.

## Two sub-shapes — strongly prefer sub-shape A

A UI prototype is much easier to judge when it's **butting up against the rest of the app** — real header, real sidebar, real data, real density. A throwaway route on its own is a vacuum: every variant looks fine in isolation. Default to sub-shape A whenever there's a plausible existing page to host the variants. Only reach for sub-shape B if the prototype genuinely has no nearby home.

### Sub-shape A — adjustment to an existing page (preferred)

The route already exists. Variants are rendered **on the same route**, gated by a `?variant=` URL query parameter. The existing data fetching, parameters, and auth all stay — only the rendering swaps. This is the default; pick it unless there's a specific reason not to.

If the prototype is for something that doesn't yet have a page but *would naturally live inside one* (a new section of the dashboard, a new card on the settings screen, a new step in an existing flow) — that's still sub-shape A. Mount the variants inside the host page.

### Sub-shape B — a new page (last resort)

Only use this when the thing being prototyped genuinely has no existing page to live inside — e.g. an entirely new top-level surface, or a flow that can't be embedded anywhere sensible.

Create a **throwaway Blazor page** following the project's existing routing convention. Name it so it's obviously a prototype (e.g. `@page "/prototype/name"`). Same `?variant=` pattern.

Before committing to sub-shape B, sanity-check: is there really no existing page this could be embedded in? An empty route hides design problems that a populated one would expose.

In both sub-shapes the floating bottom bar is identical.

## Process

### 1. State the question and pick N

Default to **3 variants**. More than 5 stops being radically different and starts being noise — cap there.

Write down the plan in one line, in the prototype's location or a top-of-file comment:

> "Three variants of the settings page, switchable via `?variant=`, on the existing `/settings` route."

### 2. Generate radically different variants

Draft each variant as a separate Blazor component (`VariantA.razor`, `VariantB.razor`, `VariantC.razor`). Hold each one to:

- The page's purpose and the data it has access to (injected services, cascading parameters).
- The project's existing CSS/component library (MudBlazor, Radzen, Bootstrap, plain CSS, Tailwind via CDN).
- A clear component name, e.g. `VariantA`, `VariantB`, `VariantC`.

Variants must be **structurally different** — different layout, different information hierarchy, different primary affordance, not just different colours. Three slightly-tweaked card grids isn't a UI prototype, it's wallpaper. If two drafts come out too similar, redo one with explicit "do not use a card grid" guidance.

### 3. Wire them together

In the host page (or new throwaway page), read the `?variant=` query parameter and render the matching component:

```razor
@page "/existing-route"
@inject NavigationManager Nav

@{
    var variant = QueryParam("variant") ?? "A";
}

@if (variant == "A") { <VariantA /> }
@if (variant == "B") { <VariantB /> }
@if (variant == "C") { <VariantC /> }

<PrototypeSwitcher Variants="@(new[]{"A","B","C"})" Current="@variant" />

@code {
    string QueryParam(string key)
    {
        var uri = new Uri(Nav.Uri);
        var query = System.Web.HttpUtility.ParseQueryString(uri.Query);
        return query[key];
    }
}
```

For sub-shape A (existing page): keep all existing `@inject` dependencies and `OnInitializedAsync` logic above the switcher; only the rendered subtree changes per variant.

For sub-shape B (new page): the throwaway page under `/prototype/<name>` mounts the same switcher.

### 4. Build the floating switcher

Create a `PrototypeSwitcher.razor` component — a small fixed-position bar at the bottom-centre of the screen with three pieces:

- **Left arrow** — cycles to the previous variant (wraps around).
- **Variant label** — shows the current variant key and, optionally, a name.
- **Right arrow** — cycles forward (wraps around).

Behaviour:

- Clicking an arrow calls `NavigationManager.NavigateTo` with an updated `?variant=` query string so the variant is shareable and reload-stable.
- Keyboard: `←` and `→` arrow keys cycle via `@onkeydown` on a focusable wrapper or JS interop. Don't intercept arrow keys when an `<input>` or `<textarea>` is focused.
- Visually distinct from the page (high-contrast pill, subtle shadow) so it's obviously not part of the design being evaluated.
- **Only rendered in Development** — gate on injected `IWebHostEnvironment`:

```razor
@inject IWebHostEnvironment Env

@if (Env.IsDevelopment())
{
    <div class="prototype-switcher">...</div>
}
```

Put the switcher in a shared location (e.g. `Shared/PrototypeSwitcher.razor`) so both sub-shapes can reuse it.

### 5. Hand it over

Surface the URL and the `?variant=` keys. The user will flip through whenever they get to it. The interesting feedback is usually **"I want the header from B with the sidebar from C"** — that's the actual design they want.

### 6. Capture the answer and clean up

Once a variant has won, write down which one and why (commit message, ADR, issue, or a `NOTES.md` next to the prototype). Then:

- **Sub-shape A** — delete the losing `VariantX.razor` files and the `PrototypeSwitcher`; fold the winner's markup into the existing page.
- **Sub-shape B** — promote the winning variant's markup to a real page, delete the throwaway route and the switcher component.

Don't leave variant components or the switcher lying around. They rot fast and confuse the next reader.

## Anti-patterns

- **Variants that differ only in colour or copy.** That's a tweak, not a prototype. Real variants disagree about structure.
- **Sharing too much markup between variants.** A shared header component is fine; a shared layout defeats the point. Each variant should be free to throw out the layout.
- **Wiring variants to real mutations.** Read-only prototypes are fine. If a variant needs to write data, point it at a stub service — the question is "what should this look like", not "does the backend work".
- **Promoting the prototype directly to production.** The variant code was written under prototype constraints (no tests, minimal error handling). Rewrite it properly when you fold it in.
