#!/usr/bin/env python3
"""
CarNation Elite — Page Generator
Generates /vehicles/ and /services/ pages + specials.html from embedded data.
Run: python3 generate-pages.py
"""

import os, json
from datetime import date

BASE_URL = "https://carnationelite.com"
PHONE = "+1 (214) 597 4922"
PHONE_HREF = "tel:+12145974922"
EMAIL = "service@carnationelite.com"
ADDRESS = "13610 Floyd Circle, Dallas, Texas"
CALENDLY = "https://calendly.com/carnationelite/schedule-your-appointment"
WARRANTY = "12-month / 12,000-mile"
TODAY = date.today().isoformat()
ROOT = os.path.dirname(os.path.abspath(__file__))

# ── DATA ─────────────────────────────────────────────────────────────────────

MAKES = [
    {"slug": "toyota",      "name": "Toyota",       "models": "Camry, Corolla, RAV4, Tacoma, Tundra, Highlander, 4Runner"},
    {"slug": "honda",       "name": "Honda",        "models": "Civic, Accord, CR-V, Pilot, Odyssey, Ridgeline"},
    {"slug": "ford",        "name": "Ford",         "models": "F-150, Explorer, Escape, Mustang, Edge, Bronco, Expedition"},
    {"slug": "chevrolet",   "name": "Chevrolet",    "models": "Silverado, Equinox, Malibu, Traverse, Colorado, Tahoe, Suburban"},
    {"slug": "nissan",      "name": "Nissan",       "models": "Altima, Rogue, Sentra, Frontier, Pathfinder, Maxima, Armada"},
    {"slug": "jeep",        "name": "Jeep",         "models": "Wrangler, Grand Cherokee, Cherokee, Compass, Gladiator"},
    {"slug": "ram",         "name": "Ram",          "models": "1500, 2500, 3500, ProMaster, Dakota"},
    {"slug": "gmc",         "name": "GMC",          "models": "Sierra, Terrain, Acadia, Yukon, Canyon, Envoy"},
    {"slug": "subaru",      "name": "Subaru",       "models": "Outback, Forester, Crosstrek, Impreza, Legacy, Ascent, WRX"},
    {"slug": "hyundai",     "name": "Hyundai",      "models": "Elantra, Tucson, Santa Fe, Sonata, Palisade, Kona"},
    {"slug": "kia",         "name": "Kia",          "models": "Sorento, Sportage, Telluride, Soul, Forte, Stinger"},
    {"slug": "bmw",         "name": "BMW",          "models": "3 Series, 5 Series, X3, X5, 7 Series, M3, M5"},
    {"slug": "mercedes-benz","name": "Mercedes-Benz","models": "C-Class, E-Class, GLE, GLC, S-Class, CLA, A-Class"},
    {"slug": "audi",        "name": "Audi",         "models": "A4, A6, Q5, Q7, Q3, A3, TT, e-tron"},
    {"slug": "lexus",       "name": "Lexus",        "models": "RX, ES, IS, GX, NX, LS, UX, LC"},
    {"slug": "volkswagen",  "name": "Volkswagen",   "models": "Jetta, Passat, Tiguan, Atlas, Golf, ID.4"},
    {"slug": "dodge",       "name": "Dodge",        "models": "Charger, Challenger, Durango, Journey, Grand Caravan"},
    {"slug": "mazda",       "name": "Mazda",        "models": "CX-5, Mazda3, CX-9, MX-5 Miata, CX-30, Mazda6"},
    {"slug": "acura",       "name": "Acura",        "models": "MDX, RDX, TLX, ILX, NSX, Integra"},
    {"slug": "infiniti",    "name": "Infiniti",     "models": "QX60, QX50, Q50, QX80, QX55, Q60"},
]

