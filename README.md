# Description

PyMyTools: simple diagnostic toolkit for Amazon Aurora and MySQL

Version: 0.1

See [this blog post](http://blog.symedia.pl/2016/11/pymytools-simple-diagnostic-aurora-mysql.html) for more information and tool demonstrations.

# Available commands

| Command | Description |
| --- | --- |
| `pmt_instance_report` | Summarize server status variables and sample engine metrics |
| `pmt_cluster_report` | Explain Aurora cluster topology, sumamrize status variables and sample engine metrics |
| `pmt_diag_monitor` | Regularly dump output from diagnostic statements |
| `pmt_statvar_monitor` | Print per-second averages of server status variables |
| `pmt_query_report` | Print diagnostic information for a SELECT query |
| `pmt_table_report` | Find tables and print details about table structure, indexes and statistics; find index design issues |

# Command documentation

## Common parameters

The below parameters are supported by all `pmt_*` commands:

| Parameter | Description |
| --- | --- |
| `--host` | Hostname/address of the server |
| `--socket` | Local MySQL socket (mutually exclusive with `--host`) |
| `--user` | Database user |
| `--password` | Database password; if not provided, the tool will prompt for password at run time |
| `--run-at` | Delay tool execution until the specified time (UTC), format: YYYY-MM-DDTHH:MM:SS (example: 2016-10-31T12:25:00) |
| `--help` | Display command syntax and parameter descriptions, then exit |

## pmt_instance_report

Depending on the features enabled, the tool uses the following sources of information:

- `SHOW GLOBAL STATUS`
- `SHOW GLOBAL VARIABLES`
- `INFORMATION_SCHEMA.PROCESSLIST`

Parameters:

| Parameter | Description |
| --- | --- |
| `--sample-length` | Sample length (seconds), default: 5 |

## pmt_cluster_report

Depending on the features enabled, the tool uses the following sources of information:

- `SHOW GLOBAL STATUS`
- `SHOW GLOBAL VARIABLES`
- `INFORMATION_SCHEMA.PROCESSLIST`
- `INFORMATION_SCHEMA.REPLICA_HOST_STATUS` (Amazon Aurora only)

Parameters:

| Parameter | Description |
| --- | --- |
| `--sample-length` | Sample length (seconds), default: do not sample |

## pmt_diag_monitor

Depending on the features enabled, the tool uses the following sources of information:

- `SHOW FULL PROCESSLIST`
- `SHOW GLOBAL STATUS`
- `SHOW ENGINE INNODB STATUS`
- `INFORMATION_SCHEMA.INNODB_TRX`
- `INFORMATION_SCHEMA.INNODB_LOCKS`
- `INFORMATION_SCHEMA.INNODB_LOCK_WAITS`

Parameters:

| Parameter | Description |
| --- | --- |
| `--interval` | Dump interval in seconds; default: 60 |
| `--count` | Dump count; default: 15 |
| `--output-dir` | Output directory; default ./pmt_diag_monitor_YYYYMMDD-HHMMSS |
| `--skip-processlist` | Skip processlit output; default: False |
| `--skip-global-status` | Skip global status output; default: False |
| `--skip-innodb-status` | Skip innodb engine status output; default: False |
| `--skip-innodb-trx` | Skip information_schema.innodb_trx output; default: False |
| `--skip-innodb-locks` | Skip information_schema.innodb_locks output; default: False |
| `--skip-innodb-lock-waits` | Skip a join query on information_schema.innodb_lock_waits and information_schema.innodb_trx; default: False |

## pmt_statvar_monitor

Depending on the features enabled, the tool uses the following sources of information:

- `SHOW GLOBAL STATUS`

Parameters:

| Parameter | Description |
| --- | --- |
| `--interval` | Report interval in seconds; default: 1 |
| `--count` | Report count; default: 60 |
| `--header-repeat` | Header repeat interval; default: 20 |
| `--csv` | Enable CSV output |
| `variable` | List of status variables to monitor, default: 'Questions', 'Com_select', 'Com_insert', 'Com_delete', 'Com_update', 'Created_tmp_tables', 'Created_tmp_disk_tables', 'Innodb_row_lock_time' |

## pmt_query_report

Depending on the features enabled, the tool uses the following sources of information:

- `EXPLAIN`
- `SHOW PROFILE`

Parameters:

| Parameter | Description |
| --- | --- |
| `--input-file` | Input file containing the query |
| `--trace` | Show optimizer trace (EXPLAIN JSON) |
| `--vertical` | Use vertical output instead of tabular for EXPLAIN |
| `--profile` | Execute the query twice with profiling |

## pmt_table_report

Depending on the features enabled, the tool uses the following sources of information:

- `SHOW GLOBAL VARIABLES`
- `SHOW CREATE TABLE`
- `INFORMATION_SCHEMA.TABLES`
- `INFORMATION_SCHEMA.STATISTICS`

Parameters:

| Parameter | Description |
| --- | --- |
| `--analyze` | Analyze the table and report index cardinality changes; default: False |
| `--find` | Only find the table, do not generate report; default: False |
| `--analyze-extended` | Analyze the table using 2 sample sizes (server/table default and sample size specified in --extended-sample-size); report index cardinality changes (implies --analyze, default: False); requires ALTER privilege on the table |
| `--extended-sample-size` | Page count for stats sampling with --analyze-extended; default: 256 |
| `table_name` | Table name (required) |
| `table_schema` | Table schema (optional) |

# Miscellaneous

### Features unique to Amazon Aurora

PyMyTools enjoy the following unique features when used against Amazon Aurora:

- Support for statement latency calculations in `pmt_instance_report`, `pmt_cluster_report` 
- Support for statement latency status variables in `pmt_statvar_monitor`
- `pmt_cluster_report`

### Elevated privilege requirements

The tool does not require administrative privileges such as SUPER, FILE. It can be used against managed MySQL servers that don't provide such privileges.
