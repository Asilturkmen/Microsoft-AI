# Operating Systems

An operating system manages hardware resources and provides services to applications. Its kernel schedules CPU time, manages memory, controls devices, and enforces protection boundaries between processes.

## Processes and threads

A process has its own address space and resources. Threads are execution paths within a process and normally share that process's memory. A context switch saves one execution state and restores another so the CPU can run multiple tasks over time.

## Virtual memory

Virtual memory gives each process a private logical address space. The operating system and hardware translate virtual addresses to physical memory pages. Pages that are not currently needed can be moved to secondary storage, although excessive paging reduces performance.
