#### Nodes
CREATE TABLE Nodes(id INTEGER PRIMARY KEY, lat REAL, lon REAL, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp DATETIME);

#### nodesTags
CREATE TABLE nodesTags(id INTEGER, key TEXT, value TEXT, type TEXT, FOREIGN KEY (id) REFERENCES Nodes (id));

#### Ways
CREATE TABLE Ways(id INTEGER PRIMARY KEY, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp DATETIME);

#### waysNodes
CREATE TABLE waysNodes(id INTEGER, node_id INTEGER, position INTEGER, FOREIGN KEY(id) REFERENCES Nodes(id));

#### waysTags
CREATE TABLE waysTags(id INTEGER, key TEXT, value TEXT, type TEXT, FOREIGN KEY(id) REFERENCES Ways(id));
