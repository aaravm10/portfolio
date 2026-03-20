<?php
/* about.php - about page for ReDesign Home Staging website */

/* team members array - add or remove members here */
$team = [
    [
        'name'  => 'Ana Silva',
        'role'  => 'Designer',
        'bio'   => 'Talented designer with a passion for creating beautiful and functional spaces.',
        'photo' => '../images/placeholder-pfp.png',
        'alt'   => 'Ana Silva'
    ],
    [
        'name'  => 'Elizabeth Lopez',
        'role'  => 'Designer',
        'bio'   => 'Experienced designer with a strong eye for detail and a passion for creating beautiful and functional spaces.',
        'photo' => '../images/placeholder-pfp.png',
        'alt'   => 'Elizabeth Lopez'
    ],
    [
        'name'  => 'Pedro Silva',
        'role'  => 'Realtor',
        'bio'   => 'Experienced realtor with a passion for helping clients find their dream home.',
        'photo' => '../images/placeholder-pfp.png',
        'alt'   => 'Pedro Silva'
    ],
    [
        'name'  => 'Adrian Lopez',
        'role'  => 'Realtor',
        'bio'   => 'Professional realtor with years of experience in the real estate industry.',
        'photo' => '../images/placeholder-pfp.png',
        'alt'   => 'Adrian Lopez'
    ]
];

?>
<!DOCTYPE html>

<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>About | ReDesign Home Staging</title>
        <link rel="stylesheet" href="../css/base.css" />
        <link rel="stylesheet" href="../css/footer.css" />
        <link rel="stylesheet" href="../css/about.css" />
    </head>

    <body>

        <!-- navbar -->
        <nav id="navbar">
            <a href="index.php" id="brand">ReDesign Home Staging</a>

            <ul id="nav-links">
                <li><a href="../services.html">Services</a></li>
                <li><a href="../php/about.php" class="active">About</a></li>
                <li><a href="../consult.html" id="nav-book">Book A Consultation</a></li>
            </ul>

            <!-- hamburger menu for mobile responsiveness -->
            <button id="nav-toggle" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </nav>

        <!-- about page content -->
        <main id="page-body">

            <!-- page header -->
            <section class="about-header">
                <p id="about-title"><span class="gold">✦ ABOUT US</span></p>
                <h1>ReDesign Home Staging</h1>
                <p>ReDesign Home Staging is a team of talented designers and realtors who are passionate about helping clients <span class="gold">sell their homes for the best price possible.</span></p>
                <p>We provide <span class="gold">premium, modern staging</span> solutions tailored to today's fast-paced real estate market. We transform empty houses into styled, click-worthy homes that sell faster and for top dollar. Serving the <span class="gold">Bay Area</span> and <span class="gold">neighboring counties</span>, we blend current design trends with strategic furniture placement to help buyers visualize their future.</p>
            </section>

            <!-- meet the team -->
            <section class="about-team">
                <p><span class="gold">✦ OUR PEOPLE</span></p>
                <h2>Meet The <span class="italic gold">Team</span></h2>

                <div class="team-carousel">

                    <!-- prev arrow -->
                    <button class="carousel-btn prev" aria-label="Previous">&#8592;</button>

                    <!-- sliding track wrapper — clips overflow -->
                    <div class="carousel-track-wrapper">
                        <div class="carousel-track">
                            <?php foreach ($team as $member): ?>
                                <div class="team-member">
                                    <div class="team-photo">
                                        <img src="<?php echo $member['photo']; ?>" alt="<?php echo $member['alt']; ?>" />
                                    </div>
                                    <h3><?php echo $member['name']; ?></h3>
                                    <p class="team-role"><?php echo $member['role']; ?></p>
                                    <p class="team-bio"><?php echo $member['bio']; ?></p>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>

                    <!-- next arrow -->
                    <button class="carousel-btn next" aria-label="Next">&#8594;</button>

                </div>
            </section>

        </main>

        <!-- footer -->
        <footer>
            <div class="footer-cta">
                <p class="footer-cta-label">✦ Ready To Sell?</p>
                <h2>Transform Your Home.<br><em>Maximize Your Sale.</em></h2>
                <a href="../consult.html" class="footer-cta-btn">Book A Consultation</a>
            </div>

            <div class="footer-lower">
                <div class="footer-grid">
                    <div>
                        <p class="footer-brand">ReDesign Home Staging</p>
                        <p class="footer-tagline">We transform homes buyers fall in love with before they step inside. Professional staging that elevates your listing.</p>
                    </div>
                    <div class="footer-col">
                        <h4>Services</h4>
                        <ul>
                            <li><a href="../services.html#packages">Standard</a></li>
                            <li><a href="../services.html#packages">Professional</a></li>
                            <li><a href="../services.html#packages">Expert</a></li>
                        </ul>
                    </div>
                    <div class="footer-col">
                        <h4>Company</h4>
                        <ul>
                            <li><a href="index.php#portfolio">Portfolio</a></li>
                            <li><a href="about.php">About Us</a></li>
                            <li><a href="index.php#testimonials">Testimonials</a></li>
                        </ul>
                    </div>
                    <div class="footer-col">
                        <h4>Contact</h4>
                        <ul>
                            <li><a>(xxx) xxx-xxxx</a></li>
                            <li><a href="mailto:email@email.com">email@email.com</a></li>
                            <li><a href="https://www.realtor.com" target="_blank">Realtor.com</a></li>
                        </ul>
                    </div>
                </div>
                <div class="footer-bottom">
                    <span>&copy; 2026 ReDesign Home Staging. All rights reserved.</span>
                    <span>Diego Silva &middot; Cole Prendeville &middot; Aarav Mehta</span>
                </div>
            </div>
        </footer>

        <script src="../js/navbar.js"></script>
        <script src="../js/about.js"></script>

    </body>
</html>