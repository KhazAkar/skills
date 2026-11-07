# TigerStyle — source snapshot

Source: https://tigerstyle.dev (TigerBeetle). Fetched 2026-11-07 and
converted to Markdown: wording preserved, layout normalized, page
visuals reduced to the examples that carry meaning. This snapshot
backs the distillation in [SKILL.md](../SKILL.md); where the two
disagree, the distilled skill text wins for Damian's repos.

> The software engineering methodology developed by TigerBeetle to
> produce safer, faster software in less time.
>
> Do the hard thing today to make tomorrow easy.

## Values, in order

1. Safety
2. Performance
3. Experience

## Safety

Correctness is necessary but not sufficient for safety. To be safe, a
program must not only run correctly. It must apply defense-in-depth
and verify itself while running, to run correctly or else shut down
if it detects that it has violated expectations.

### NASA's Power Of Ten Rules

TigerStyle follows the spirit of NASA's Power of Ten Rules for
Safety-Critical Code by Gerard J. Holzmann. For example, static
allocation, assertions and explicit limits.

> "The rules act like the seat-belt in your car: initially they are
> perhaps a little uncomfortable, but after a while their use becomes
> second-nature and not using them becomes unimaginable."
>
> — Gerard J. Holzmann

### Explicit Limits

Put a limit on everything because everything has a limit. Bound all
resources, concurrency, and execution. Don't react to stimuli but use
fixed intervals to schedule work. Avoid recursion. Bound loops and
queues to detect infinite loops and latency spikes. Use fixed types
like `u32`. Avoid architecture-specific types like `usize`.

### Static Memory Allocation

Allocate all memory at startup. Don't allocate after initialization.
This centralizes and simplifies resource management, solves
fragmentation, forces you to think through "the physics of the
system", and leads to an elegant design, with efficient, predictable
performance.

### Assertions

Where types check structure, assertions check all logic and state, to
detect programmer error, multiply fuzzing, and downgrade catastrophe.
Assert arguments, returns, and invariants: what you expect and don't
expect, the positive and negative space, not only contract but breach.

### Logical Interfaces

The safety (as well as performance and experience) of a system is
dominated by the quality of its interfaces.

- Minimize surface area
- Define fault models
- Abstract physical non-deterministic interfaces with logical
  deterministic interfaces
- Push control flow up and data flow down

### Dimensionality

Simplify function signatures to minimize branches at the call site,
which are viral through the call graph. As a return type, `bool`
trumps `u64` trumps `!u64`. Minimize or define variables near to
when/where they are used, to close semantic gaps in time/space.

### Zero Dependencies

Dependencies risk safety and performance, invite supply chain attacks,
and increase install times. For infrastructure in particular, these
costs multiply up the stack. Similarly, tools have costs. A small
standard toolbox feels slow for you at first but accelerates the team
long term.

### Zero Technical Debt

Code, like steel, is easier to change while it's hot. Do it right the
first time, the best you know how, because you may not get another
chance, and because quality builds momentum. This is the only way to
make steady progress, knowing that the foundations are solid.

## Performance

The lack of back-of-the-envelope sketches is the root of all evil.
Think about performance from the outset. The time to solve
performance, and get the 1000x wins, is in the design phase, when you
can't profile. It's hard to fix a system after implementation, and
the gains are less. Have mechanical sympathy. Like a carpenter, work
with the grain.

### Primary Colors

Like a painter, perform back-of-the-envelope performance sketches with
respect to the four primary colors (network, storage, memory,
compute) and their two textures (bandwidth, latency) to be "roughly
right" and land within 90% of the global maxima.

### Control Plane / Data Plane

Separate the control plane from the data plane by batching. Use bigger
buffers to amortize network, storage, memory and compute costs, and to
enable assertions in the control plane without trading performance in
the data plane. Let the CPU sprint through large units of work.

### Make the Roads Bigger

Think of the future, where things are going. Use bigger block sizes to
amortize fixed costs, to minimize control plane overhead, and to place
fewer demands on hardware for performance. Embrace concurrency.

### Zero Copy / Deserialization

Per core memory bandwidth is a new bottleneck:

- Do things in the most direct way possible
- Don't copy memory in the data plane
- Don't thrash the CPU cache
- Don't serialize or deserialize data
- Use fixed-size cache line aligned structs
- Align structs to their largest field

## Experience

Together, we serve the users. A day of design is worth weeks or months
in production. Therefore, go slow to go fast. Optimize the total cost
of software ownership, not for those who write it once, but for those
who read and run it many times. Trade linear deadlines for exponential
quality.

### Simplicity And Elegance

> "...simple and elegant systems tend to be easier and faster to
> design and get right, more efficient in execution, and much more
> reliable, [but] require hard work and discipline to achieve..."
>
> — Edsger Dijkstra

### Nouns And Verbs

Great names are the essence of great code, capturing what a thing is or
does, for a crisp mental model.

- Append qualifiers to names
- Sort by most significant word (big endian naming)
- Use the same number of characters for related names (e.g.
  source/target) so they line up in the source
- Use `snake_case`
- Don't abbreviate

Naming example from the page:

```
Little Endian Naming                Big Endian Naming
min_connection_delay                connection_delay_ms_min
max_connection_delay                connection_delay_ms_max
max_connections                     connection_count_max
```

### Biodigital Jazz

> Software is engineering, and more, it is art. Information and
> inspiration. Reason and experience. Precision and poetry. Just like
> music. A tight beat. A rare groove. Words that rhyme and rhymes that
> break. If you believe in the songs, take them on tour. Making is
> showbiz.

> If you want to be remembered, be remarkable.
