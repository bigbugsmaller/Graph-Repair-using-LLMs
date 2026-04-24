:begin
CREATE CONSTRAINT UNIQUE_IMPORT_NAME FOR (node:`UNIQUE IMPORT LABEL`) REQUIRE (node.`UNIQUE IMPORT ID`) IS UNIQUE;
:commit
CALL db.awaitIndexes(300);
:begin
UNWIND [{_id:2, properties:{id:"node_2"}}, {_id:6, properties:{id:"node_6"}}, {_id:7, properties:{id:"node_7"}}, {_id:19, properties:{id:"node_19"}}, {_id:27, properties:{id:"node_27"}}, {_id:29, properties:{id:"node_29"}}, {_id:30, properties:{id:"node_30"}}, {_id:31, properties:{id:"node_31"}}, {_id:48, properties:{id:"node_48"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N1;
UNWIND [{_id:15, properties:{x:93, id:"node_15"}}, {_id:21, properties:{x:66, id:"node_21"}}, {_id:26, properties:{x:71, id:"node_26"}}, {_id:28, properties:{x:71, id:"node_28"}}, {_id:38, properties:{x:93, id:"node_38"}}, {_id:46, properties:{x:68, id:"node_46"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N5;
UNWIND [{_id:8, properties:{date_val:date('2005-09-24'), id:"node_8"}}, {_id:10, properties:{date_val:date('2012-11-27'), id:"node_10"}}, {_id:11, properties:{date_val:date('2016-09-23'), id:"node_11"}}, {_id:12, properties:{date_val:date('2017-05-27'), id:"node_12"}}, {_id:22, properties:{date_val:date('2019-11-05'), id:"node_22"}}, {_id:23, properties:{date_val:date('2000-09-02'), id:"node_23"}}, {_id:32, properties:{date_val:date('2009-12-29'), id:"node_32"}}, {_id:35, properties:{date_val:date('2002-01-20'), id:"node_35"}}, {_id:36, properties:{date_val:date('2006-01-12'), id:"node_36"}}, {_id:41, properties:{date_val:date('2003-05-09'), id:"node_41"}}, {_id:47, properties:{date_val:date('2009-11-11'), id:"node_47"}}, {_id:49, properties:{date_val:date('2017-05-20'), id:"node_49"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N4;
UNWIND [{_id:1, properties:{date_val:date('2021-11-18'), id:"node_1"}}, {_id:3, properties:{date_val:date('2020-12-30'), id:"node_3"}}, {_id:16, properties:{date_val:date('2005-09-22'), id:"node_16"}}, {_id:18, properties:{date_val:date('2010-02-17'), id:"node_18"}}, {_id:20, properties:{date_val:date('2013-07-03'), id:"node_20"}}, {_id:34, properties:{date_val:date('2006-07-18'), id:"node_34"}}, {_id:39, properties:{date_val:date('2007-01-21'), id:"node_39"}}, {_id:42, properties:{date_val:date('2004-11-09'), id:"node_42"}}, {_id:43, properties:{date_val:date('2014-11-19'), id:"node_43"}}, {_id:44, properties:{date_val:date('2001-03-27'), id:"node_44"}}, {_id:45, properties:{date_val:date('2005-02-11'), id:"node_45"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N3;
UNWIND [{_id:0, properties:{id:"node_0"}}, {_id:4, properties:{id:"node_4"}}, {_id:5, properties:{id:"node_5"}}, {_id:9, properties:{id:"node_9"}}, {_id:13, properties:{id:"node_13"}}, {_id:14, properties:{id:"node_14"}}, {_id:17, properties:{id:"node_17"}}, {_id:24, properties:{id:"node_24"}}, {_id:25, properties:{id:"node_25"}}, {_id:33, properties:{id:"node_33"}}, {_id:37, properties:{id:"node_37"}}, {_id:40, properties:{id:"node_40"}}] AS row
CREATE (n:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row._id}) SET n += row.properties SET n:N2;
:commit
:begin
UNWIND [{start: {_id:9}, end: {_id:29}, properties:{}}, {start: {_id:14}, end: {_id:19}, properties:{}}, {start: {_id:25}, end: {_id:19}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:2}, end: {_id:0}, properties:{}}, {start: {_id:6}, end: {_id:0}, properties:{}}, {start: {_id:27}, end: {_id:0}, properties:{}}, {start: {_id:31}, end: {_id:0}, properties:{}}, {start: {_id:48}, end: {_id:0}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:3}, end: {_id:2}, properties:{}}, {start: {_id:3}, end: {_id:6}, properties:{}}, {start: {_id:3}, end: {_id:7}, properties:{}}, {start: {_id:3}, end: {_id:19}, properties:{}}, {start: {_id:16}, end: {_id:6}, properties:{}}, {start: {_id:16}, end: {_id:7}, properties:{}}, {start: {_id:16}, end: {_id:19}, properties:{}}, {start: {_id:16}, end: {_id:27}, properties:{}}, {start: {_id:20}, end: {_id:6}, properties:{}}, {start: {_id:20}, end: {_id:7}, properties:{}}, {start: {_id:20}, end: {_id:30}, properties:{}}, {start: {_id:34}, end: {_id:6}, properties:{}}, {start: {_id:34}, end: {_id:19}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:3}, end: {_id:0}, properties:{}}, {start: {_id:16}, end: {_id:0}, properties:{}}, {start: {_id:20}, end: {_id:0}, properties:{}}, {start: {_id:44}, end: {_id:0}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:8}, end: {_id:2}, properties:{}}, {start: {_id:8}, end: {_id:6}, properties:{}}, {start: {_id:8}, end: {_id:7}, properties:{}}, {start: {_id:8}, end: {_id:27}, properties:{}}, {start: {_id:10}, end: {_id:31}, properties:{}}, {start: {_id:12}, end: {_id:29}, properties:{}}, {start: {_id:22}, end: {_id:2}, properties:{}}, {start: {_id:22}, end: {_id:27}, properties:{}}, {start: {_id:23}, end: {_id:6}, properties:{}}, {start: {_id:23}, end: {_id:7}, properties:{}}, {start: {_id:23}, end: {_id:27}, properties:{}}, {start: {_id:23}, end: {_id:31}, properties:{}}, {start: {_id:36}, end: {_id:19}, properties:{}}, {start: {_id:36}, end: {_id:29}, properties:{}}, {start: {_id:41}, end: {_id:7}, properties:{}}, {start: {_id:47}, end: {_id:19}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:2}, end: {_id:7}, properties:{}}, {start: {_id:2}, end: {_id:19}, properties:{}}, {start: {_id:2}, end: {_id:48}, properties:{}}, {start: {_id:6}, end: {_id:19}, properties:{}}, {start: {_id:6}, end: {_id:30}, properties:{}}, {start: {_id:27}, end: {_id:29}, properties:{}}, {start: {_id:27}, end: {_id:48}, properties:{}}, {start: {_id:31}, end: {_id:2}, properties:{}}, {start: {_id:31}, end: {_id:6}, properties:{}}, {start: {_id:31}, end: {_id:19}, properties:{}}, {start: {_id:31}, end: {_id:48}, properties:{}}, {start: {_id:48}, end: {_id:6}, properties:{}}, {start: {_id:48}, end: {_id:19}, properties:{}}, {start: {_id:48}, end: {_id:27}, properties:{}}, {start: {_id:48}, end: {_id:30}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:3}, end: {_id:8}, properties:{}}, {start: {_id:3}, end: {_id:10}, properties:{}}, {start: {_id:3}, end: {_id:11}, properties:{}}, {start: {_id:3}, end: {_id:12}, properties:{}}, {start: {_id:3}, end: {_id:22}, properties:{}}, {start: {_id:3}, end: {_id:23}, properties:{}}, {start: {_id:3}, end: {_id:32}, properties:{}}, {start: {_id:3}, end: {_id:35}, properties:{}}, {start: {_id:3}, end: {_id:36}, properties:{}}, {start: {_id:3}, end: {_id:41}, properties:{}}, {start: {_id:3}, end: {_id:47}, properties:{}}, {start: {_id:3}, end: {_id:49}, properties:{}}, {start: {_id:16}, end: {_id:8}, properties:{}}, {start: {_id:16}, end: {_id:10}, properties:{}}, {start: {_id:16}, end: {_id:12}, properties:{}}, {start: {_id:16}, end: {_id:22}, properties:{}}, {start: {_id:16}, end: {_id:23}, properties:{}}, {start: {_id:16}, end: {_id:32}, properties:{}}, {start: {_id:16}, end: {_id:36}, properties:{}}, {start: {_id:16}, end: {_id:47}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:16}, end: {_id:49}, properties:{}}, {start: {_id:20}, end: {_id:10}, properties:{}}, {start: {_id:20}, end: {_id:12}, properties:{}}, {start: {_id:20}, end: {_id:22}, properties:{}}, {start: {_id:20}, end: {_id:23}, properties:{}}, {start: {_id:20}, end: {_id:32}, properties:{}}, {start: {_id:20}, end: {_id:41}, properties:{}}, {start: {_id:44}, end: {_id:23}, properties:{}}, {start: {_id:44}, end: {_id:41}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R1]->(end) SET r += row.properties;
UNWIND [{start: {_id:3}, end: {_id:0}, properties:{}}, {start: {_id:3}, end: {_id:4}, properties:{}}, {start: {_id:3}, end: {_id:5}, properties:{}}, {start: {_id:3}, end: {_id:9}, properties:{}}, {start: {_id:3}, end: {_id:14}, properties:{}}, {start: {_id:3}, end: {_id:17}, properties:{}}, {start: {_id:3}, end: {_id:37}, properties:{}}, {start: {_id:3}, end: {_id:40}, properties:{}}, {start: {_id:16}, end: {_id:9}, properties:{}}, {start: {_id:16}, end: {_id:14}, properties:{}}, {start: {_id:16}, end: {_id:17}, properties:{}}, {start: {_id:16}, end: {_id:25}, properties:{}}, {start: {_id:16}, end: {_id:37}, properties:{}}, {start: {_id:16}, end: {_id:40}, properties:{}}, {start: {_id:20}, end: {_id:5}, properties:{}}, {start: {_id:20}, end: {_id:9}, properties:{}}, {start: {_id:20}, end: {_id:17}, properties:{}}, {start: {_id:20}, end: {_id:24}, properties:{}}, {start: {_id:20}, end: {_id:25}, properties:{}}, {start: {_id:20}, end: {_id:40}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:34}, end: {_id:0}, properties:{}}, {start: {_id:34}, end: {_id:5}, properties:{}}, {start: {_id:34}, end: {_id:13}, properties:{}}, {start: {_id:34}, end: {_id:14}, properties:{}}, {start: {_id:34}, end: {_id:24}, properties:{}}, {start: {_id:44}, end: {_id:9}, properties:{}}, {start: {_id:44}, end: {_id:24}, properties:{}}, {start: {_id:44}, end: {_id:25}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:3}, end: {_id:28}, properties:{}}, {start: {_id:3}, end: {_id:46}, properties:{}}, {start: {_id:16}, end: {_id:21}, properties:{}}, {start: {_id:20}, end: {_id:21}, properties:{}}, {start: {_id:20}, end: {_id:46}, properties:{}}, {start: {_id:44}, end: {_id:26}, properties:{}}, {start: {_id:44}, end: {_id:46}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:15}, end: {_id:1}, properties:{}}, {start: {_id:28}, end: {_id:34}, properties:{}}, {start: {_id:38}, end: {_id:3}, properties:{}}, {start: {_id:38}, end: {_id:16}, properties:{}}, {start: {_id:38}, end: {_id:18}, properties:{}}, {start: {_id:38}, end: {_id:20}, properties:{}}, {start: {_id:38}, end: {_id:42}, properties:{}}, {start: {_id:38}, end: {_id:43}, properties:{}}, {start: {_id:46}, end: {_id:1}, properties:{}}, {start: {_id:46}, end: {_id:44}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:0}, end: {_id:40}, properties:{}}, {start: {_id:9}, end: {_id:33}, properties:{}}, {start: {_id:14}, end: {_id:24}, properties:{}}, {start: {_id:33}, end: {_id:13}, properties:{}}, {start: {_id:40}, end: {_id:14}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:15}, end: {_id:4}, properties:{}}, {start: {_id:15}, end: {_id:14}, properties:{}}, {start: {_id:15}, end: {_id:40}, properties:{}}, {start: {_id:21}, end: {_id:0}, properties:{}}, {start: {_id:21}, end: {_id:4}, properties:{}}, {start: {_id:21}, end: {_id:5}, properties:{}}, {start: {_id:21}, end: {_id:37}, properties:{}}, {start: {_id:28}, end: {_id:4}, properties:{}}, {start: {_id:28}, end: {_id:5}, properties:{}}, {start: {_id:28}, end: {_id:14}, properties:{}}, {start: {_id:28}, end: {_id:24}, properties:{}}, {start: {_id:28}, end: {_id:25}, properties:{}}, {start: {_id:28}, end: {_id:33}, properties:{}}, {start: {_id:38}, end: {_id:4}, properties:{}}, {start: {_id:38}, end: {_id:5}, properties:{}}, {start: {_id:38}, end: {_id:13}, properties:{}}, {start: {_id:38}, end: {_id:40}, properties:{}}, {start: {_id:46}, end: {_id:37}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:0}, end: {_id:15}, properties:{}}, {start: {_id:25}, end: {_id:38}, properties:{}}, {start: {_id:33}, end: {_id:21}, properties:{}}, {start: {_id:40}, end: {_id:26}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:2}, end: {_id:1}, properties:{}}, {start: {_id:2}, end: {_id:16}, properties:{}}, {start: {_id:6}, end: {_id:16}, properties:{}}, {start: {_id:6}, end: {_id:18}, properties:{}}, {start: {_id:6}, end: {_id:34}, properties:{}}, {start: {_id:27}, end: {_id:18}, properties:{}}, {start: {_id:27}, end: {_id:42}, properties:{}}, {start: {_id:31}, end: {_id:1}, properties:{}}, {start: {_id:31}, end: {_id:16}, properties:{}}, {start: {_id:31}, end: {_id:34}, properties:{}}, {start: {_id:31}, end: {_id:43}, properties:{}}, {start: {_id:31}, end: {_id:45}, properties:{}}, {start: {_id:48}, end: {_id:1}, properties:{}}, {start: {_id:48}, end: {_id:3}, properties:{}}, {start: {_id:48}, end: {_id:16}, properties:{}}, {start: {_id:48}, end: {_id:20}, properties:{}}, {start: {_id:48}, end: {_id:39}, properties:{}}, {start: {_id:48}, end: {_id:43}, properties:{}}, {start: {_id:48}, end: {_id:44}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:8}, end: {_id:3}, properties:{}}, {start: {_id:8}, end: {_id:18}, properties:{}}, {start: {_id:8}, end: {_id:20}, properties:{}}, {start: {_id:8}, end: {_id:34}, properties:{}}, {start: {_id:8}, end: {_id:45}, properties:{}}, {start: {_id:10}, end: {_id:3}, properties:{}}, {start: {_id:10}, end: {_id:42}, properties:{}}, {start: {_id:10}, end: {_id:43}, properties:{}}, {start: {_id:10}, end: {_id:44}, properties:{}}, {start: {_id:12}, end: {_id:34}, properties:{}}, {start: {_id:22}, end: {_id:16}, properties:{}}, {start: {_id:22}, end: {_id:18}, properties:{}}, {start: {_id:22}, end: {_id:43}, properties:{}}, {start: {_id:22}, end: {_id:44}, properties:{}}, {start: {_id:22}, end: {_id:45}, properties:{}}, {start: {_id:23}, end: {_id:1}, properties:{}}, {start: {_id:23}, end: {_id:3}, properties:{}}, {start: {_id:23}, end: {_id:18}, properties:{}}, {start: {_id:23}, end: {_id:39}, properties:{}}, {start: {_id:23}, end: {_id:42}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:36}, end: {_id:18}, properties:{}}, {start: {_id:36}, end: {_id:39}, properties:{}}, {start: {_id:36}, end: {_id:44}, properties:{}}, {start: {_id:41}, end: {_id:1}, properties:{}}, {start: {_id:41}, end: {_id:20}, properties:{}}, {start: {_id:41}, end: {_id:42}, properties:{}}, {start: {_id:41}, end: {_id:44}, properties:{}}, {start: {_id:47}, end: {_id:1}, properties:{}}, {start: {_id:47}, end: {_id:44}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:8}, end: {_id:12}, properties:{}}, {start: {_id:8}, end: {_id:41}, properties:{}}, {start: {_id:8}, end: {_id:47}, properties:{}}, {start: {_id:8}, end: {_id:49}, properties:{}}, {start: {_id:10}, end: {_id:22}, properties:{}}, {start: {_id:10}, end: {_id:32}, properties:{}}, {start: {_id:10}, end: {_id:36}, properties:{}}, {start: {_id:10}, end: {_id:47}, properties:{}}, {start: {_id:10}, end: {_id:49}, properties:{}}, {start: {_id:12}, end: {_id:22}, properties:{}}, {start: {_id:12}, end: {_id:23}, properties:{}}, {start: {_id:12}, end: {_id:35}, properties:{}}, {start: {_id:22}, end: {_id:11}, properties:{}}, {start: {_id:22}, end: {_id:32}, properties:{}}, {start: {_id:23}, end: {_id:8}, properties:{}}, {start: {_id:23}, end: {_id:10}, properties:{}}, {start: {_id:23}, end: {_id:11}, properties:{}}, {start: {_id:23}, end: {_id:12}, properties:{}}, {start: {_id:23}, end: {_id:36}, properties:{}}, {start: {_id:23}, end: {_id:47}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:36}, end: {_id:23}, properties:{}}, {start: {_id:36}, end: {_id:32}, properties:{}}, {start: {_id:36}, end: {_id:35}, properties:{}}, {start: {_id:36}, end: {_id:49}, properties:{}}, {start: {_id:47}, end: {_id:35}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R2]->(end) SET r += row.properties;
UNWIND [{start: {_id:0}, end: {_id:8}, properties:{}}, {start: {_id:9}, end: {_id:10}, properties:{}}, {start: {_id:14}, end: {_id:23}, properties:{}}, {start: {_id:25}, end: {_id:12}, properties:{}}, {start: {_id:33}, end: {_id:10}, properties:{}}, {start: {_id:40}, end: {_id:32}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:2}, end: {_id:4}, properties:{}}, {start: {_id:2}, end: {_id:17}, properties:{}}, {start: {_id:2}, end: {_id:33}, properties:{}}, {start: {_id:6}, end: {_id:24}, properties:{}}, {start: {_id:6}, end: {_id:33}, properties:{}}, {start: {_id:27}, end: {_id:5}, properties:{}}, {start: {_id:27}, end: {_id:17}, properties:{}}, {start: {_id:27}, end: {_id:37}, properties:{}}, {start: {_id:31}, end: {_id:4}, properties:{}}, {start: {_id:31}, end: {_id:9}, properties:{}}, {start: {_id:31}, end: {_id:13}, properties:{}}, {start: {_id:31}, end: {_id:33}, properties:{}}, {start: {_id:48}, end: {_id:0}, properties:{}}, {start: {_id:48}, end: {_id:4}, properties:{}}, {start: {_id:48}, end: {_id:13}, properties:{}}, {start: {_id:48}, end: {_id:14}, properties:{}}, {start: {_id:48}, end: {_id:17}, properties:{}}, {start: {_id:48}, end: {_id:25}, properties:{}}, {start: {_id:48}, end: {_id:33}, properties:{}}, {start: {_id:48}, end: {_id:37}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:48}, end: {_id:40}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R4]->(end) SET r += row.properties;
UNWIND [{start: {_id:3}, end: {_id:46}, properties:{}}, {start: {_id:16}, end: {_id:21}, properties:{}}, {start: {_id:16}, end: {_id:28}, properties:{}}, {start: {_id:16}, end: {_id:38}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
UNWIND [{start: {_id:15}, end: {_id:39}, properties:{}}, {start: {_id:21}, end: {_id:16}, properties:{}}, {start: {_id:21}, end: {_id:34}, properties:{}}, {start: {_id:28}, end: {_id:20}, properties:{}}, {start: {_id:28}, end: {_id:42}, properties:{}}, {start: {_id:38}, end: {_id:16}, properties:{}}, {start: {_id:38}, end: {_id:43}, properties:{}}, {start: {_id:38}, end: {_id:44}, properties:{}}, {start: {_id:46}, end: {_id:18}, properties:{}}, {start: {_id:46}, end: {_id:20}, properties:{}}] AS row
MATCH (start:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.start._id})
MATCH (end:`UNIQUE IMPORT LABEL`{`UNIQUE IMPORT ID`: row.end._id})
CREATE (start)-[r:R3]->(end) SET r += row.properties;
:commit
:begin
MATCH (n:`UNIQUE IMPORT LABEL`)  WITH n LIMIT 20000 REMOVE n:`UNIQUE IMPORT LABEL` REMOVE n.`UNIQUE IMPORT ID`;
:commit
:begin
DROP CONSTRAINT UNIQUE_IMPORT_NAME;
:commit
