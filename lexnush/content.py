import math
import re
from html import unescape
from textwrap import dedent

HTML_TAG_RE = re.compile(r"<[^>]+>")


def calculate_read_time(text):
    plain_text = unescape(HTML_TAG_RE.sub(" ", text))
    word_count = len(plain_text.split())
    minutes = max(1, math.ceil(word_count / 200))
    return f"{minutes} min read"


BLOG_POSTS = [
    {
        "id": 1,
        "slug": "surgery-or-autopsy-adr-award-modification",
        "title": "Surgery or Autopsy? The Supreme Court's Arbitral Scalpel",
        "author": "Anushka Pandey",
        "category": "ADR",
        "date": "March 2026",
        "date_iso": "2026-03-01",
        "summary": "It is the ultimate legal showdown: does this rescue people from endless litigation loops, or has the court opened the floodgates for judges to rewrite private contracts?",
        "key_takeaways": [
            "For the last thirty years, the absolute golden rule of arbitration has been finality.",
            "But on April 30, 2025, the Supreme Court of India shattered that rule.",
            "The Supreme Court has handed Indian judges a powerful new scalpel.",
        ],
        "content": dedent(
            """
            <p>Let’s be honest: when most people picture the law, they see an icy, closed-off world of black robes, towering stacks of paperwork, and people speaking a language that sounds suspiciously like Latin spells from Harry Potter. It feels distant, cold, and entirely detached from real life.</p>

            <p>But in the real world, the law has a heartbeat, and right now, that heartbeat is pounding fast in a room outside the traditional courtroom.</p>

            <p>Welcome to the world of Alternative Dispute Resolution (ADR), specifically arbitration. Think of it as a private, out-of-court dispute system where companies skip the endless lines of traditional courts and hire a neutral expert (the arbitrator) to act as their private judge. The final decision they hand down isn’t a judgment; it’s called an arbitral award.</p>

            <p>For the last thirty years, the absolute golden rule of arbitration has been finality. You get one shot. If you do not like the decision and drag it to a real court to challenge it under Section 34 of the Arbitration Act, the judge’s hands were legally tied.</p>

            <p>The rule was brutal: a court could only perform an autopsy, never surgery. If a judge found a fatal flaw in the award, they could not fix it. They could only kill it entirely, setting it aside and sending the parties right back to square one to start a years-long arbitration process all over again.</p>

            <p>But on April 30, 2025, the Supreme Court of India shattered that rule. In a monumental 4:1 landmark decision titled Gayatri Balasamy v. ISG Novasoft Technologies Ltd., a 5-judge Constitution Bench ruled that Indian courts do have a limited, precise power to surgically modify an arbitral award.</p>

            <p>It’s the ultimate legal showdown: does this rescue people from endless litigation loops, or has the court just opened the floodgates for judges to rewrite private contracts?</p>

            <h2>The Human Story Behind the Legal Battle</h2>

            <p>At LexNush, we believe clients are not case numbers; they are stories. And the story behind this landmark case is a masterclass in resilience.</p>

            <p>Back in 2006, Gayatri Balasamy, a senior woman executive, faced workplace sexual harassment and was subsequently served with arbitrary termination notices by her employer. She did not back down. She fought through private arbitration and won an award of Rs. 2 Crores in compensation.</p>

            <p>But the arbitrator overlooked a few of her claims. When she approached the High Court to get those specific omissions fixed, she entered a circular, multi-stage legal nightmare:</p>

            <p><strong>The Single Judge’s Surgery:</strong> Seeing the injustice of the overlooked claims, a single judge bench performed "surgery," upgrading her compensation by an extra Rs. 1.6 Crores.</p>

            <p><strong>The Division Bench’s Reversal:</strong> On appeal, a two-judge bench struck that down. They ruled that judges legally cannot modify awards, slashing her additional compensation to a mere Rs. 50,000 because they thought the initial enhancement was procedurally illegal.</p>

            <p><strong>The Supreme Court’s Final Stand:</strong> Finally reaching the apex court, a 5-judge bench stepped in to answer the ultimate question: can a court actually modify an award to ensure a human being gets justice?</p>

            <p>By the time the Supreme Court delivered its final verdict on April 30, 2025, nearly two decades had passed since her employment was terminated. Her case perfectly exposed the agony of the old system: if a court cannot make minor, common-sense corrections to an award, the pursuit of justice becomes an endless, exhausting loop.</p>

            <h2>Breaking Down the Jargon: Set Aside vs. Modify</h2>

            <p>Let’s translate the law into life. What do these terms actually mean when a case hits a judge’s desk?</p>

            <p><strong>Setting Aside (The Autopsy):</strong> This is the old-school power under Section 34. The court declares the arbitrator’s decision dead. The award is annulled. The parties have to pack their bags, hire new lawyers, and start a brand-new arbitration from scratch.</p>

            <p><strong>Modification (The Surgery):</strong> The court looks at the award, spots a clear error, fixes that specific part, and leaves the rest of the decision alive and enforceable.</p>

            <p>For years, the gold standard rule was: “You are not an appellate court. You cannot rewrite what the arbitrator wrote. If it’s broken, throw it away.” The 2025 Balasamy judgment changed the game.</p>

            <h2>How the Court Justified the Medical Upgrade</h2>

            <p>Writing for the 4-judge majority, Chief Justice Sanjiv Khanna relied on a classic legal concept: the idea that the greater power includes the lesser.</p>

            <p>The Court reasoned that if a judge has the massive, destructive power to strike down an entire award, they must logically possess the smaller, gentler power to cut out only the broken parts and save the rest.</p>

            <p>The Supreme Court carved out three strict zones where a judge can now use a legal scalpel:</p>

            <div class="table-scroll">
                <table>
                    <caption>Limited situations in which a court may modify an arbitral award</caption>
                    <thead>
                        <tr>
                            <th>The Toolkit</th>
                            <th>What a Judge Can Do Now</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>1. The Severability Scalpel</strong></td>
                            <td>If an award can be cleanly split into independent sections, the court can chop off the invalid or illegal part and preserve the healthy, legal portions.</td>
                        </tr>
                        <tr>
                            <td><strong>2. The Math Correction</strong></td>
                            <td>If the arbitrator made an undeniable mathematical, clerical, or typographical error on the face of the record, the judge can fix the typo.</td>
                        </tr>
                        <tr>
                            <td><strong>3. The Interest Tweak</strong></td>
                            <td>The court can modify the post-award interest rate if it is absurdly high or completely missing.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <p>The majority argued this is not "re-trying" the case; it is simply rescuing people from a tragic loop of re-arbitration over obvious, un-debatable mistakes.</p>

            <h2>The Dissent: A Warning of Chaos</h2>

            <p>Not everyone on the bench was celebrating. Justice K.V. Viswanathan wrote a fierce dissenting opinion that acts as a serious warning flare for the business world.</p>

            <p>His argument was all about legislative fidelity, respecting the exact laws written by Parliament. He pointed out that when Parliament drafted the 1996 Arbitration Act, it deliberately deleted the words "power to modify" that existed in the old 1940 law. Parliament wanted courts to stay out of the private arbitration kitchen.</p>

            <p>Justice Viswanathan warned that terms like "obvious error" are highly subjective. One judge’s "quick fix" is another lawyer’s "intense debate." By giving judges a scalpel, he argues, the court has compromised the finality of arbitration. International investors choose arbitration because they want a private tribunal to have the final word, not a domestic judge who might decide to tidy up the math.</p>

            <h2>The LexNush Takeaway</h2>

            <p>The Balasamy judgment is a classic balancing act between two things we love at LexNush: speedy, empathetic justice and system integrity.</p>

            <p>On one hand, making a victim of harassment fight for 18 years just because a court could not fix a basic calculation error is institutional cruelty. The power to modify is a triumph of human common sense over rigid black-letter law.</p>

            <p>On the other hand, if every losing party now believes they can convince a judge that an award contains an error worth "modifying," arbitration challenges will transform into full-blown appellate trials, destroying the very speed and privacy arbitration was built for.</p>

            <p>The Supreme Court has handed Indian judges a powerful new scalpel. Whether they use it for precise, life-saving surgery or accidentally perform a destructive autopsy on party autonomy is the real story to watch.</p>
            """
        ).strip(),
    }
]


