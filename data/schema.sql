PRAGMA foreign_keys = ON;
CREATE TABLE employee (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('executive','manager','engineer','designer','analyst','intern')),
    salary INTEGER NOT NULL CHECK (salary >= 0), -- annual USD cents
    manager_id INTEGER REFERENCES employee(id),
    start_date TEXT NOT NULL CHECK (length(start_date) = 10 AND date(start_date) IS NOT NULL AND date(start_date) = start_date),
    CHECK (manager_id IS NULL OR manager_id != id)
);
CREATE INDEX employee_manager_idx ON employee(manager_id);

