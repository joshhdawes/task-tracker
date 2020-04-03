create table task (
label text not null primary key,
description text not null,
parent text not null,
foreign key (parent) references task(label)
);

create table person (
id integer not null primary key autoincrement,
name text not null
);

create table task_person_pair (
person integer not null,
task text not null,
foreign key (person) references person(id),
foreign key (task) references task(label)
);
