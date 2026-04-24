:begin
CREATE CONSTRAINT UNIQUE_IMPORT_NAME FOR (node:`UNIQUE IMPORT LABEL`) REQUIRE (node.`UNIQUE IMPORT ID`) IS UNIQUE;
:commit
CALL db.awaitIndexes(300);
:begin
UNWIND [{_id:55, properties:{id:"node_15"}}, {_id:64, properties:{id:"node_24"}}, {_id:74, properties:{id:"node_34"}}, {_id:81, properties:{id:"node_41"}}, {_id:83, properties:{id:"node_43"}}, {_id:131, properties:{id:"node_1"}}, {_id:136, properties:{id:"node_6"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N1;
UNWIND [{_id:59, properties:{x:23, id:"node_19"}}, {_id:70, properties:{x:93, id:"node_30"}}, {_id:72, properties:{x:74, id:"node_32"}}, {_id:75, properties:{x:71, id:"node_35"}}, {_id:79, properties:{x:58, id:"node_39"}}, {_id:80, properties:{x:76, id:"node_40"}}, {_id:82, properties:{x:44, id:"node_42"}}, {_id:85, properties:{x:59, id:"node_45"}}, {_id:86, properties:{x:62, id:"node_46"}}, {_id:130, properties:{x:44, id:"node_0"}}, {_id:132, properties:{x:78, id:"node_2"}}, {_id:135, properties:{x:95, id:"node_5"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N5;
UNWIND [{_id:60, properties:{id:"node_20"}}, {_id:61, properties:{id:"node_21"}}, {_id:62, properties:{id:"node_22"}}, {_id:63, properties:{id:"node_23"}}, {_id:66, properties:{id:"node_26"}}, {_id:67, properties:{id:"node_27"}}, {_id:71, properties:{id:"node_31"}}, {_id:73, properties:{id:"node_33"}}, {_id:76, properties:{id:"node_36"}}, {_id:138, properties:{id:"node_8"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N4;
UNWIND [{_id:50, properties:{id:"node_10"}}, {_id:51, properties:{id:"node_11"}}, {_id:53, properties:{id:"node_13"}}, {_id:56, properties:{id:"node_16"}}, {_id:58, properties:{id:"node_18"}}, {_id:65, properties:{id:"node_25"}}, {_id:77, properties:{id:"node_37"}}, {_id:78, properties:{id:"node_38"}}, {_id:84, properties:{id:"node_44"}}, {_id:88, properties:{id:"node_48"}}, {_id:89, properties:{id:"node_49"}}, {_id:133, properties:{id:"node_3"}}, {_id:134, properties:{id:"node_4"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N3;
UNWIND [{_id:52, properties:{id:"node_12"}}, {_id:54, properties:{id:"node_14"}}, {_id:57, properties:{id:"node_17"}}, {_id:68, properties:{id:"node_28"}}, {_id:69, properties:{id:"node_29"}}, {_id:87, properties:{id:"node_47"}}, {_id:137, properties:{id:"node_7"}}, {_id:139, properties:{id:"node_9"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N2;
:commit
:begin
UNWIND [{start: {_id:59}, end: {_id:63}, properties:{}}, {start: {_id:80}, end: {_id:63}, properties:{}}, {start: {_id:80}, end: {_id:67}, properties:{}}, {start: {_id:82}, end: {_id:61}, properties:{}}, {start: {_id:82}, end: {_id:63}, properties:{}}, {start: {_id:130}, end: {_id:138}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:50}, end: {_id:82}, properties:{}}, {start: {_id:50}, end: {_id:85}, properties:{}}, {start: {_id:53}, end: {_id:70}, properties:{}}, {start: {_id:56}, end: {_id:59}, properties:{}}, {start: {_id:56}, end: {_id:86}, properties:{}}, {start: {_id:58}, end: {_id:72}, properties:{}}, {start: {_id:58}, end: {_id:75}, properties:{}}, {start: {_id:58}, end: {_id:80}, properties:{}}, {start: {_id:88}, end: {_id:79}, properties:{}}, {start: {_id:88}, end: {_id:86}, properties:{}}, {start: {_id:88}, end: {_id:132}, properties:{}}, {start: {_id:89}, end: {_id:135}, properties:{}}, {start: {_id:133}, end: {_id:75}, properties:{}}, {start: {_id:133}, end: {_id:80}, properties:{}}, {start: {_id:133}, end: {_id:132}, properties:{}}, {start: {_id:134}, end: {_id:70}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:60}, end: {_id:139}, properties:{}}, {start: {_id:62}, end: {_id:54}, properties:{}}, {start: {_id:66}, end: {_id:68}, properties:{}}, {start: {_id:66}, end: {_id:139}, properties:{}}, {start: {_id:71}, end: {_id:54}, properties:{}}, {start: {_id:138}, end: {_id:68}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:52}, end: {_id:55}, properties:{}}, {start: {_id:52}, end: {_id:83}, properties:{}}, {start: {_id:52}, end: {_id:131}, properties:{}}, {start: {_id:68}, end: {_id:136}, properties:{}}, {start: {_id:87}, end: {_id:74}, properties:{}}, {start: {_id:87}, end: {_id:81}, properties:{}}, {start: {_id:139}, end: {_id:81}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:74}, end: {_id:138}, properties:{}}, {start: {_id:81}, end: {_id:62}, properties:{}}, {start: {_id:81}, end: {_id:66}, properties:{}}, {start: {_id:81}, end: {_id:71}, properties:{}}, {start: {_id:81}, end: {_id:73}, properties:{}}, {start: {_id:81}, end: {_id:138}, properties:{}}, {start: {_id:131}, end: {_id:60}, properties:{}}, {start: {_id:131}, end: {_id:63}, properties:{}}, {start: {_id:136}, end: {_id:66}, properties:{}}, {start: {_id:136}, end: {_id:67}, properties:{}}, {start: {_id:136}, end: {_id:73}, properties:{}}, {start: {_id:136}, end: {_id:138}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:60}, end: {_id:59}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:74}, end: {_id:60}, properties:{}}, {start: {_id:81}, end: {_id:60}, properties:{}}, {start: {_id:131}, end: {_id:60}, properties:{}}, {start: {_id:136}, end: {_id:60}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:50}, end: {_id:55}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:52}, end: {_id:83}, properties:{}}, {start: {_id:57}, end: {_id:74}, properties:{}}, {start: {_id:68}, end: {_id:81}, properties:{}}, {start: {_id:87}, end: {_id:81}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:55}, end: {_id:51}, properties:{}}, {start: {_id:55}, end: {_id:77}, properties:{}}, {start: {_id:55}, end: {_id:84}, properties:{}}, {start: {_id:55}, end: {_id:89}, properties:{}}, {start: {_id:74}, end: {_id:51}, properties:{}}, {start: {_id:74}, end: {_id:53}, properties:{}}, {start: {_id:74}, end: {_id:88}, properties:{}}, {start: {_id:81}, end: {_id:50}, properties:{}}, {start: {_id:81}, end: {_id:51}, properties:{}}, {start: {_id:81}, end: {_id:65}, properties:{}}, {start: {_id:81}, end: {_id:77}, properties:{}}, {start: {_id:81}, end: {_id:78}, properties:{}}, {start: {_id:81}, end: {_id:89}, properties:{}}, {start: {_id:131}, end: {_id:56}, properties:{}}, {start: {_id:131}, end: {_id:84}, properties:{}}, {start: {_id:131}, end: {_id:133}, properties:{}}, {start: {_id:131}, end: {_id:134}, properties:{}}, {start: {_id:136}, end: {_id:53}, properties:{}}, {start: {_id:136}, end: {_id:56}, properties:{}}, {start: {_id:136}, end: {_id:65}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:136}, end: {_id:84}, properties:{}}, {start: {_id:136}, end: {_id:88}, properties:{}}, {start: {_id:136}, end: {_id:89}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:75}, end: {_id:55}, properties:{}}, {start: {_id:79}, end: {_id:64}, properties:{}}, {start: {_id:79}, end: {_id:83}, properties:{}}, {start: {_id:80}, end: {_id:55}, properties:{}}, {start: {_id:80}, end: {_id:64}, properties:{}}, {start: {_id:80}, end: {_id:74}, properties:{}}, {start: {_id:80}, end: {_id:81}, properties:{}}, {start: {_id:132}, end: {_id:81}, properties:{}}, {start: {_id:132}, end: {_id:131}, properties:{}}, {start: {_id:132}, end: {_id:136}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:52}, end: {_id:68}, properties:{}}, {start: {_id:57}, end: {_id:139}, properties:{}}, {start: {_id:87}, end: {_id:52}, properties:{}}, {start: {_id:87}, end: {_id:68}, properties:{}}, {start: {_id:87}, end: {_id:139}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:50}, end: {_id:52}, properties:{}}, {start: {_id:50}, end: {_id:54}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:52}, end: {_id:61}, properties:{}}, {start: {_id:52}, end: {_id:62}, properties:{}}, {start: {_id:52}, end: {_id:66}, properties:{}}, {start: {_id:52}, end: {_id:67}, properties:{}}, {start: {_id:52}, end: {_id:71}, properties:{}}, {start: {_id:52}, end: {_id:138}, properties:{}}, {start: {_id:57}, end: {_id:73}, properties:{}}, {start: {_id:57}, end: {_id:76}, properties:{}}, {start: {_id:68}, end: {_id:63}, properties:{}}, {start: {_id:68}, end: {_id:76}, properties:{}}, {start: {_id:87}, end: {_id:60}, properties:{}}, {start: {_id:87}, end: {_id:61}, properties:{}}, {start: {_id:87}, end: {_id:63}, properties:{}}, {start: {_id:87}, end: {_id:66}, properties:{}}, {start: {_id:87}, end: {_id:67}, properties:{}}, {start: {_id:87}, end: {_id:73}, properties:{}}, {start: {_id:87}, end: {_id:76}, properties:{}}, {start: {_id:139}, end: {_id:67}, properties:{}}, {start: {_id:139}, end: {_id:138}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:59}, end: {_id:51}, properties:{}}, {start: {_id:59}, end: {_id:53}, properties:{}}, {start: {_id:59}, end: {_id:58}, properties:{}}, {start: {_id:59}, end: {_id:77}, properties:{}}, {start: {_id:59}, end: {_id:84}, properties:{}}, {start: {_id:59}, end: {_id:133}, properties:{}}, {start: {_id:80}, end: {_id:51}, properties:{}}, {start: {_id:80}, end: {_id:88}, properties:{}}, {start: {_id:82}, end: {_id:56}, properties:{}}, {start: {_id:85}, end: {_id:58}, properties:{}}, {start: {_id:85}, end: {_id:65}, properties:{}}, {start: {_id:85}, end: {_id:77}, properties:{}}, {start: {_id:85}, end: {_id:89}, properties:{}}, {start: {_id:86}, end: {_id:50}, properties:{}}, {start: {_id:86}, end: {_id:65}, properties:{}}, {start: {_id:86}, end: {_id:134}, properties:{}}, {start: {_id:130}, end: {_id:51}, properties:{}}, {start: {_id:130}, end: {_id:134}, properties:{}}, {start: {_id:135}, end: {_id:65}, properties:{}}, {start: {_id:135}, end: {_id:134}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:50}, end: {_id:52}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:59}, end: {_id:54}, properties:{}}, {start: {_id:59}, end: {_id:57}, properties:{}}, {start: {_id:59}, end: {_id:68}, properties:{}}, {start: {_id:79}, end: {_id:52}, properties:{}}, {start: {_id:79}, end: {_id:57}, properties:{}}, {start: {_id:80}, end: {_id:54}, properties:{}}, {start: {_id:80}, end: {_id:57}, properties:{}}, {start: {_id:80}, end: {_id:139}, properties:{}}, {start: {_id:82}, end: {_id:52}, properties:{}}, {start: {_id:82}, end: {_id:54}, properties:{}}, {start: {_id:82}, end: {_id:57}, properties:{}}, {start: {_id:82}, end: {_id:68}, properties:{}}, {start: {_id:82}, end: {_id:69}, properties:{}}, {start: {_id:82}, end: {_id:87}, properties:{}}, {start: {_id:82}, end: {_id:137}, properties:{}}, {start: {_id:82}, end: {_id:139}, properties:{}}, {start: {_id:85}, end: {_id:57}, properties:{}}, {start: {_id:86}, end: {_id:54}, properties:{}}, {start: {_id:86}, end: {_id:57}, properties:{}}, {start: {_id:130}, end: {_id:52}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:130}, end: {_id:137}, properties:{}}, {start: {_id:132}, end: {_id:57}, properties:{}}, {start: {_id:135}, end: {_id:52}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:134}, end: {_id:76}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:53}, end: {_id:73}, properties:{}}, {start: {_id:56}, end: {_id:66}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:60}, end: {_id:54}, properties:{}}, {start: {_id:60}, end: {_id:87}, properties:{}}, {start: {_id:63}, end: {_id:52}, properties:{}}, {start: {_id:66}, end: {_id:52}, properties:{}}, {start: {_id:66}, end: {_id:139}, properties:{}}, {start: {_id:138}, end: {_id:57}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:50}, end: {_id:51}, properties:{}}, {start: {_id:50}, end: {_id:53}, properties:{}}, {start: {_id:53}, end: {_id:58}, properties:{}}, {start: {_id:53}, end: {_id:65}, properties:{}}, {start: {_id:53}, end: {_id:84}, properties:{}}, {start: {_id:53}, end: {_id:88}, properties:{}}, {start: {_id:53}, end: {_id:134}, properties:{}}, {start: {_id:89}, end: {_id:50}, properties:{}}, {start: {_id:134}, end: {_id:58}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:53}, end: {_id:71}, properties:{}}, {start: {_id:89}, end: {_id:60}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:85}, end: {_id:138}, properties:{}}, {start: {_id:132}, end: {_id:67}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:55}, end: {_id:50}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:60}, end: {_id:50}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:60}, end: {_id:54}, properties:{}}, {start: {_id:60}, end: {_id:57}, properties:{}}, {start: {_id:71}, end: {_id:68}, properties:{}}, {start: {_id:138}, end: {_id:52}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:60}, end: {_id:51}, properties:{}}, {start: {_id:60}, end: {_id:58}, properties:{}}, {start: {_id:60}, end: {_id:65}, properties:{}}, {start: {_id:60}, end: {_id:78}, properties:{}}, {start: {_id:60}, end: {_id:88}, properties:{}}, {start: {_id:61}, end: {_id:65}, properties:{}}, {start: {_id:61}, end: {_id:78}, properties:{}}, {start: {_id:61}, end: {_id:84}, properties:{}}, {start: {_id:61}, end: {_id:88}, properties:{}}, {start: {_id:62}, end: {_id:58}, properties:{}}, {start: {_id:62}, end: {_id:89}, properties:{}}, {start: {_id:66}, end: {_id:56}, properties:{}}, {start: {_id:66}, end: {_id:65}, properties:{}}, {start: {_id:66}, end: {_id:78}, properties:{}}, {start: {_id:66}, end: {_id:134}, properties:{}}, {start: {_id:71}, end: {_id:51}, properties:{}}, {start: {_id:71}, end: {_id:65}, properties:{}}, {start: {_id:73}, end: {_id:51}, properties:{}}, {start: {_id:73}, end: {_id:58}, properties:{}}, {start: {_id:73}, end: {_id:78}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:73}, end: {_id:84}, properties:{}}, {start: {_id:138}, end: {_id:56}, properties:{}}, {start: {_id:138}, end: {_id:65}, properties:{}}, {start: {_id:138}, end: {_id:134}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
:commit
:begin
MATCH (n:`UNIQUE IMPORT LABEL`)  WITH n LIMIT 20000 REMOVE n:`UNIQUE IMPORT LABEL` REMOVE n.`UNIQUE IMPORT ID`;
:commit
:begin
DROP CONSTRAINT UNIQUE_IMPORT_NAME;
:commit
