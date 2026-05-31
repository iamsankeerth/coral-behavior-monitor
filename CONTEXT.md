# Coral Behavior-Health Monitor

A unified local behavioral and physical health analytics platform that joins web activity data, browser extension scrolling sessions, and mobile health metrics.

## Language

**Active Logs**:
Raw StayFree browser database dumps, IndexedDB leveldb files, and Edge History records that capture real-time web usage and screen time.
_Avoid_: raw events, browser logs, history dumps

**Health Metrics**:
Physical activity metrics, specifically step counts and sleep durations, retrieved from the Health Connect export database.
_Avoid_: physical stats, health data, connect records

**Behavior Analytics**:
The aggregated SQLite database containing the final joined daily behavior, health, and focus ratios.
_Avoid_: join database, sql tables, consolidated db

**PathConfig**:
The centralized module responsible for resolving local filesystem paths, environment variables, and config properties.
_Avoid_: path resolver, file manager, workspace helper

**Hermes Communication Seam**:
The message-dispatching seam that allows sending alerts and health stats to the user (e.g. via WhatsApp) using the Hermes Agent System.
_Avoid_: message gateway, notifier, whatsapp bridge
