<?php
require_once __DIR__ . '/db.php';
$pdo = db();

$pdo->exec("DELETE FROM testimonials;");
$testimonials = [
    [
        'author_name'     => 'John Doe',
        'author_location' => 'San Francisco, CA',
        'author_initials' => 'JD',
        'rating'          => 5,
        'quote'           => "ReDesign Home Staging transformed my home from a drab rental into a showstopper. The staging team's attention to detail made all the difference.",
        'sort_order'      => 1,
    ],
    [
        'author_name'     => 'Mike Johnson',
        'author_location' => 'San Jose, CA',
        'author_initials' => 'MJ',
        'rating'          => 5,
        'quote'           => "The home sold above asking within a week. Buyers kept commenting on how beautiful it looked.",
        'sort_order'      => 2,
    ],
    [
        'author_name'     => 'Jessica Brown',
        'author_location' => 'Palo Alto, CA',
        'author_initials' => 'JB',
        'rating'          => 5,
        'quote'           => "Professional, responsive, and with a great eye for detail. Highly recommend ReDesign Home Staging.",
        'sort_order'      => 3,
    ],
    [
        'author_name'     => 'Emily Davis',
        'author_location' => 'Sunnyvale, CA',
        'author_initials' => 'ED',
        'rating'          => 5,
        'quote'           => "ReDesign Home Staging made our home look amazing. We sold it for more than we expected.",
        'sort_order'      => 4,
    ],
];
$stmt = $pdo->prepare("
    INSERT INTO testimonials (author_name, author_location, author_initials, rating, quote, sort_order)
    VALUES (:author_name, :author_location, :author_initials, :rating, :quote, :sort_order)
");
foreach ($testimonials as $t) {
    $stmt->execute($t);
}

$pdo->exec("DELETE FROM photos;");
$photos = [
    [
        'file_path' => 'images/rdhs-image-2.png',
        'title'     => 'Luxury Living Room',
        'subtitle'  => null,
        'tag'       => 'Luxury',
        'location'  => 'San Jose, CA',
        'alt_text'  => 'Luxury staged living room with large window',
        'sort_order'=> 1,
    ],
    [
        'file_path' => 'images/rdhs-image-3.png',
        'title'     => 'Modern Home',
        'subtitle'  => null,
        'tag'       => 'Modern',
        'location'  => 'Hollister, CA',
        'alt_text'  => 'Modern staged home with neutral furniture',
        'sort_order'=> 2,
    ],
    [
        'file_path' => 'images/rdhs-image-4.png',
        'title'     => 'Minimal Retreat',
        'subtitle'  => null,
        'tag'       => 'Minimal',
        'location'  => 'Gilroy, CA',
        'alt_text'  => 'Minimal staged living room with greenery',
        'sort_order'=> 3,
    ],
    [
        'file_path' => 'images/rdhs-image-5.png',
        'title'     => 'Cozy Kitchen',
        'subtitle'  => null,
        'tag'       => 'Cozy',
        'location'  => 'Morgan Hill, CA',
        'alt_text'  => 'Cozy staged kitchen with modern furniture',
        'sort_order'=> 4,
    ],
    [
        'file_path' => 'images/rdhs-image-6.png',
        'title'     => 'Modern Apartment',
        'subtitle'  => null,
        'tag'       => 'Modern',
        'location'  => 'San Jose, CA',
        'alt_text'  => 'Modern staged apartment with neutral furniture',
        'sort_order'=> 5,
    ],
    [
        'file_path' => 'images/rdhs-image-7.png',
        'title'     => 'Stylish Bedroom',
        'subtitle'  => null,
        'tag'       => 'Stylish',
        'location'  => 'Milpitas, CA',
        'alt_text'  => 'Stylish staged bedroom with modern furniture',
        'sort_order'=> 6,
    ]
];
$stmtPhoto = $pdo->prepare("
    INSERT INTO photos (file_path, title, subtitle, tag, location, alt_text, sort_order)
    VALUES (:file_path, :title, :subtitle, :tag, :location, :alt_text, :sort_order)
");
foreach ($photos as $p) {
    $stmtPhoto->execute($p);
}
echo "Seed complete.\n";