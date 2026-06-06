from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import abort
from html import unescape
from textwrap import dedent
import math
import re

app = Flask(__name__)

# ================= THE "BRAIN" (SIMULATED DATABASE) =================

BLOG_POSTS = [
    {
        "id": 1,
        "slug": "surgery-or-autopsy-adr-award-modification",
        "title": "Surgery or Autopsy? The Supreme Court's Arbitral Scalpel",
        "author": "Anushka Pandey",
        "category": "ADR",
        "date": "March 2026",
        "summary": "It’s the ultimate legal showdown: Does this rescue people from endless litigation loops, or has the court just opened the floodgates for judges to rewrite private contracts?",
        "key_takeaways": [
            "For the last thirty years, the absolute golden rule of arbitration has been finality.",
            "But on April 30, 2025, the Supreme Court of India shattered that rule.",
            "The Supreme Court has handed Indian judges a powerful new scalpel."
        ],
        "content": dedent("""
<p style="margin: 0 0 1.4em 0;">Let’s be honest: when most people picture the law, they see an icy, closed-off world of black robes, towering stacks of paperwork, and people speaking a language that sounds suspiciously like Latin spells from Harry Potter. It feels distant, cold, and entirely detached from real life.</p>

<p style="margin: 0 0 1.4em 0;">But in the real world, the law has a heartbeat, and right now, that heartbeat is pounding fast in a room outside the traditional courtroom.</p>

<p style="margin: 0 0 1.4em 0;">Welcome to the world of Alternative Dispute Resolution (ADR) specifically, Arbitration. Think of it as a private, out-of-court dispute system where companies skip the endless lines of traditional courts and hire a neutral expert (the arbitrator) to act as their private judge. The final decision they hand down isn’t a judgment; it’s called an Arbitral Award.</p>

<p style="margin: 0 0 1.4em 0;">For the last thirty years, the absolute golden rule of arbitration has been finality. You get one shot. If you don't like the decision and drag it to a real court to challenge it under Section 34 of the Arbitration Act, the judge’s hands were legally tied.</p>

<p style="margin: 0 0 1.4em 0;">The rule was brutal: A court could only perform an autopsy, never surgery. If a judge found a fatal flaw in the award, they couldn't fix it. They could only kill it entirely, setting it aside and sending the parties right back to square one to start a years-long arbitration process all over again.</p>

<p style="margin: 0 0 1.4em 0;">But on April 30, 2025, the Supreme Court of India shattered that rule. In a monumental 4:1 landmark decision titled Gayatri Balasamy v. ISG Novasoft Technologies Ltd., a 5-judge Constitution Bench ruled that Indian courts do have a limited, precise power to surgically modify an arbitral award.</p>

<p style="margin: 0 0 1.4em 0;">It’s the ultimate legal showdown: Does this rescue people from endless litigation loops, or has the court just opened the floodgates for judges to rewrite private contracts?</p>

<h2 style="font-size: 1.8rem; line-height: 1.25; margin: 2.5em 0 0.9em 0;">The Human Story Behind the Legal Battle</h2>

<p style="margin: 0 0 1.4em 0;">At LexNush, we believe clients aren’t case numbers- they’re stories. And the story behind this landmark case is a masterclass in resilience.</p>

<p style="margin: 0 0 1.4em 0;">Back in 2006, Gayatri Balasamy, a senior woman executive, faced workplace sexual harassment and was subsequently served with arbitrary termination notices by her employer. She didn't back down. She fought through private arbitration and won an award of ₹2 Crores in compensation.</p>

<p style="margin: 0 0 1.4em 0;">But the arbitrator overlooked a few of her claims. When she approached the High Court to get those specific omissions fixed, she entered a circular, multi-stage legal nightmare:</p>

<p style="margin: 0 0 1.4em 0;">The Single Judge’s Surgery: Seeing the injustice of the overlooked claims, a single judge bench performed "surgery," upgrading her compensation by an extra ₹1.6 Crores.</p>

<p style="margin: 0 0 1.4em 0;">The Division Bench’s Reversal: On appeal, a two-judge bench struck that down. They ruled that judges legally cannot modify awards, slashing her additional compensation to a mere ₹50,000 because they thought the initial enhancement was procedurally illegal.</p>

<p style="margin: 0 0 1.4em 0;">The Supreme Court’s Final Stand: Finally reaching the apex court, a 5-judge bench stepped in to answer the ultimate question: Can a court actually modify an award to ensure a human being gets justice?</p>

<p style="margin: 0 0 1.4em 0;">By the time the Supreme Court delivered its final verdict on April 30, 2025, nearly two decades had passed since her employment was terminated. Her case perfectly exposed the agony of the old system: if a court cannot make minor, common-sense corrections to an award, the pursuit of justice becomes an endless, exhausting loop.</p>

<h2 style="font-size: 1.8rem; line-height: 1.25; margin: 2.5em 0 0.9em 0;">Breaking Down the Jargon: "Set Aside" vs. "Modify"</h2>

<p style="margin: 0 0 1.4em 0;">Let’s translate the law into life. What do these terms actually mean when a case hits a judge's desk?</p>

<p style="margin: 0 0 1.4em 0;">Setting Aside (The Autopsy): This is the old-school power under Section 34. The court declares the arbitrator's decision dead. The award is annulled. The parties have to pack their bags, hire new lawyers, and start a brand-new arbitration from scratch.</p>

<p style="margin: 0 0 1.4em 0;">Modification (The Surgery): The court looks at the award, spots a clear error, fixes that specific part, and leaves the rest of the decision alive and enforceable.</p>

<p style="margin: 0 0 1.4em 0;">For years, the gold standard rule was: “You are not an appellate court. You cannot rewrite what the arbitrator wrote. If it’s broken, throw it away.” The 2025 Balasamy judgment changed the game.</p>

<h2 style="font-size: 1.8rem; line-height: 1.25; margin: 2.5em 0 0.9em 0;">How the Court Justified the Medical Upgrade</h2>

<p style="margin: 0 0 1.4em 0;">Writing for the 4-judge majority, Chief Justice Sanjiv Khanna relied on a classic legal concept: the idea that the greater power includes the lesser.</p>

<p style="margin: 0 0 1.4em 0;">The Court reasoned that if a judge has the massive, destructive power to strike down an entire award, they must logically possess the smaller, gentler power to cut out only the broken parts and save the rest.</p>

<p style="margin: 0 0 1.4em 0;">The Supreme Court carved out three strict zones where a judge can now use a legal scalpel:</p>

<div style="margin: 2.2em 0; overflow-x: auto;">
    <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; border: 1px solid var(--border-color); background: var(--card-bg);">
        <thead>
            <tr>
                <th style="text-align: left; padding: 16px; border: 1px solid var(--border-color); color: var(--accent); font-size: 0.9rem; letter-spacing: 1px; text-transform: uppercase;">The Toolkit</th>
                <th style="text-align: left; padding: 16px; border: 1px solid var(--border-color); color: var(--accent); font-size: 0.9rem; letter-spacing: 1px; text-transform: uppercase;">What a Judge Can Do Now</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 16px; border: 1px solid var(--border-color); vertical-align: top; color: var(--text-main);"><strong>1. The Severability Scalpel</strong></td>
                <td style="padding: 16px; border: 1px solid var(--border-color); vertical-align: top; color: var(--text-muted);">If an award can be cleanly split into independent sections, the court can chop off the invalid/illegal part and preserve the healthy, legal portions.</td>
            </tr>
            <tr>
                <td style="padding: 16px; border: 1px solid var(--border-color); vertical-align: top; color: var(--text-main);"><strong>2. The Math Correction</strong></td>
                <td style="padding: 16px; border: 1px solid var(--border-color); vertical-align: top; color: var(--text-muted);">If the arbitrator made an undeniable mathematical, clerical, or typographical error on the face of the record, the judge can fix the typo.</td>
            </tr>
            <tr>
                <td style="padding: 16px; border: 1px solid var(--border-color); vertical-align: top; color: var(--text-main);"><strong>3. The Interest Tweak</strong></td>
                <td style="padding: 16px; border: 1px solid var(--border-color); vertical-align: top; color: var(--text-muted);">The court can modify the post-award interest rate if it is absurdly high or completely missing.</td>
            </tr>
        </tbody>
    </table>
</div>

<p style="margin: 0 0 1.4em 0;">The majority argued this isn't "re-trying" the case; it’s simply rescuing people from a tragic loop of re-arbitration over obvious, un-debatable mistakes.</p>

<h2 style="font-size: 1.8rem; line-height: 1.25; margin: 2.5em 0 0.9em 0;">The Dissent: A Warning of Chaos</h2>

<p style="margin: 0 0 1.4em 0;">Not everyone on the bench was celebrating. Justice K.V. Viswanathan wrote a fierce dissenting opinion that acts as a serious warning flare for the business world.</p>

<p style="margin: 0 0 1.4em 0;">His argument was all about Legislative Fidelity, respecting the exact laws written by Parliament. He pointed out that when Parliament drafted the 1996 Arbitration Act, it deliberately deleted the words "power to modify" that existed in the old 1940 law. Parliament wanted courts to stay out of the private arbitration kitchen.</p>

<p style="margin: 0 0 1.4em 0;">Justice Viswanathan warned that terms like "obvious error" are highly subjective. One judge's "quick fix" is another lawyer's "intense debate." By giving judges a scalpel, he argues, the court has compromised the finality of arbitration. International investors choose arbitration because they want a private tribunal to have the final word, not a domestic judge who might decide to tidy up the math.</p>

<h2 style="font-size: 1.8rem; line-height: 1.25; margin: 2.5em 0 0.9em 0;">The LexNush Takeaway</h2>

<p style="margin: 0 0 1.4em 0;">The Balasamy judgment is a classic balancing act between two things we love at LexNush: Speedy, Empathetic Justice and System Integrity.</p>

<p style="margin: 0 0 1.4em 0;">On one hand, making a victim of harassment fight for 18 years just because a court couldn't fix a basic calculation error is institutional cruelty. The power to modify is a triumph of human common sense over rigid black-letter law.</p>

<p style="margin: 0 0 1.4em 0;">On the other hand, if every losing party now believes they can convince a judge that an award contains an error worth "modifying," arbitration challenges will transform into full-blown appellate trials, destroying the very speed and privacy arbitration was built for.</p>

<p style="margin: 0 0 1.4em 0;">The Supreme Court has handed Indian judges a powerful new scalpel. Whether they use it for precise, life-saving surgery or accidentally perform a destructive autopsy on party autonomy is the real story to watch.</p>
        """).strip(),
    }
]