SERVICES = [
    {
        "slug": "oil-change-dallas",
        "name": "Oil Change",
        "headline": "Oil Change Service in Dallas, TX",
        "desc": "Conventional, synthetic blend, or full synthetic — matched to your vehicle's spec.",
        "body": """<p>Oil is the lifeblood of your engine. Skipping changes or running the wrong viscosity shortens engine life fast — especially in Dallas summers where oil temps run higher than the bottle assumes. At CarNation Elite on Floyd Circle, we match oil type and weight to your exact vehicle spec, inspect every other fluid while we're in there, and reset your maintenance indicator before you leave.</p>
<p>We service all makes and models. Most oil changes are done in under 45 minutes with no appointment required, though booking ahead locks your time slot.</p>
<h3>What's Included</h3>
<ul><li>Drain &amp; replace engine oil with manufacturer-specified grade</li><li>New OEM-spec oil filter</li><li>Top-off washer fluid, coolant, and power steering fluid</li><li>Tire pressure check and visual brake inspection</li><li>Maintenance reminder reset</li></ul>"""
    },
    {
        "slug": "brake-repair-service-dallas",
        "name": "Brake Repair",
        "headline": "Brake Repair &amp; Replacement in Dallas, TX",
        "desc": "Brake pads, rotors, calipers, ABS diagnosis — fixed right the first time.",
        "body": """<p>Dallas stop-and-go traffic on I-635, LBJ, and Central Expressway puts serious wear on brake pads and rotors. Add summer heat and you've got a city where brake maintenance isn't optional. CarNation Elite measures pad thickness and rotor depth before recommending anything — you see the numbers, you approve the work, we fix only what actually needs fixing.</p>
<h3>Brake Services We Perform</h3>
<ul><li>Brake pad replacement (all axles)</li><li>Rotor resurfacing or replacement</li><li>Caliper replacement and brake fluid flush</li><li>ABS module diagnosis and repair</li><li>Emergency brake adjustment</li><li>Brake line inspection and replacement</li></ul>"""
    },
    {
        "slug": "engine-diagnostics-repair-dallas",
        "name": "Engine Diagnostics & Repair",
        "headline": "Engine Diagnostics &amp; Repair in Dallas, TX",
        "desc": "Check engine light on? We scan every module and give you a clear repair plan.",
        "body": """<p>A check engine light covers dozens of possible faults across multiple modules. We don't just pull codes — we trace the fault to the actual broken component using live data, freeze frame, and oscilloscope work where needed. You get a prioritized repair plan in plain English before we touch a wrench.</p>
<h3>Engine Services</h3>
<ul><li>Full OBD-II and module scan (not just powertrain)</li><li>Timing chain and belt service</li><li>Head gasket diagnosis and repair</li><li>Fuel system cleaning and injector service</li><li>Turbocharger and supercharger repair</li><li>Engine mounts and seals</li></ul>"""
    },
    {
        "slug": "ac-heat-repair-dallas",
        "name": "AC & Heat Repair",
        "headline": "AC &amp; Heat Repair in Dallas, TX",
        "desc": "Dallas summers demand a working AC. We diagnose, recharge, and repair same day.",
        "body": """<p>A failing AC in a Dallas summer isn't a comfort issue — it's a safety issue. Cabin temps in a parked car exceed 140°F on a July afternoon. CarNation Elite diagnoses the full AC system: compressor, condenser, evaporator, expansion valve, and refrigerant charge. Most AC recharges and simple leaks are same-day.</p>
<h3>AC &amp; Heat Services</h3>
<ul><li>Refrigerant recharge (R-134a / R-1234yf)</li><li>Leak detection and repair</li><li>Compressor, condenser, and evaporator replacement</li><li>Cabin air filter replacement</li><li>Heater core and blower motor service</li><li>Climate control diagnosis</li></ul>"""
    },
    {
        "slug": "transmission-repair-dallas",
        "name": "Transmission Repair",
        "headline": "Transmission Repair in Dallas, TX",
        "desc": "Automatic and manual transmission service, diagnosis, and rebuild.",
        "body": """<p>Transmission repairs are among the most expensive on any vehicle — which makes getting the diagnosis right the first time critical. We verify transmission faults with live data before recommending any rebuild or replacement. Fluid services, solenoid replacements, and valve body work often resolve issues that look like full failures.</p>
<h3>Transmission Services</h3>
<ul><li>Transmission fluid exchange (automatic and CVT)</li><li>Torque converter replacement</li><li>Solenoid and valve body repair</li><li>Manual clutch replacement</li><li>Transfer case service (4WD/AWD)</li><li>Full rebuild and remanufactured unit installation</li></ul>"""
    },
    {
        "slug": "electrical-repair-dallas",
        "name": "Electrical Repair",
        "headline": "Auto Electrical Repair in Dallas, TX",
        "desc": "Wiring, modules, sensors, and charging system — diagnosed and fixed fast.",
        "body": """<p>Modern vehicles have more computing power than a 1990s spacecraft. Electrical faults are rarely as simple as a bad sensor — they involve wiring harnesses, grounds, control modules, and CAN bus communication. Our technicians use factory-level diagnostic software and oscilloscopes to trace electrical faults to the source rather than guessing with part swaps.</p>
<h3>Electrical Services</h3>
<ul><li>Battery, alternator, and starter diagnosis and replacement</li><li>Wiring harness repair and splice work</li><li>Module coding and programming</li><li>Sensor replacement (O2, MAF, crankshaft, camshaft)</li><li>Lighting and accessory circuits</li><li>Power window, door lock, and sunroof repair</li></ul>"""
    },
    {
        "slug": "steering-suspension-repair-dallas",
        "name": "Steering & Suspension",
        "headline": "Steering &amp; Suspension Repair in Dallas, TX",
        "desc": "Shocks, struts, ball joints, and alignment — ride and handling restored.",
        "body": """<p>Dallas roads and Texas highways put real stress on suspension components. Worn shocks and struts don't just affect ride comfort — they extend stopping distance and reduce tire contact with the road. We inspect the full suspension system and show you worn components before recommending replacements.</p>
<h3>Steering &amp; Suspension Services</h3>
<ul><li>Shock and strut replacement</li><li>Ball joint, tie rod, and control arm service</li><li>Wheel alignment (2-wheel and 4-wheel)</li><li>Power steering fluid flush and pump repair</li><li>Rack and pinion replacement</li><li>Sway bar links and bushings</li></ul>"""
    },
    {
        "slug": "battery-replacement-dallas",
        "name": "Battery Replacement",
        "headline": "Car Battery Replacement in Dallas, TX",
        "desc": "Fast battery testing and replacement — most vehicles done in under 30 minutes.",
        "body": """<p>Dallas heat is brutal on car batteries. The average battery lasts 3–5 years nationally; in North Texas heat, many fail in 2–3. We test your battery's cold cranking amps and state of charge before recommending replacement — so you're not buying a battery you don't need. We also test the alternator and charging system to make sure a failing alternator isn't killing the new battery.</p>
<h3>Battery Services</h3>
<ul><li>Load test and state-of-health check</li><li>Battery replacement (all group sizes)</li><li>Alternator and charging system test</li><li>Terminal cleaning and cable inspection</li><li>AGM and stop-start battery systems</li></ul>"""
    },
    {
        "slug": "vehicle-inspection-dallas",
        "name": "Vehicle Inspection",
        "headline": "Vehicle Inspection in Dallas, TX",
        "desc": "Pre-purchase inspections, state inspections, and full multi-point checks.",
        "body": """<p>Before you buy a used car in Dallas — from a dealer or a private seller — get an independent inspection. We've helped hundreds of Dallas buyers avoid expensive mistakes by catching hidden faults before money changes hands. We also perform thorough multi-point inspections to give you a clear picture of your current vehicle's health.</p>
<h3>Inspection Services</h3>
<ul><li>Pre-purchase used vehicle inspection</li><li>Texas state safety inspection</li><li>50-point multi-point inspection</li><li>Fluid condition analysis</li><li>Tire depth and condition report</li><li>Undercarriage and frame inspection</li></ul>"""
    },
    {
        "slug": "fleet-services-dallas",
        "name": "Fleet Services",
        "headline": "Fleet Services in Dallas, TX",
        "desc": "Preventive maintenance programs for Dallas businesses with 2 or more vehicles.",
        "body": """<p>Downtime costs money. CarNation Elite's fleet maintenance program keeps your vans, trucks, and company cars on the road with scheduled service intervals, priority scheduling, and consolidated billing. We work with small businesses across North Dallas, Richardson, and Plano — from two-vehicle operations to 30-unit fleets.</p>
<h3>Fleet Program Includes</h3>
<ul><li>Dedicated fleet service advisor</li><li>Scheduled preventive maintenance (oil, filters, brakes, tires)</li><li>Priority scheduling — no waiting behind retail customers</li><li>Consolidated monthly invoicing</li><li>Vehicle inspection reports per unit</li><li>24/7 roadside assistance for fleet vehicles</li></ul>"""
    },
    {
        "slug": "roadside-assistance-dallas",
        "name": "24/7 Roadside Assistance",
        "headline": "24/7 Roadside Assistance in Dallas, TX",
        "desc": "Flat tire, dead battery, lockout, or tow — we respond day and night.",
        "body": """<p>CarNation Elite offers 24/7 roadside assistance across Dallas, Richardson, Plano, Garland, and surrounding areas. Whether you're stranded on I-635 at 2am or stuck in a parking lot on a Sunday, call us and we'll dispatch help. Unlike Taylor Auto Repair, which closes at 5pm weekdays and shuts down on weekends — we're available whenever you need us.</p>
<h3>Roadside Services</h3>
<ul><li>Jump start and battery service</li><li>Flat tire change or inflation</li><li>Fuel delivery</li><li>Lockout service</li><li>Emergency towing to our shop or your preferred location</li><li>On-site minor repairs</li></ul>"""
    },
    {
        "slug": "hybrid-ev-repair-dallas",
        "name": "Hybrid & EV Repair",
        "headline": "Hybrid &amp; EV Repair in Dallas, TX",
        "desc": "High-voltage system diagnostics, battery health, and hybrid service for all makes.",
        "body": """<p>Hybrid and electric vehicles need technicians trained in high-voltage systems — not just standard combustion mechanics. CarNation Elite services Toyota, Honda, Ford, Chevrolet, and other hybrid platforms, as well as plug-in hybrids and EVs. We handle everything from routine hybrid battery health checks to charging system diagnosis and regenerative brake calibration.</p>
<h3>Hybrid &amp; EV Services</h3>
<ul><li>High-voltage battery health check and cell balancing</li><li>12V auxiliary battery service</li><li>Charging system diagnosis and repair</li><li>Regenerative brake system service</li><li>Inverter and DC-DC converter diagnosis</li><li>Toyota Hybrid (Prius, RAV4 Hybrid, Camry Hybrid, Highlander Hybrid)</li><li>Ford Escape Hybrid, F-150 Hybrid, Maverick Hybrid</li><li>Chevrolet Volt, Bolt, and Malibu Hybrid</li></ul>"""
    },
]

