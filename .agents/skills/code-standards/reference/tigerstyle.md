# TigerStyle — rationale digest

Paraphrased digest of https://tigerstyle.dev, the methodology published
by TigerBeetle, compiled 2026-11-07 for review-time and ADR-time
reference. This file carries our wording, not the source's; short
quotes are attributed. Read the site for the original prose. The
distilled rules in [SKILL.md](../SKILL.md) win over both.

Their tagline, quoted: "Do the hard thing today to make tomorrow
easy."

## Values, in order

Safety first, performance second, the experience of readers and
operators third. The ordering is deliberate: safety is never traded
away for speed or polish.

## Safety

Correct code can still be unsafe. TigerStyle asks a program to check
itself while it runs: layered defenses, runtime verification of
expectations, and a preference for shutting down over continuing in a
known-bad state. TigerStyle explicitly follows the spirit of NASA's
Power of Ten (Holzmann); static allocation, assertions, and explicit
limits are its three visible habits.

- **Explicit limits.** Everything finite gets a number: bounded
  resources, bounded concurrency, bounded execution. Work is
  scheduled at fixed intervals instead of reacting to stimuli,
  recursion is avoided, and loops and queues are capped so runaway
  code and latency spikes surface immediately. Fixed-width types
  (`u32`) are preferred over architecture-dependent ones (`usize`)
  so a limit means the same thing everywhere.
- **Static memory allocation.** Reserve memory at startup, never
  allocate afterwards. This centralizes resource management, removes
  fragmentation, forces early clarity about the system's real
  resource needs, and yields predictable performance.
- **Assertions.** Types check structure; assertions check logic and
  state. Assert arguments, returns, and invariants, on both the
  expected side and the must-never-happen side. The payoff: programmer
  error surfaces at the fault instead of downstream, and fuzzing is
  multiplied because every assertion is a tripwire.
- **Logical interfaces.** System quality tracks interface quality.
  Keep the surface small, state what can fail and how, wrap
  non-deterministic (physical, concurrent) things behind
  deterministic logical interfaces, push control flow up and data flow
  down.
- **Dimensionality.** Fewer parameters mean fewer branches at call
  sites, and call-site branches spread through the whole call graph.
  Prefer the simplest honest return type (a bool over a count, a
  count over a nullable count) and define variables close to their
  use, to close the gap in time and space between a name and its
  meaning.
- **Zero dependencies.** Each dependency carries safety and
  performance risk, supply-chain exposure, and install-time cost, and
  those costs compound in infrastructure. The same logic applies to
  tools: a small standard toolbox feels slow at first and pays off
  later.
- **Zero technical debt.** Change is cheapest while the code is still
  hot, so do it right the first time, the best you know how. Solid
  foundations are what make steady progress possible.

## Performance

The root failure is skipping the back-of-envelope sketch. The big
wins come at design time, before anything can be profiled;
retrofitting performance onto a built system is harder and gains
less. Have mechanical sympathy: work with the grain of the hardware,
like a carpenter with wood.

- **Primary colors.** Sketch any hot path against four resources
  (network, storage, memory, compute) and two textures (bandwidth,
  latency). Rough numbers land within striking distance of the global
  optimum; precision can wait.
- **Control plane / data plane.** Separate the two with batching:
  bigger buffers amortize per-operation costs, assertions live in
  the control plane without slowing the data plane, and the CPU
  sprints through large units of work.
- **Bigger blocks.** Think about where hardware is going. Larger block
  sizes amortize fixed costs and cut control-plane overhead per byte;
  embrace concurrency rather than fear it.
- **Zero copy.** Per-core memory bandwidth is the modern bottleneck:
  take the most direct path, do not copy in the data plane, do not
  thrash the cache, do not serialize/deserialize, and lay out
  fixed-size structs on cache-line boundaries aligned to their
  largest field.

## Experience

Serve the people who read and run the code, not the one who writes it
once. A day of design saves weeks of production firefighting, so go
slow to go fast; optimize total cost of ownership and trade linear
deadlines for exponential quality.

- **Simplicity and elegance.** In Dijkstra's words, simple and elegant
  systems are easier to get right, more efficient to run, and much
  more reliable — at the price of hard work and discipline.
- **Nouns and verbs.** Names carry the mental model: name things for
  what they are or do, order words most-significant first so related
  names sort together, keep paired names the same length, use
  snake_case, and do not abbreviate.
- **The art of it.** TigerStyle closes by acknowledging that
  engineering is also craft: reason and experience, precision and
  poetry. Their parting line, quoted: "If you want to be remembered,
  be remarkable."
