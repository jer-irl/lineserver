# lineserver
Line server challenge to showcase my systems and design skills when coding with
a deadline for a job interview.  I don't have a huge amount of experience
building server applications so far, so my architecture might not reflect best
practices.  I'm eager to learn!

Run ./build.sh to run the two test suites (unit and system).  It may also show
warnings, because the server socket isn't properly torn down between test runs.
If I had more time, one thing I would do is to beef up the testing
architecture.  At the end of the tests, 4 and 8 tests should be successfully
run respectively.

Run `./run.sh [filename]` to start the server on port 8000.  Then,you can make
requests of the server using cURL, telnet, or any other tool that supports http
requests.

## Notes
- The cache and directory assume that files are ascii formatted.  This could be
  generalized in the future.
- The endpoint dispatching only considers the first element of the HTTP request
  path.  This isn't terrible, but could be generalized.
- The cache is protected by a coarse lock.  This is discussed below, but a more
  comprehensive caching mechanism could be explored in the future.
- The cache and directory could be implemented using the `linecache` module.  I
  didn't know it existed when I started, and I think the manual implementation
  better shows my skills.

## How it works
lineserver.py is a frontend that manages command-line input and initializes the
Server.  Actual implementation code is in lineserver/.

lineserver/server.py contains the Server code, which takes incoming requests and
dispatches to endpoint handlers, coded in lineserver/endpoints.py.  Endpoint
handlers are functions that take a single argument, the initial request handler,
and service the request.  There is one endpoint handler for each HTTP
method/endpoint combination.  Right now, only the first element of the request
path is considered in dispatching to handlers, but this could be generalized.

The Server owns a Cache, which is responsible for retrieving all text from the
text file.  The cache stores up to a specified number of bytes a gigabyte as
currently specified, making sure not to store more than that number.  An
advantage to the cache is that it operates by individual lines, which could be
variable length.  This puts a lot of faith in the Python garbage collector, and
could lead to memory fragmentation, but is space-efficient if random lines are
"hot" and receive a lot of requests.  It also has the advantage over fixed-size
cache units in that no half-lines are cached, which are semantically useless for
our application where entire lines are always required.  Cache eviction is done
with a simple "clock" algorithm, that keeps management of the cache constant
time (mostly).

The Cache also owns a Directory, which stores preprocessing information about
the file.  To bound memory, the Directory is initialized with a fixed max number
of records.  Records in the Directory are mappings from line number to offset
in the file.  These records may be sparse if memory is constrained (for the 100
GB case).  If the Cache needs to read in from file, it consults the Directory
for an offset close to the target line, leading to an approximately
constant-time complexity read in.  (Technically linear if the number of records
is constrained, but effectively constant.)

__NOTE:__
After coding this, I realized that there is a `linecache` Python module.  If
I were to redo this, I would probably use the pre-made module, but for the
submission I think it better shows my skills if I keep my manually coded cache
and directory.

## Build requirements
I am only using the Python standard library, but have only tested the server on
Python 3.7.

## Performance for large files
Large file performance is made faster by using the Directory and Cache, at the
cost of a one time two-pass preprocessing stage.  For repetitive access
patterns, the Cache will read from memory and perform quickly.  If access is
random, serving requests will be slower, but still almost logarithmic in the
size of the file.  This isn't quite true because there is a linear component to
lookups, but with a reasonable number of directory records, it is effectively
still logarithmic in the size of the file.  The directory is helpful enough that
OS paging and disk hardware start to play a role in the algorithmic analysis.

## Performance under user load
I'm trusting the `http.server` implementation here to do well.  It implements an
event loop that leads to multithreaded handling.  An unfortunate implementation
detail is that the cache is protected by a Big Fat Lock (BFL).  The BFL is
unfortunate, but I don't think the end of the world, because of CPython's Global
Interpreter Lock (GIL).  The BFL prevents multiple disk reads from happening
concurrently, which prevents nice OS batching of reads, but the GIL already
prevents concurrent execution of my code.  If I had more time to research, I'd
like to batch read requests and make locking finer-grained.

## Documentation referenced
I reference the Python standard library documentation extensively, but pulled
from previous experience in designing the APIs and caching and directory
structures.

## Third-party libraries and tools
Only the Python standard library was used.

## Time spent and possible improvements
Total, I'd estimate I spent around 6 hours on this project.  The bulk of time
was spent figuring out how to get the network connections to work, and realizing
that telnet wasn't the most appropriate tool for manual testing.

I chose Python because it's a nice language to prototype in, and also because it
came with the tools necessary for the job.  Were I given infinite time, I would
probably rewrite in C++, because I would get more control over the memory usage
and could do caching better.  I would also put more time into researching proper
REST API design principles and implementation.

## Self-critique
I tried to take a systems-level approach to i/o performance, but neglected the
load requirements until later on.  I think the single biggest area I could
improve on is load scalability, which might require a different programming
language, a different deployment, or other measures.
