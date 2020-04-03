## Simple task tracking for the command line in Python

`python task_tracker.py show tasks` - show a tree of tasks
`python task_tracker.py show people` - show the list of people

`python task_tracker.py add task` - add a new task, either under a projet or under a task
`python task_tracker.py add person` - add a new person
`python task_tracker.py add person-to-task` - associate a person with a task
`python task_tracker.py edit task` - modify a task
`python task_tracker.py edit person` - modify a person (name and associated tasks)
`python task_tracker.py rm task` - remove a task and all contained tasks
`python task_tracker.py rm person` - remove a person and all associations they have with tasks
`python task_tracker.py rm person-from-task` - disassociate a person from a task
