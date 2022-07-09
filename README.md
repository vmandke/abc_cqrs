
# ABC of CQRS (circa 2018)

### Running tests
###### make test

### Arch
I have modelled the given problem statement using a minmal CQRS solution (recently started reading about this). There is a writeside and a readside. Commands which modify the state are handled by writeside, and queries are handled by read side.

The is a runner process, a writeside registry, a readside registry all running in different processes. Interprocess communication is handled by Queues and Pipes.

I have tried to incorporate the Actor model, as I have understood it into this solution. Almost all of the classes are Actors, even the Registry class is one.

As this is a minimal actor model representation there is a slight delay while generating the outputs, as the communication, thought async internally, is blocked on output at the user's end. I assume that this delay is what causes the provided tests to fail, (due to time constrainst not fixing the provided tests)

### Possible improvement 
-- Registries might become hotspots
-- Python threads are inefficient due to GIL, taskless / greenlets can be explored
-- There is lot of error handling which was avoided to complete the solution in time.