for post in BLOG_POSTS:
    post["read_time"] = calculate_read_time(post["content"])


INTERVIEWS = [
    {
        "id": 1,
        "guest": "Dr. Shashi Tharoor",
        "role": "MP & Author",
        "title": "Law, Language & Legacy",
        "date": "Coming Soon",
        "image": "guest1.jpg",
    }
]


PAGE_META = {
    "home": {
        "title": "LexNush | Law With A Pulse",
        "description": "LexNush is a premium legal publication for clear legal analysis, policy conversations, and modern legal insight.",
    },
    "about": {
        "title": "About LexNush",
        "description": "Learn why LexNush exists and how it translates law into clear, useful, human-centered legal insight.",
    },
    "blogs": {
        "title": "The Journal",
        "description": "Read LexNush essays on law, arbitration, policy, judgments, institutions, and the future of legal thinking.",
    },
    "interviews": {
        "title": "Interviews",
        "description": "Candid LexNush conversations with legal practitioners, policy architects, and institutional voices.",
    },
    "contact": {
        "title": "Contact LexNush",
        "description": "Contact LexNush for editorial pitches, collaboration proposals, corrections, and thoughtful legal dialogue.",
    },
    "privacy": {
        "title": "Privacy | LexNush",
        "description": "How LexNush handles contact inquiries and newsletter subscriptions.",
    },
}
