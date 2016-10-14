CREATE TABLE pubmed_papers (
  id   TEXT PRIMARY KEY UNIQUE,
  pmid TEXT,
  title TEXT,
  abstract TEXT
);