INTERVIEWS = [
    {
        "id": 1,
        "guest": "Dr. Shashi Tharoor",
        "role": "MP & Author",
        "title": "Law, Language & Legacy",
        "date": "Coming Soon",
        "image": "guest1.jpg"
    }
]

# ================= UTILITY FUNCTIONS =================

HTML_TAG_RE = re.compile(r"<[^>]+>")


def calculate_read_time(text):
    """Calculates read time based on 200 words per minute."""
    plain_text = unescape(HTML_TAG_RE.sub(" ", text))
    word_count = len(plain_text.split())
    minutes = max(1, math.ceil(word_count / 200))
    return f"{minutes} min read"


# Pre-calculate read times
for post in BLOG_POSTS:
    post["read_time"] = calculate_read_time(post["content"])

# ================= ROUTES =================


@app.route("/")
def home():
    featured = BLOG_POSTS[0] if BLOG_POSTS else None
    return render_template("index.html", featured_post=featured)


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/blogs/")
def blogs():
    return render_template("blogs.html", posts=BLOG_POSTS)


@app.route("/blogs/<slug>")
def post_detail(slug):
    post = next((item for item in BLOG_POSTS if item["slug"] == slug), None)
    if post is None:
        abort(404)
    return render_template("post.html", post=post)


@app.route("/interviews/")
def interviews():
    return render_template("interviews.html", interviews=INTERVIEWS)


@app.route("/contact/")
def contact():
    return render_template("contact.html")


# ================= API ENDPOINTS =================

@app.route("/api/search")
def search():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])

    results = []
    for post in BLOG_POSTS:
        if query in post["title"].lower() or query in post["summary"].lower():
            results.append({
                "type": "Article",
                "title": post["title"],
                "url": f"/blogs/{post['slug']}"
            })

    for interview in INTERVIEWS:
        if query in interview["guest"].lower() or query in interview["title"].lower():
            results.append({
                "type": "Interview",
                "title": f"Interview: {interview['guest']}",
                "url": "/interviews/"
            })

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)