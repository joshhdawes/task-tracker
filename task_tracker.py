"""
Simple command-line task tracking tool.

Base object is a Task.
Tasks contain other Tasks.
Tasks are performed by one or more people.
Everything is stored in an SQLite database file with tables task, person and task_person_pair.

Usage:

./task_tracker.py show task-tree - show a tree of tasks
./task_tracker.py show people - show the list of people

./task_tracker.py add task - add a new task, either under a projet or under a task
./task_tracker.py add person - add a new person
./task_tracker.py add person-to-task - associate a person with a task
./task_tracker.py edit task <label> - modify a task
./task_tracker.py edit person <label> - modify a person (name and associated tasks)
./task_tracker.py rm task - remove a task and all contained tasks
./task_tracker.py rm person - remove a person and all associations they have with tasks
./task_tracker.py rm person-from-task - disassociate a person from a task

"""

import sqlite3
import argparse
import sys
import traceback

db_name = "tasks.db"

def connect():
  """
  Connect to the tasks database file.
  """
  global db_name
  con = sqlite3.connect(db_name)
  return con

def query_with_results(string, args):
  """
  Execute a select query on the database.
  """
  con = connect()
  cursor = con.cursor()
  results = cursor.execute(string, args).fetchall()
  con.close()
  return results

def query_no_results(string, args):
  """
  Execute a select query on the database.
  """
  con = connect()
  cursor = con.cursor()
  cursor.execute(string, args)
  # if we expect no results, the query is either delete or update, so we need to commit
  con.commit()
  con.close()

def print_help():
  """
  Print help string.
  """
  print("Please given an action to perform, and then an object to perform it on.")
  print("Options are:")
  print("  ./task_tracker.py add task")
  print("  ./task_tracker.py add person")
  print("  ./task_tracker.py add person-to-task")
  print("  ./task_tracker.py edit task <label>")
  print("  ./task_tracker.py edit person <label>")
  print("  ./task_tracker.py rm task")
  print("  ./task_tracker.py rm person")
  print("  ./task_tracker.py rm person-from-task")

def accept_inputs(fields):
  """
  Based on a list of fields to fill, run inputs.
  Loop while the user has said they're not happy.
  """
  user_is_not_happy = True
  while user_is_not_happy:
    # store the response provisionally until we know the user wants to keep it
    provisional_response_dict = {}
    for field in fields:
      provisional_response_dict[field] = str(raw_input("%s: " % field))
    response = str(raw_input("Happy with this? y/n: "))
    if response == "y":
      user_is_not_happy = False
    else:
      # if this is the case, we go around again
      user_is_not_happy = True

  # return the provisional_response_dict
  return provisional_response_dict

def show_people():
  """
  List the people.
  """
  people = query_with_results("select * from person", [])
  for person in people:
    print("== %s ==" % person[1])
    # get this person's tasks
    tasks = query_with_results(
      "select task.label, task.description from (task inner join task_person_pair on task.label = task_person_pair.task) where task_person_pair.person = ?", [person[0]]
    )
    for task in tasks:
      print("---- [%s] %s" % (task[0], task[1]))

def show_tasks():
  """
  Show the tree of tasks - top level function
  """
  top_level_tasks = query_with_results("select label, description from task where parent = ''", [])
  for task in top_level_tasks:
    _show_task(task)

def _show_task(task, depth=0):
  """
  Show the tree of tasks - recursive part
  """
  indent = "  "*depth
  # get people associated with this task
  people = query_with_results("select person.name from (person inner join task_person_pair on person.id = task_person_pair.person) where task_person_pair.task = ?", [task[0]])
  people_string = ", ".join(map(lambda person : person[0], people)) if len(people) > 0 else "no one yet"
  # output this task line
  print("%s[%s] %s (%s)" % (indent, task[0], task[1], people_string))
  child_tasks = query_with_results("select label, description from task where parent = ?", [task[0]])
  for child_task in child_tasks:
    _show_task(child_task, depth+1)
  

def add_task():
  """
  Take the user through the procedure for adding a new task.
  """
  # get values from user
  responses = accept_inputs(["Task label", "Short task description", "Parent task label"])
  # insert into db
  query_no_results("insert into task values(?, ?, ?)",
    [responses["Task label"], responses["Short task description"], responses["Parent task label"]])
  print("New task created")

def add_person():
  """
  Take the user through the procedure for adding a new person.
  """
  # get values from user
  responses = accept_inputs(["Name"])
  # insert into db
  query_no_results("insert into person (name) values(?)", [responses["Name"]])
  print("New person created")

def add_person_to_task():
  """
  Take the user through the procedure for associating a person with a task.
  """
  # get values from user
  responses = accept_inputs(["Person", "Task label"])
  # get the person's ID
  id = query_with_results("select id from person where name = ?", [responses["Person"]])[0][0]
  # insert into db
  query_no_results("insert into task_person_pair (person, task) values(?, ?)", [id, responses["Task label"]])
  print("%s added to task %s" % (responses["Person"], responses["Task label"]))

