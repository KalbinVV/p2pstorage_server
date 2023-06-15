create table owners(
    id integer primary key autoincrement,
    file_id integer not null,
    host_id integer not null,
    foreign key(host_id) references hosts(id) on delete cascade,
    foreign key(file_id) references files(id) on delete cascade
)