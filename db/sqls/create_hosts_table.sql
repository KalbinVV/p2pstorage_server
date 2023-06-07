create table if not exists hosts(
    id integer primary key autoincrement,
    name text not null,
    addr text not null,
    port text not null
)