SPECIALS = [
    {"title": "Oil Change Special", "price": "$49.99", "detail": "Full synthetic oil change up to 5 qts + new filter. Most cars. Expires end of month.", "badge": "Most Popular"},
    {"title": "Free Multi-Point Inspection", "price": "FREE", "detail": "50-point inspection with any service. Includes brake check, fluid levels, tire depth, and undercarriage report.", "badge": "No Purchase Required"},
    {"title": "Brake Pad Special", "price": "$30 OFF", "detail": "$30 off front or rear brake pad replacement. Includes rotor inspection. Cannot combine with other offers.", "badge": "Limited Time"},
    {"title": "AC Recharge", "price": "$89.99", "detail": "R-134a or R-1234yf recharge + leak check. Most vehicles. Beat the Dallas heat.", "badge": "Summer Deal"},
    {"title": "New Customer Discount", "price": "10% OFF", "detail": "First-time CarNation Elite customers save 10% on any repair over $100. Mention this offer when booking.", "badge": "First Visit"},
    {"title": "Free Second Opinion", "price": "FREE", "detail": "Got a high dealer quote? Bring it in. We'll re-scan your vehicle and tell you whether the diagnosis holds up. No charge.", "badge": "Always Available"},
]

# ── TEMPLATE PARTS ────────────────────────────────────────────────────────────

