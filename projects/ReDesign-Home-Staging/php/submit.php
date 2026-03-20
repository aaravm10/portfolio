<?php
/* submit.php - consultation page utility to process form submission */

require_once __DIR__ . '/db.php';

/* only accept POST requests */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../consult.html');
    exit;
}

/* collect form data */
$name       = trim($_POST['name']    ?? '');
$email      = trim($_POST['email']   ?? '');
$phone      = trim($_POST['phone']   ?? '');
$date       = trim($_POST['date']    ?? '');
$message    = trim($_POST['message'] ?? '');

/* validation */
$errors = [];

if (empty($name)) {
    $errors[] = 'Name is required.';
}
if (empty($email)) {
    $errors[] = 'Email is required.';
} elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'Invalid email format.';
}
if (empty($message)) {
    $errors[] = 'Message is required.';
}

/* redirect back to form if validation fails */
if (!empty($errors)) {
    header('Location: ../consult.html');
    exit;
}

/* redirect to confirmation page on success */
try {
    $stmt = db()->prepare("
        INSERT INTO contact_requests 
            (name, email, phone, date, message)
        VALUES 
            (:name, :email, :phone, :date, :message)
    ");
    $stmt->execute([
        'name' => $name,
        'email' => $email,
        'phone' => $phone,
        'date' => $date,
        'message' => $message,
    ]);
} catch (PDOException $e) {
    error_log("Database error: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['error' => 'Failed to submit request']);
    exit;
}

header('Location: ../form-utils/confirmation.html');
exit;
?>