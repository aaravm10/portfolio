<?php
/* index.php - homepage for ReDesign Home Staging */

require_once __DIR__ . '/db.php';

/* portfolio photos (for bento grid) */
$photosStmt = db()->query("
    SELECT file_path, tag, location, title, subtitle, alt_text
    FROM photos
    ORDER BY sort_order ASC, id DESC
");
$photos = $photosStmt->fetchAll();

/* testimonials for slider */
$testimonialsStmt = db()->query("
    SELECT author_name, author_location, author_initials, rating, quote
    FROM testimonials
    ORDER BY sort_order ASC, id DESC
");
$testimonials = $testimonialsStmt->fetchAll();
?>
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>ReDesign Home Staging</title>
        <link rel="stylesheet" href="../css/base.css" />
        <link rel="stylesheet" href="../css/index.css" />
        <link rel="stylesheet" href="../css/footer.css" />
    </head>

    <body>

        <!-- navbar -->
        <nav id="navbar">
            <a href="index.php" id="brand">ReDesign Home Staging</a>

            <ul id="nav-links">
                <li><a href="../services.html">Services</a></li>
                <li><a href="about.php">About</a></li>
                <li><a href="../consult.html" id="nav-book">Book A Consultation</a></li>
            </ul>

            <!-- hamburger menu for mobile responsiveness -->
            <button id="nav-toggle" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </nav>

        <!-- home page content -->
        <main id="page-body">
            <div class="hero">
                <img src="../images/home-image-1.png" alt="Homepage Hero Image" class="hero-image">
                <div class="hero-overlay"></div>
                <div class="hero-content">
                    <h1><span class="italic gold">First Impressions</span></h1>
                    <h1>That Last</h1>
                    <p>
                        Staged homes sell 75% faster and for up to 20% more. Let us make your listing unforgettable
                    </p>
                    <!--button to scroll down to portfolio section-->
                    <div class="inline">
                        <a href="#portfolio" class="hero-cta">View Our Work</a>
                        <a href="../consult.html" class="hero-cta secondary">Free Consultation</a>
                    </div>
                </div>
            </div>

            <!-- portfolio section -->
            <section id="portfolio" class="portfolio">
                <div class="portfolio-header">
                    <div class="header-left">
                        <p><span class="gold">✦ FEATURED WORK</span></p>
                        <h2>Our <span class="italic gold"><br>Portfolio</span></h2>
                    </div>
                    <div class="header-right">
                        <p>Every project is a story of transformation. We transform homes buyers fall in love with before they step inside.</p>
                    </div>
                </div>

                <!-- Portfolio Grid -->
                <div class="portfolio-grid">
                    <?php foreach ($photos as $photo): ?>
                        <div class="portfolio-item">
                            <div class="portfolio-image-wrapper">
                                <img
                                    src="<?php echo htmlspecialchars('../' . $photo['file_path'], ENT_QUOTES); ?>"
                                    alt="<?php echo htmlspecialchars($photo['alt_text'] ?: ($photo['title'] ?: 'Portfolio image'), ENT_QUOTES); ?>"
                                >
                                <div class="portfolio-image-overlay"></div>

                                <?php if (!empty($photo['tag'])): ?>
                                    <span class="portfolio-tag">
                                        <?php echo htmlspecialchars($photo['tag'], ENT_QUOTES); ?>
                                    </span>
                                <?php endif; ?>

                                <div class="portfolio-caption">
                                    <?php if (!empty($photo['title'])): ?>
                                        <h3><?php echo htmlspecialchars($photo['title'], ENT_QUOTES); ?></h3>
                                    <?php endif; ?>

                                    <?php if (!empty($photo['location'])): ?>
                                        <p><?php echo htmlspecialchars($photo['location'], ENT_QUOTES); ?></p>
                                    <?php elseif (!empty($photo['subtitle'])): ?>
                                        <p><?php echo htmlspecialchars($photo['subtitle'], ENT_QUOTES); ?></p>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </section>

            <!-- transformation section-->
            <section id="transformation" class="transformation">
                <div class="transformation-inner">
                    <!-- Before/After Slider (left column) -->
                    <div class="transformation-slider-wrapper">
                        <div class="transformation-slider" id="transformation-slider">
                            <!-- After Image -->
                            <img 
                                src="../images/rdhs-after-pic-1.png" 
                                alt="After" 
                                class="transformation-img transformation-img-before">

                            <!-- Before Image -->
                            <div class="transformation-after-wrapper" id="after-clip" style="width: 50%;">
                                <img 
                                    src="../images/rdhs-before-image-1.png" 
                                    alt="Before" 
                                    class="transformation-img transformation-img-after">
                            </div>

                            <!-- Pills -->
                            <span class="transformation-pill transformation-pill-before">Before</span>
                            <span class="transformation-pill transformation-pill-after">After</span>

                            <!-- Slider Handle -->
                            <div class="transformation-handle" id="slider-handle" role="slider" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" tabindex="0">
                                <span class="transformation-handle-icon">&#8596;</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Content (right column) -->
                    <div class="transformation-content">
                        <p class="transformation-label"><span class="gold">✦ TRANSFORMATION</span></p>
                        <h2>See the <span class="italic gold">Difference</span></h2>
                        <p class="transformation-subtitle">Drag the slider to reveal the impact of our professional staging.</p>
                        <ul class="transformation-facts">
                            <li class="transformation-fact">
                                <span class="transformation-fact-value">75%</span>
                                <span class="transformation-fact-label">Faster sales than unstaged homes</span>
                            </li>
                            <li class="transformation-fact">
                                <span class="transformation-fact-value">+20%</span>
                                <span class="transformation-fact-label">Average increase in final sale price</span>
                            </li>
                            <li class="transformation-fact">
                                <span class="transformation-fact-value">12.3 Days</span>
                                <span class="transformation-fact-label">From listing to final sale date</span>
                            </li>
                            <li class="transformation-fact">
                                <span class="transformation-fact-value">15+</span>
                                <span class="transformation-fact-label">Successful transformations since 2019</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- testimonials section -->
            <section id="testimonials" class="testimonials">
                <div class="testimonials-header">
                    <div class="testimonials-header-left">
                        <p><span class="gold">✦ TESTIMONIALS</span></p>
                        <h2>What Our <span class="italic gold">Clients</span> Say</h2>
                    </div>
                    <div class="testimonials-header-right">
                        <button class="testimonials-nav-prev" type="button" aria-label="Previous testimonial">&#65513;</button>
                        <button class="testimonials-nav-next" type="button" aria-label="Next testimonial">&#65515;</button>
                    </div>
                </div>

                <!-- cards filled from database -->
                <div class="testimonials-cards">
                    <?php foreach ($testimonials as $t): ?>
                        <div class="testimonial-card">
                            <p class="stars">
                                <span class="gold">
                                    <?php
                                    $rating = (int)($t['rating'] ?? 5);
                                    echo str_repeat('★', max(1, min(5, $rating)));
                                    ?>
                                </span>
                            </p>

                            <p class="testimonial-text">
                                “<?php echo htmlspecialchars($t['quote'], ENT_QUOTES); ?>”
                            </p>

                            <div class="testimonial-author">
                                <div class="testimonial-author-initials">
                                    <p>
                                        <?php
                                        $initials = $t['author_initials'];
                                        if (!$initials && $t['author_name']) {
                                            $parts = preg_split('/\s+/', trim($t['author_name']));
                                            $first = $parts[0] ?? '';
                                            $last  = $parts[count($parts)-1] ?? '';
                                            $initials = strtoupper(mb_substr($first, 0, 1) . mb_substr($last, 0, 1));
                                        }
                                        echo htmlspecialchars($initials ?: '??', ENT_QUOTES);
                                        ?>
                                    </p>
                                </div>
                                <div class="testimonial-author-name">
                                    <p class="testimonial-author-name-text">
                                        <?php echo htmlspecialchars($t['author_name'], ENT_QUOTES); ?>
                                    </p>
                                    <?php if (!empty($t['author_location'])): ?>
                                        <p class="testimonial-author-location">
                                            <?php echo htmlspecialchars($t['author_location'], ENT_QUOTES); ?>
                                        </p>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
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
                            <li><a href="#portfolio">Portfolio</a></li>
                            <li><a href="about.php">About Us</a></li>
                            <li><a href="#testimonials">Testimonials</a></li>
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
        <script src="../js/transformation-slider.js"></script>
        <script src="../js/testimonials.js"></script>
    </body>
</html>