# Relational Databases

A relational database stores structured data in tables made of rows and columns. A primary key uniquely identifies a row, and a foreign key links a row to a related row in another table. SQL is used to define, query, and update this data.

## Normalization

Database normalization organizes tables to reduce duplicated data and prevent update anomalies. First normal form requires atomic column values. Second and third normal forms progressively remove dependencies on only part of a key and on non-key columns. Practical designs sometimes denormalize selected data when measured performance needs justify the trade-off.

## Transactions and indexes

A transaction groups operations into one logical unit and follows the ACID properties: atomicity, consistency, isolation, and durability. An index accelerates searches on selected columns, but consumes storage and adds work to inserts and updates.