def head(title, desc, keywords, canonical, depth=1):
    rel = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3HL7JENB2E"></script>
    <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-3HL7JENB2E');</script>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
    <title>{title}</title>
    <meta name="description" content="{desc}"/>
    <meta name="keywords" content="{keywords}"/>
    <meta name="author" content="CarNation Elite Auto Repair &amp; Sales"/>
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"/>
    <meta name="geo.region" content="US-TX"/>
    <meta name="geo.placename" content="Dallas, Texas"/>
    <link rel="canonical" href="{canonical}"/>
    <meta property="og:type" content="website"/>
    <meta property="og:title" content="{title}"/>
    <meta property="og:description" content="{desc}"/>
    <meta property="og:url" content="{canonical}"/>
    <meta property="og:site_name" content="CarNation Elite Auto Repair &amp; Sales"/>
    <meta property="og:image" content="{BASE_URL}/assets/images/resources/logo-2.png"/>
    <meta name="twitter:card" content="summary_large_image"/>
    <meta name="twitter:title" content="{title}"/>
    <meta name="twitter:description" content="{desc}"/>
    <meta name="twitter:image" content="{BASE_URL}/assets/images/resources/logo-2.png"/>
    <link rel="icon" type="image/png" sizes="32x32" href="{rel}assets/images/favicons/favicon-32x32.png"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
    <link rel="preconnect" href="https://fonts.googleapis.com/">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{rel}assets/css/bootstrap.min.css"/>
    <link rel="stylesheet" href="{rel}assets/css/style.css"/>
    <link rel="stylesheet" href="{rel}assets/css/responsive.css"/>
    <link type="text/plain" rel="me" href="{BASE_URL}/llms.txt"/>
    <link type="text/plain" rel="me" href="{BASE_URL}/llms-full.txt"/>
    <style>
        .page-hero{{background:linear-gradient(135deg,#0a0a0a 0%,#1a1a2e 100%);padding:80px 0 60px;text-align:center;color:#fff;}}
        .page-hero h1{{font-size:clamp(1.8rem,4vw,2.8rem);font-weight:700;margin-bottom:12px;}}
        .page-hero p{{font-size:1.1rem;opacity:.85;max-width:620px;margin:0 auto 28px;}}
        .btn-hero{{display:inline-block;background:#e8272a;color:#fff;padding:14px 32px;border-radius:6px;font-weight:600;text-decoration:none;margin:0 8px 8px;}}
        .btn-hero-outline{{display:inline-block;border:2px solid #fff;color:#fff;padding:12px 30px;border-radius:6px;font-weight:600;text-decoration:none;margin:0 8px 8px;}}
        .trust-bar{{background:#e8272a;padding:18px 0;text-align:center;}}
        .trust-bar span{{color:#fff;font-weight:600;margin:0 20px;font-size:.95rem;}}
        .content-section{{padding:70px 0;}}
        .content-section h2{{font-size:clamp(1.5rem,3vw,2rem);font-weight:700;margin-bottom:20px;color:#1a1a2e;}}
        .content-section h3{{font-size:1.2rem;font-weight:600;margin:28px 0 12px;color:#1a1a2e;}}
        .content-section p{{color:#555;line-height:1.8;margin-bottom:16px;}}
        .content-section ul{{color:#555;line-height:1.9;padding-left:20px;}}
        .cta-box{{background:#1a1a2e;border-radius:12px;padding:48px 40px;text-align:center;color:#fff;margin:48px 0;}}
        .cta-box h2{{color:#fff;margin-bottom:12px;}}
        .cta-box p{{opacity:.85;margin-bottom:24px;}}
        .warranty-badge{{display:inline-block;background:#fff;color:#1a1a2e;border-radius:8px;padding:10px 20px;font-weight:700;font-size:.9rem;margin-bottom:20px;}}
        .makes-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin:32px 0;}}
        .make-card{{background:#f8f8f8;border-radius:8px;padding:16px;text-align:center;text-decoration:none;color:#1a1a2e;font-weight:600;font-size:.9rem;border:1px solid #eee;transition:all .2s;}}
        .make-card:hover{{background:#e8272a;color:#fff;border-color:#e8272a;}}
        .faq-item{{border-bottom:1px solid #eee;padding:20px 0;}}
        .faq-item h4{{font-size:1rem;font-weight:600;color:#1a1a2e;margin-bottom:8px;}}
        .faq-item p{{color:#555;margin:0;line-height:1.7;}}
    </style>
</head>"""

SCHEMA_BUSINESS = """{
    "@context": "https://schema.org",
    "@type": ["LocalBusiness","AutoRepair"],
    "@id": "https://carnationelite.com/#business",
    "name": "CarNation Elite Auto Repair & Sales",
    "url": "https://carnationelite.com",
    "telephone": "+1-214-597-4922",
    "email": "service@carnationelite.com",
    "image": "https://carnationelite.com/assets/images/resources/logo-2.png",
    "address": {"@type":"PostalAddress","streetAddress":"13610 Floyd Circle","addressLocality":"Dallas","addressRegion":"TX","postalCode":"75243","addressCountry":"US"},
    "geo": {"@type":"GeoCoordinates","latitude":32.9029,"longitude":-96.7044},
    "openingHoursSpecification": [{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"08:00","closes":"18:00"}],
    "priceRange": "$$",
    "aggregateRating": {"@type":"AggregateRating","ratingValue":"4.8","reviewCount":"77","bestRating":"5"}
}"""

def navbar(depth=1):
    rel = "../" * depth
    return f"""<header class="main-header-two">
    <div class="main-menu-two__top">
        <div class="main-menu-two__top-inner">
            <ul class="list-unstyled main-menu-two__contact-list">
                <li><div class="icon"><i class="icon-phone-call"></i></div><div class="text"><p><a href="{PHONE_HREF}">{PHONE}</a></p></div></li>
                <li><div class="icon"><i class="icon-email"></i></div><div class="text"><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div></li>
                <li><div class="icon"><i class="icon-pin"></i></div><div class="text"><p>{ADDRESS}</p></div></li>
            </ul>
            <p class="main-menu-two__top-welcome-text">Welcome to CarNation Elite Auto Repair</p>
            <div class="main-menu-two__top-right">
                <div class="main-menu-two__top-time">
                    <span class="fas fa-clock"></span>
                    <p class="main-menu-two__top-text">Mon - Sat: 08:00 - 18:00 &nbsp;|&nbsp; 24/7 Roadside</p>
                </div>
            </div>
        </div>
    </div>
    <nav class="main-menu main-menu-two">
        <div class="main-menu-two__wrapper">
            <div class="main-menu-two__wrapper-inner">
                <div class="main-menu-two__left">
                    <div class="main-menu-two__logo">
                        <a href="{rel}index.html"><img src="{rel}assets/images/resources/logo-2.png" alt="CarNation Elite logo" style="height:80px;width:80px;" loading="eager"></a>
                    </div>
                </div>
                <div class="main-menu-two__main-menu-box">
                    <a href="javascript:void(0);" class="mobile-nav__toggler"><i class="fa fa-bars"></i></a>
                    <ul class="main-menu__list">
                        <li><a href="{rel}index.html">Home</a></li>
                        <li><a href="{rel}about.html">About Us</a></li>
                        <li><a href="{rel}services.html">Services</a></li>
                        <li><a href="{rel}carsales.html">Car Sales</a></li>
                        <li><a href="{rel}contact.html">Contact</a></li>
                    </ul>
                </div>
                <div class="main-menu-two__right">
                    <div class="main-menu-two__btn-box">
                        <a href="{CALENDLY}" class="thm-btn" target="_blank">Book Now <span><i class="fa fa-calendar"></i></span></a>
                    </div>
                </div>
            </div>
        </div>
    </nav>
</header>"""

def footer(depth=1):
    rel = "../" * depth
    return f"""<footer class="site-footer-two">
    <div class="container">
        <div class="site-footer-two__top">
            <div class="row">
                <div class="col-xl-4 col-lg-6 col-md-6">
                    <div class="footer-widget-two__column footer-widget-two__about">
                        <div class="footer-widget-two__logo">
                            <a href="{rel}index.html"><img src="{rel}assets/images/resources/logo-2.png" alt="CarNation Elite logo" style="height:80px;width:80px;"></a>
                        </div>
                        <p class="footer-widget-two__about-text">CarNation Elite Auto Repair &amp; Sales — Dallas, TX. Expert auto repair, 24/7 roadside assistance, fleet services, and quality used cars. Serving North Dallas, Richardson, Plano, and Addison.</p>
                        <div class="site-footer-two__social">
                            <a target="_blank" href="https://www.facebook.com/carnationelite"><i class="icon-facebook-app-symbol"></i></a>
                            <a target="_blank" href="https://www.instagram.com/carnation_elite/"><i class="icon-instagram"></i></a>
                            <a target="_blank" href="https://twitter.com/carnationelite"><i class="fa-brands fa-x-twitter"></i></a>
                        </div>
                    </div>
                </div>
                <div class="col-xl-2 col-lg-6 col-md-6">
                    <div class="footer-widget-two__column footer-widget-two__usefull-link">
                        <div class="footer-widget-two__title-box"><h3 class="footer-widget-two__title">Quick Links</h3></div>
                        <ul class="footer-widget-two__link list-unstyled">
                            <li><a href="{rel}index.html">Home</a></li>
                            <li><a href="{rel}about.html">About Us</a></li>
                            <li><a href="{rel}services.html">Services</a></li>
                            <li><a href="{rel}specials.html">Specials</a></li>
                            <li><a href="{rel}carsales.html">Car Sales</a></li>
                            <li><a href="{rel}contact.html">Contact</a></li>
                        </ul>
                    </div>
                </div>
                <div class="col-xl-3 col-lg-6 col-md-6">
                    <div class="footer-widget-two__column footer-widget-two__services">
                        <div class="footer-widget-two__title-box"><h3 class="footer-widget-two__title">Our Services</h3></div>
                        <ul class="footer-widget-two__link list-unstyled">
                            <li><a href="{rel}services/oil-change-dallas.html">Oil Change</a></li>
                            <li><a href="{rel}services/brake-repair-service-dallas.html">Brake Repair</a></li>
                            <li><a href="{rel}services/ac-heat-repair-dallas.html">AC &amp; Heat Repair</a></li>
                            <li><a href="{rel}services/hybrid-ev-repair-dallas.html">Hybrid &amp; EV Repair</a></li>
                            <li><a href="{rel}services/roadside-assistance-dallas.html">24/7 Roadside</a></li>
                            <li><a href="{rel}services/fleet-services-dallas.html">Fleet Services</a></li>
                        </ul>
                    </div>
                </div>
                <div class="col-xl-3 col-lg-6 col-md-6">
                    <div class="footer-widget-two__column footer-widget-two__newsletter">
                        <div class="footer-widget-two__title-box"><h3 class="footer-widget-two__newsletter-title">Contact Us</h3></div>
                        <ul class="footer-widget-two__contact list-unstyled">
                            <li><div class="icon"><span class="icon-phone-call"></span></div><div class="content"><h5>Phone</h5><p><a href="{PHONE_HREF}">(214) 597-4922</a></p></div></li>
                            <li><div class="icon"><span class="icon-location"></span></div><div class="content"><h5>Location</h5><p>13610 Floyd Circle, Dallas, TX 75243</p></div></li>
                            <li><div class="icon"><span class="icon-email"></span></div><div class="content"><h5>Email</h5><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="site-footer-two__bottom">
        <div class="container">
            <div class="site-footer-two__bottom-inner">
                <p class="site-footer-two__bottom-text">© Copyright 2026 by CarNation Elite Auto Repair &amp; Sales. All Rights Reserved.</p>
            </div>
        </div>
    </div>
</footer>"""

MAKES_LINKS_HTML = "\n".join(
    f'<a class="make-card" href="/vehicles/{m["slug"]}-repair-dallas.html">{m["name"]}</a>'
    for m in MAKES
)

# ── PAGE BUILDERS ─────────────────────────────────────────────────────────────

def build_vehicle_page(make):
    slug = make["slug"]
    name = make["name"]
    models = make["models"]
    filename = f"{slug}-repair-dallas.html"
    canonical = f"{BASE_URL}/vehicles/{filename}"
    title = f"{name} Repair Dallas TX | CarNation Elite Auto Repair"
    desc = f"Expert {name} repair in Dallas, TX. CarNation Elite services {models} and all {name} models. Lower than dealer pricing, 24/7 roadside, {WARRANTY} warranty. Call (214) 597-4922."
    keywords = f"{name.lower()} repair Dallas, {name.lower()} mechanic Dallas TX, {name.lower()} service Dallas, {name.lower()} auto repair near me, Dallas {name.lower()} shop"

    schema = f"""{{
    "@context": "https://schema.org",
    "@type": ["LocalBusiness","AutoRepair"],
    "@id": "{BASE_URL}/#business",
    "name": "CarNation Elite Auto Repair & Sales",
    "url": "{BASE_URL}",
    "telephone": "+1-214-597-4922",
    "email": "service@carnationelite.com",
    "address": {{"@type":"PostalAddress","streetAddress":"13610 Floyd Circle","addressLocality":"Dallas","addressRegion":"TX","postalCode":"75243","addressCountry":"US"}},
    "geo": {{"@type":"GeoCoordinates","latitude":32.9029,"longitude":-96.7044}},
    "priceRange": "$$",
    "openingHoursSpecification": [{{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"08:00","closes":"18:00"}}],
    "serviceType": ["{name} Repair","Oil Change","Brake Repair","Engine Diagnostics","AC Repair","Transmission Repair"],
    "aggregateRating": {{"@type":"AggregateRating","ratingValue":"4.8","reviewCount":"77","bestRating":"5"}}
}}"""

    content = f"""
    <div class="page-hero">
        <div class="container">
            <h1>{name} Repair in Dallas, TX</h1>
            <p>Expert {name} service for {models}. Dealer-grade diagnostics at independent shop prices — with 24/7 roadside and a {WARRANTY} warranty on every repair.</p>
            <a href="{CALENDLY}" class="btn-hero" target="_blank">Book Appointment</a>
            <a href="{PHONE_HREF}" class="btn-hero-outline">Call (214) 597-4922</a>
        </div>
    </div>

    <div class="trust-bar">
        <span>✓ {WARRANTY} Warranty</span>
        <span>✓ Lower Than Dealer Pricing</span>
        <span>✓ 24/7 Roadside Assistance</span>
        <span>✓ Free Second Opinion</span>
    </div>

    <section class="content-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8">
                    <h2>{name} Repair &amp; Maintenance — Floyd Circle, Dallas</h2>
                    <p>CarNation Elite has been servicing {name} vehicles for Dallas-area drivers for over 15 years. We work on the full {name} lineup — {models} — from routine oil changes and brake jobs to complex engine diagnostics and transmission repair. Every repair comes backed by our {WARRANTY} warranty on parts and labor.</p>

                    <p>We're located at 13610 Floyd Circle in Northeast Dallas, minutes from Richardson, Lake Highlands, and Garland. Unlike the dealership, you won't wait a week for an appointment or sit in a waiting room for three hours. Most routine {name} services are same-day.</p>

                    <h3>Common {name} Services We Perform</h3>
                    <ul>
                        <li>Oil change (conventional, synthetic blend, or full synthetic — matched to {name} spec)</li>
                        <li>Brake pad and rotor replacement</li>
                        <li>Engine diagnostics and check engine light diagnosis</li>
                        <li>AC and heating system repair</li>
                        <li>Transmission fluid service and repair</li>
                        <li>Battery and alternator testing and replacement</li>
                        <li>Suspension, alignment, and steering repair</li>
                        <li>Timing belt/chain service</li>
                        <li>Coolant flush and radiator service</li>
                        <li>Pre-purchase {name} inspection</li>
                    </ul>

                    <h3>Why Dallas {name} Owners Choose CarNation Elite</h3>
                    <p><strong>Lower than dealer pricing.</strong> Dealership service departments carry high overhead. We pass those savings to you without cutting corners on parts or process. Bring us any dealer quote — we'll give you a straight comparison.</p>
                    <p><strong>Transparent estimates.</strong> You approve the work before we start. No surprise line items, no "while-we-were-in-there" additions you didn't authorize.</p>
                    <p><strong>24/7 availability.</strong> Our roadside assistance runs around the clock, seven days a week. If your {name} breaks down at midnight on a Friday, we've got you — not an answering machine.</p>

                    <div class="cta-box">
                        <div class="warranty-badge">✓ {WARRANTY} Warranty on All Repairs</div>
                        <h2>Ready to Book Your {name} Service?</h2>
                        <p>Online booking takes 60 seconds. Or call us and we'll get you in today.</p>
                        <a href="{CALENDLY}" class="btn-hero" target="_blank">Book Online</a>
                        <a href="{PHONE_HREF}" class="btn-hero-outline">Call (214) 597-4922</a>
                    </div>

                    <h3>Frequently Asked Questions — {name} Repair Dallas</h3>
                    <div class="faq-item">
                        <h4>How much does {name} repair cost in Dallas?</h4>
                        <p>Pricing depends on the model, year, and what needs fixing. Call us at (214) 597-4922 with your vehicle info and the issue — we'll quote diagnostic time upfront and won't add time without your approval. We're consistently 20–40% below dealer rates on most repairs.</p>
                    </div>
                    <div class="faq-item">
                        <h4>Will using an independent shop void my {name} warranty?</h4>
                        <p>No. The federal Magnuson-Moss Warranty Act protects your right to service your vehicle at any qualified independent shop without voiding the factory warranty, as long as the work is done correctly with quality parts. We document every service properly.</p>
                    </div>
                    <div class="faq-item">
                        <h4>How long does {name} service take?</h4>
                        <p>Routine services (oil change, brakes, battery) are typically same-day, often under 2 hours. Complex diagnostics or major repairs like timing chains or transmissions can take 1–3 days depending on parts availability. We give you a timeline before you approve.</p>
                    </div>
                    <div class="faq-item">
                        <h4>Do you offer a free second opinion on {name} repairs?</h4>
                        <p>Yes. If a dealer or another shop gave you a quote that felt high, bring it in. We'll inspect your {name} and tell you whether the diagnosis holds up — no charge, no pressure.</p>
                    </div>
                </div>

                <div class="col-lg-4">
                    <div style="background:#f8f8f8;border-radius:12px;padding:28px;margin-bottom:28px;">
                        <h3 style="margin-top:0;">Quick Contact</h3>
                        <p><strong>Phone:</strong> <a href="{PHONE_HREF}">(214) 597-4922</a></p>
                        <p><strong>Email:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
                        <p><strong>Address:</strong> 13610 Floyd Circle, Dallas, TX 75243</p>
                        <p><strong>Hours:</strong> Mon–Sat 8am–6pm<br>24/7 Roadside Assistance</p>
                        <a href="{CALENDLY}" class="btn-hero" style="display:block;text-align:center;margin-top:16px;" target="_blank">Book Appointment</a>
                    </div>
                    <div style="background:#1a1a2e;border-radius:12px;padding:28px;color:#fff;margin-bottom:28px;">
                        <h3 style="color:#fff;margin-top:0;">Current Specials</h3>
                        <p style="opacity:.85;">Oil change from <strong style="color:#e8272a;">$49.99</strong></p>
                        <p style="opacity:.85;">Free multi-point inspection with any service</p>
                        <p style="opacity:.85;">$30 off brake pad replacement</p>
                        <a href="/specials.html" style="color:#e8272a;font-weight:600;">View All Specials →</a>
                    </div>
                    <div style="background:#f8f8f8;border-radius:12px;padding:28px;">
                        <h3 style="margin-top:0;">Other Makes We Service</h3>
                        <div class="makes-grid" style="grid-template-columns:1fr 1fr;">
                            {MAKES_LINKS_HTML}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
"""

    html = f"""{head(title, desc, keywords, canonical, depth=1)}
<script type="application/ld+json">{schema}</script>
<body class="custom-cursor">
<div class="page-wrapper">
{navbar(depth=1)}
{content}
{footer(depth=1)}
</div>
</body>
</html>"""
    return filename, html


def build_service_page(svc):
    slug = svc["slug"]
    name = svc["name"]
    headline = svc["headline"]
    desc_short = svc["desc"]
    body = svc["body"]
    filename = f"{slug}.html"
    canonical = f"{BASE_URL}/services/{filename}"
    title = f"{name} Dallas TX | CarNation Elite Auto Repair"
    desc = f"{desc_short} CarNation Elite at Floyd Circle, Dallas. {WARRANTY} warranty, lower than dealer pricing, 24/7 roadside. Call (214) 597-4922."
    keywords = f"{name.lower()} Dallas, {name.lower()} Dallas TX, auto {name.lower()} near me, car {name.lower()} Dallas, Dallas auto repair"

    schema = f"""{{
    "@context": "https://schema.org",
    "@type": ["LocalBusiness","AutoRepair"],
    "@id": "{BASE_URL}/#business",
    "name": "CarNation Elite Auto Repair & Sales",
    "url": "{BASE_URL}",
    "telephone": "+1-214-597-4922",
    "email": "service@carnationelite.com",
    "address": {{"@type":"PostalAddress","streetAddress":"13610 Floyd Circle","addressLocality":"Dallas","addressRegion":"TX","postalCode":"75243","addressCountry":"US"}},
    "geo": {{"@type":"GeoCoordinates","latitude":32.9029,"longitude":-96.7044}},
    "priceRange": "$$",
    "openingHoursSpecification": [{{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"08:00","closes":"18:00"}}],
    "hasOfferCatalog": {{"@type":"OfferCatalog","name":"{name} Dallas","itemListElement":[{{"@type":"Offer","itemOffered":{{"@type":"Service","name":"{name}","areaServed":"Dallas, TX"}}}}]}},
    "aggregateRating": {{"@type":"AggregateRating","ratingValue":"4.8","reviewCount":"77","bestRating":"5"}}
}}"""

    content = f"""
    <div class="page-hero">
        <div class="container">
            <h1>{headline}</h1>
            <p>{desc_short} {WARRANTY} warranty on every repair. Open Mon–Sat + 24/7 roadside.</p>
            <a href="{CALENDLY}" class="btn-hero" target="_blank">Book Appointment</a>
            <a href="{PHONE_HREF}" class="btn-hero-outline">Call (214) 597-4922</a>
        </div>
    </div>

    <div class="trust-bar">
        <span>✓ {WARRANTY} Warranty</span>
        <span>✓ Lower Than Dealer Pricing</span>
        <span>✓ 24/7 Roadside Assistance</span>
        <span>✓ Free Second Opinion</span>
    </div>

    <section class="content-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8">
                    {body}
                    <div class="cta-box">
                        <div class="warranty-badge">✓ {WARRANTY} Warranty on Parts &amp; Labor</div>
                        <h2>Book Your {name} Appointment</h2>
                        <p>Online booking takes 60 seconds. Same-day service available most days.</p>
                        <a href="{CALENDLY}" class="btn-hero" target="_blank">Book Online</a>
                        <a href="{PHONE_HREF}" class="btn-hero-outline">Call (214) 597-4922</a>
                    </div>
                    <h3>Frequently Asked Questions</h3>
                    <div class="faq-item">
                        <h4>How much does {name.lower()} cost in Dallas?</h4>
                        <p>Pricing varies by vehicle make, model, and exact issue. Call us at (214) 597-4922 — we'll quote upfront with no surprises. We're typically 20–40% below dealer pricing on the same work.</p>
                    </div>
                    <div class="faq-item">
                        <h4>Is same-day service available?</h4>
                        <p>Yes, for most routine services. Complex repairs may require 1–3 days depending on parts. Book online or call to check current availability.</p>
                    </div>
                    <div class="faq-item">
                        <h4>What warranty do you offer?</h4>
                        <p>Every repair at CarNation Elite is backed by a {WARRANTY} warranty on parts and labor. If anything fails within that window, we fix it at no charge.</p>
                    </div>
                </div>

                <div class="col-lg-4">
                    <div style="background:#f8f8f8;border-radius:12px;padding:28px;margin-bottom:28px;">
                        <h3 style="margin-top:0;">Quick Contact</h3>
                        <p><strong>Phone:</strong> <a href="{PHONE_HREF}">(214) 597-4922</a></p>
                        <p><strong>Email:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
                        <p><strong>Address:</strong> 13610 Floyd Circle, Dallas, TX 75243</p>
                        <p><strong>Hours:</strong> Mon–Sat 8am–6pm<br>24/7 Roadside Assistance</p>
                        <a href="{CALENDLY}" class="btn-hero" style="display:block;text-align:center;margin-top:16px;" target="_blank">Book Appointment</a>
                    </div>
                    <div style="background:#1a1a2e;border-radius:12px;padding:28px;color:#fff;">
                        <h3 style="color:#fff;margin-top:0;">All Services</h3>
                        <ul style="list-style:none;padding:0;margin:0;">
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/oil-change-dallas.html" style="color:#ccc;text-decoration:none;">Oil Change</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/brake-repair-service-dallas.html" style="color:#ccc;text-decoration:none;">Brake Repair</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/engine-diagnostics-repair-dallas.html" style="color:#ccc;text-decoration:none;">Engine Diagnostics</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/ac-heat-repair-dallas.html" style="color:#ccc;text-decoration:none;">AC &amp; Heat Repair</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/transmission-repair-dallas.html" style="color:#ccc;text-decoration:none;">Transmission</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/electrical-repair-dallas.html" style="color:#ccc;text-decoration:none;">Electrical Repair</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/steering-suspension-repair-dallas.html" style="color:#ccc;text-decoration:none;">Steering &amp; Suspension</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/battery-replacement-dallas.html" style="color:#ccc;text-decoration:none;">Battery Replacement</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/vehicle-inspection-dallas.html" style="color:#ccc;text-decoration:none;">Vehicle Inspection</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/fleet-services-dallas.html" style="color:#ccc;text-decoration:none;">Fleet Services</a></li>
                            <li style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,.1);"><a href="/services/roadside-assistance-dallas.html" style="color:#ccc;text-decoration:none;">24/7 Roadside</a></li>
                            <li style="padding:6px 0;"><a href="/services/hybrid-ev-repair-dallas.html" style="color:#ccc;text-decoration:none;">Hybrid &amp; EV Repair</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </section>
"""
    html = f"""{head(title, desc, keywords, canonical, depth=1)}
<script type="application/ld+json">{schema}</script>
<body class="custom-cursor">
<div class="page-wrapper">
{navbar(depth=1)}
{content}
{footer(depth=1)}
</div>
</body>
</html>"""
    return filename, html


def build_specials_page():
    canonical = f"{BASE_URL}/specials.html"
    title = "Auto Repair Specials & Deals | CarNation Elite Dallas TX"
    desc = "Current auto repair specials and deals from CarNation Elite in Dallas, TX. Oil change from $49.99, free multi-point inspection, $30 off brakes, and more. Call (214) 597-4922."
    keywords = "auto repair deals Dallas, car repair specials Dallas TX, oil change coupon Dallas, brake repair discount Dallas, CarNation Elite specials"

    cards = ""
    for s in SPECIALS:
        badge = f'<span style="background:#e8272a;color:#fff;font-size:.75rem;font-weight:700;padding:4px 10px;border-radius:20px;display:inline-block;margin-bottom:12px;">{s["badge"]}</span>' if s.get("badge") else ""
        cards += f"""
        <div class="col-lg-4 col-md-6 mb-4">
            <div style="background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.08);padding:32px 28px;height:100%;display:flex;flex-direction:column;">
                {badge}
                <div style="font-size:2.4rem;font-weight:800;color:#e8272a;margin-bottom:8px;">{s["price"]}</div>
                <h3 style="font-size:1.15rem;font-weight:700;color:#1a1a2e;margin-bottom:12px;">{s["title"]}</h3>
                <p style="color:#666;line-height:1.7;flex:1;">{s["detail"]}</p>
                <a href="{CALENDLY}" class="btn-hero" style="text-align:center;margin-top:20px;display:block;" target="_blank">Book This Deal</a>
            </div>
        </div>"""

    content = f"""
    <div class="page-hero">
        <div class="container">
            <h1>Auto Repair Specials — Dallas, TX</h1>
            <p>Real deals on the services Dallas drivers need most. No hidden fees, no bait-and-switch. Book online or call to lock in your price.</p>
            <a href="{CALENDLY}" class="btn-hero" target="_blank">Book an Appointment</a>
            <a href="{PHONE_HREF}" class="btn-hero-outline">Call (214) 597-4922</a>
        </div>
    </div>

    <div class="trust-bar">
        <span>✓ {WARRANTY} Warranty</span>
        <span>✓ Lower Than Dealer Pricing</span>
        <span>✓ 24/7 Roadside Assistance</span>
        <span>✓ Free Second Opinion</span>
    </div>

    <section class="content-section">
        <div class="container">
            <div class="text-center mb-5">
                <h2>Current Offers</h2>
                <p style="color:#666;max-width:560px;margin:0 auto;">All offers valid at 13610 Floyd Circle, Dallas, TX 75243. Mention the offer when booking. Cannot combine unless stated.</p>
            </div>
            <div class="row">
                {cards}
            </div>
            <div class="cta-box mt-5">
                <div class="warranty-badge">✓ {WARRANTY} Warranty on Every Repair</div>
                <h2>Questions About a Special?</h2>
                <p>Call us and we'll walk you through pricing before you commit to anything.</p>
                <a href="{CALENDLY}" class="btn-hero" target="_blank">Book Online</a>
                <a href="{PHONE_HREF}" class="btn-hero-outline">Call (214) 597-4922</a>
            </div>
        </div>
    </section>
"""
    html = f"""{head(title, desc, keywords, canonical, depth=0)}
<script type="application/ld+json">{SCHEMA_BUSINESS}</script>
<body class="custom-cursor">
<div class="page-wrapper">
{navbar(depth=0)}
{content}
{footer(depth=0)}
</div>
</body>
</html>"""
    return "specials.html", html


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    vehicles_dir = os.path.join(ROOT, "vehicles")
    services_dir = os.path.join(ROOT, "services")
    os.makedirs(vehicles_dir, exist_ok=True)
    os.makedirs(services_dir, exist_ok=True)

    count = 0

    print("Generating vehicle pages...")
    for make in MAKES:
        filename, html = build_vehicle_page(make)
        path = os.path.join(vehicles_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ vehicles/{filename}")
        count += 1

    print("\nGenerating service pages...")
    for svc in SERVICES:
        filename, html = build_service_page(svc)
        path = os.path.join(services_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ services/{filename}")
        count += 1

    print("\nGenerating specials page...")
    filename, html = build_specials_page()
    path = os.path.join(ROOT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {filename}")
    count += 1

    print(f"\nDone! {count} pages generated.")
    print(f"Next: run  python3 update-sitemap.py  to add all URLs to sitemap.xml")

if __name__ == "__main__":
    main()