def add_task_to_task():
  """
  Take the user through the procedure for adding a task to a new parent task.
  """
  # get task label from user
  responses = accept_inputs(["Task label"])
  child_label = responses["Task label"]
  # check for existence of task
  results = query_with_results("select * from task where label = ?", [child_label])
  if len(results) == 0:
    print("No task found with label '%s' that we could use." % child_label)
    return
  # get task label from user
  responses = accept_inputs(["New parent task label"])
  parent_label = responses["New parent task label"]
  # check for existence of task
  results = query_with_results("select * from task where label = ?", [parent_label])
  if len(results) == 0:
    print("No task found with label '%s' that we could use." % parent_label)
    return
  # update the task to remove the parent
  query_no_results("update task set parent = ? where label = ?", [parent_label, child_label])
  print("Set parent of task with label '%s' to task with label '%s'." % (child_label, parent_label))
  

def edit_task():
  """
  Take the user through the procedure for editing an existing task.
  """
  # get task label from user
  responses = accept_inputs(["Task label"])
  label = responses["Task label"]
  # check for existence of task
  results = query_with_results("select * from task where label = ?", [label])
  if len(results) == 0:
    print("No task found with label '%s'." % label)
    return
  # the task exists, so ask the user for the new description
  responses = accept_inputs(["New description"])
  # update db
  query_no_results("update task set description = ? where label = ?", [responses["New description"], label])
  print("Task with label '%s' updated." % label)

def edit_person():
  """
  Take the user through the procedure for editing an existing person.
  """
  # get person name from user
  responses = accept_inputs(["Person's name"])
  person_name = responses["Person's name"]
  # check for existence
  results = query_with_results("select * from person where name = ?", [person_name])
  if len(results) == 0:
    print("No person found with name '%s'." % person_name)
    return
  else:
    # get id of person
    id = query_with_results("select id from person where name = ?", [person_name])[0][0]
  # the task exists, so ask the user for the new description
  responses = accept_inputs(["New name"])
  # update db
  query_no_results("update person set name = ? where id = ?", [responses["New name"], id])
  print("Person with old name '%s' changed to '%s'." % (person_name, responses["New name"]))

def rm_task():
  """
  Take the user through the procedure for removing a task.
  """
  # get task label from user
  responses = accept_inputs(["Task label"])
  label = responses["Task label"]
  # check for existence of task
  results = query_with_results("select * from task where label = ?", [label])
  if len(results) == 0:
    print("No task found with label '%s' that we could remove." % label)
    return
  # the task exists, so remove it
  query_no_results("delete from task where label = ?", [label])  
  # remove all person associations
  query_no_results("delete from task_person_pair where task = ?", [label])
  print("Task with label '%s' removed." % label)

def rm_person():
  """
  Take the user through the procedure for removing a person.
  """
  # get person name from user
  responses = accept_inputs(["Person name"])
  person_name = responses["Person name"]
  # check for existence of person
  results = query_with_results("select id from person where name = ?", [person_name])
  if len(results) == 0:
    print("No person found with name '%s' that we could remove." % person_name)
    return
  # the person exists, so remove it
  query_no_results("delete from person where name = ?", [person_name])
  # remove all associations with tasks
  query_no_results("delete from task_person_pair where person = ?", [results[0][0]])
  print("Person with name '%s' removed." % person_name)

def rm_person_from_task():
  """
  Take the user through the procedure for removing a person from a task.
  """
  # get person name from user
  responses = accept_inputs(["Person name", "Task label"])
  person_name = responses["Person name"]
  task_label = responses["Task label"]
  # check for existence of person
  person_results = query_with_results("select id from person where name = ?", [person_name])
  if len(person_results) == 0:
    print("No person found with name '%s'." % person_name)
    return
  # check for the existence of task
  task_results = query_with_results("select * from task where label = ?", [task_label])
  if len(task_results) == 0:
    print("No task found with label '%s'." % task_label)
    return
  # disassociate the person from the task
  query_no_results("delete from task_person_pair where person = ? and task = ?", [person_results[0][0], task_label])
  print("Person '%s' removed from task with label '%s'." % (person_name, task_label))

def rm_task_from_parent():
  """
  Take the user through the procedure for removing a task from a parent task.
  """
  # get task label from user
  responses = accept_inputs(["Task label"])
  label = responses["Task label"]
  # check for existence of task
  results = query_with_results("select * from task where label = ?", [label])
  if len(results) == 0:
    print("No task found with label '%s' that we could remove." % label)
    return
  # update the task to remove the parent
  query_no_results("update task set parent = '' where label = ?", [label])
  print("Set parent of task with label '%s' to none." % label)

if __name__ == "__main__":
  try:
    # get the first argument, which will be the action to perform
    action = sys.argv[1]
    obj = sys.argv[2]
    if action == "add":
      if obj == "task":
        add_task()
      elif obj == "person":
        add_person()
      elif obj == "person-to-task":
        add_person_to_task()
      elif obj == "task-to-task":
        add_task_to_task()
    elif action == "edit":
      if obj == "task":
        edit_task()
      elif obj == "person":
        edit_person()
    elif action == "rm":
      if obj == "task":
        rm_task()
      elif obj == "person":
        rm_person()
      elif obj == "person-from-task":
        rm_person_from_task()
      elif obj == "task-from-parent":
        rm_task_from_parent()
    elif action == "show":
      if obj == "people":
        show_people()
      elif obj == "tasks":
        show_tasks()
    else:
      print_help()
  except:
    traceback.print_exc()
    print_help()
