<?php
/* migrate.php - migrate data from schema.sql to database */

$dbPath = __DIR__ . '/../data/site.db';
$schema = __DIR__ . '/../data/schema.sql';

/* make sure data directory exists */
if (!is_dir(dirname($dbPath))) {
    mkdir(dirname($dbPath), 0755, true);
}

/* load schema file */
$sql = file_get_contents($schema);
if ($sql === false) {
    die('Failed to read schema file');
}

/* connect via PDO */
$pdo = new PDO('sqlite:' . $dbPath);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$pdo->exec("PRAGMA foreign_keys = ON");

/* execute schema */
$pdo->exec($sql);

echo 'Database schema migrated successfully' . PHP_EOL;
