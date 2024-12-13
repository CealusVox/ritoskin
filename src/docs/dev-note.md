Structure project for multithreading

- champion level: multiple champion folders to process
- skin level: within each champion folder, there are multiple skin files to process
- combine both ideas (complex in resource management)
- add loggin and output for each operation
- cond for two threads not access same file ---- RACE CONDITION
- protect shared data structures (mutex, locks, etcd)
- limit max threads (cpu bottleneck)

kkkmmmm::mmm

thread safety: 
- shared ress (bin unhasher, files stream, DS operations) - thread  safe??


BUnh - read operation after init and drop state after process? - thread safe
if not ts, create separate instances for each thread -> would avoid shared state issues

CH level - could solve the problem by creating separate instances for each thread
!! - could lead to conflict when dealing with related folderss (delete folders before processing)
Sk level - process sequentially using threads in champion skin folder
!! - solve the conflict.. -> file is independent and safe in its own thread? :we

Both - fastest approach but complex in resource management
!! - ?? abort it

Skin level:
-> process indep and each state is no shared (process_binfile should handle - check?
-> better control over the num of threads)
-> solve problemw ith related folders (delete folders before processing)
-? scalable zz
-- single champ has many skins that num of thread?  - 1 thread per skin?? unmanageable

- thread pool !! - limit the num of threads
- batch process - skins in batches (make sure it is processed in parallel)

impl;
process each champion folder sequentially, and allow for some parallelism accross
thread pool limit num of concurrent threads
isolate skin file
manage res 
filesys operation

make sure BUnh is only read data and don't change state

sync console output - mutex cons, local buffers

- Clean up temp files - delete after processing to prevent clutter
- Create log events in dif files


Consider low end cpu - limt the num of threads using hardware_conc() from c++17 (skip it now)