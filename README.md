## Simple task tracking for the command line in Python

The base object is the `task`, of which a `person` can be a part.

Each `task` has a uniquely-identifying `label` and a not-necessarily-unique `description`.

Each `task` can have a parent task which can be changed or removed (in which case it becomes top-level).

Relationships between tasks and people are based on tasks' labels.

You can use the commands below to construct, manipulate and display your tasks and the list of people who work on them.

### Commands

Show a tree of tasks

```python task_tracker.py show tasks```

Show the list of people

```python task_tracker.py show people```

Adding objects...

```python task_tracker.py add task```

```python task_tracker.py add person```

```python task_tracker.py add person-to-task```

```python task_tracker.py add task-to-task```

Editing objects...

```python task_tracker.py edit task```

```python task_tracker.py edit person```

Removing objects...

```python task_tracker.py rm task```

```python task_tracker.py rm person```

```python task_tracker.py rm person-from-task```

```python task_tracker.py rm task-from-parent```
