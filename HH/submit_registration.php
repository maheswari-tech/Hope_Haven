<?php
$connection = oci_connect("username", "password", "//localhost/XE"); // Use your credentials

if (!$connection) {
    $e = oci_error();
    die("Connection failed: " . $e['message']);
}

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    // 1. Retrieve and bind all form values
    $id = $_POST['id'];
    $name = $_POST['name'];
    $type = $_POST['type'];
    $capacity = $_POST['capacity'];

    $street = $_POST['address']['street'];
    $area = $_POST['address']['area'];
    $city = $_POST['address']['city'];
    $state = $_POST['address']['state'];
    $postal_code = $_POST['address']['postal_code'];
    $lat = $_POST['address']['coordinates'][0];
    $lon = $_POST['address']['coordinates'][1];

    $phone = $_POST['contact']['phone'];
    $whatsapp = $_POST['contact']['whatsapp'];
    $email = $_POST['contact']['email'];

    // 2. Insert into orphanages
    $stmt = oci_parse($connection, "INSERT INTO orphanages 
        (id, name, type, capacity, street, area, city, state, postal_code, latitude, longitude, phone, whatsapp, email) 
        VALUES (:id, :name, :type, :capacity, :street, :area, :city, :state, :postal_code, :latitude, :longitude, :phone, :whatsapp, :email)");

    oci_bind_by_name($stmt, ":id", $id);
    oci_bind_by_name($stmt, ":name", $name);
    oci_bind_by_name($stmt, ":type", $type);
    oci_bind_by_name($stmt, ":capacity", $capacity);
    oci_bind_by_name($stmt, ":street", $street);
    oci_bind_by_name($stmt, ":area", $area);
    oci_bind_by_name($stmt, ":city", $city);
    oci_bind_by_name($stmt, ":state", $state);
    oci_bind_by_name($stmt, ":postal_code", $postal_code);
    oci_bind_by_name($stmt, ":latitude", $lat);
    oci_bind_by_name($stmt, ":longitude", $lon);
    oci_bind_by_name($stmt, ":phone", $phone);
    oci_bind_by_name($stmt, ":whatsapp", $whatsapp);
    oci_bind_by_name($stmt, ":email", $email);
    oci_execute($stmt);

    // 3. Insert current needs
    foreach ($_POST['current_needs'] as $need) {
        $need_type = $need['type'];
        $quantity = $need['quantity_needed'];
        $urgency = $need['urgency'];
        $age_group = $need['age_group'] ?? null;

        $stmt2 = oci_parse($connection, "INSERT INTO current_needs 
            (orphanage_id, type, quantity_needed, urgency, age_group) 
            VALUES (:orphanage_id, :type, :quantity, :urgency, :age_group)");

        oci_bind_by_name($stmt2, ":orphanage_id", $id);
        oci_bind_by_name($stmt2, ":type", $need_type);
        oci_bind_by_name($stmt2, ":quantity", $quantity);
        oci_bind_by_name($stmt2, ":urgency", $urgency);
        oci_bind_by_name($stmt2, ":age_group", $age_group);
        oci_execute($stmt2);
    }

    // 4. Fetch back orphanage + needs
    $stmt3 = oci_parse($connection, "SELECT * FROM orphanages WHERE id = :id");
    oci_bind_by_name($stmt3, ":id", $id);
    oci_execute($stmt3);
    $orphanage = oci_fetch_assoc($stmt3);

    $stmt4 = oci_parse($connection, "SELECT type, quantity_needed, urgency, age_group FROM current_needs WHERE orphanage_id = :id");
    oci_bind_by_name($stmt4, ":id", $id);
    oci_execute($stmt4);

    // 5. Display Confirmation
    echo "<h2 style='text-align:center;'>Registration Successful!</h2>";
    echo "<h3 style='text-align:center;'>Registered Orphanage Details</h3>";
    echo "<table border='1' cellpadding='10' style='margin:auto; background:#f8f8f8; color:#000;'>";
    foreach ($orphanage as $key => $value) {
        echo "<tr><td><strong>" . htmlspecialchars($key) . "</strong></td><td>" . htmlspecialchars($value) . "</td></tr>";
    }
    echo "</table><br>";

    echo "<h3 style='text-align:center;'>Current Needs</h3>";
    echo "<table border='1' cellpadding='10' style='margin:auto; background:#fefefe; color:#000;'>
            <tr><th>Type</th><th>Quantity</th><th>Urgency</th><th>Age Group</th></tr>";
    while ($need = oci_fetch_assoc($stmt4)) {
        echo "<tr>
                <td>" . htmlspecialchars($need['TYPE']) . "</td>
                <td>" . htmlspecialchars($need['QUANTITY_NEEDED']) . "</td>
                <td>" . htmlspecialchars($need['URGENCY']) . "</td>
                <td>" . htmlspecialchars($need['AGE_GROUP']) . "</td>
              </tr>";
    }
    echo "</table><br><p style='text-align:center;'><a href='registrationform.html'>Register another</a></p>";

    oci_free_statement($stmt);
    oci_free_statement($stmt2);
    oci_free_statement($stmt3);
    oci_free_statement($stmt4);
    oci_close($connection);
}
?>
