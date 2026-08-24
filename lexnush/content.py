import math
import re
from html import unescape
from textwrap import dedent

HTML_TAG_RE = re.compile(r"<[^>]+>")
SITE_LASTMOD_ISO = "2026-08-24"

AUTHORS = {
    "anushka-pandey": {
        "slug": "anushka-pandey",
        "name": "Anushka Pandey",
        "role": "Founder & Editor, LexNush",
        "short_bio": (
            "Anushka Pandey is the founder and editor of LexNush, focused on making law, policy, "
            "and public life clearer without flattening their complexity."
        ),
        "image": "images/anushka-760.jpg",
        "same_as": "https://www.linkedin.com/in/anushka-pandey31",
    }
}


def calculate_read_time(text):
    plain_text = unescape(HTML_TAG_RE.sub(" ", text))
    word_count = len(plain_text.split())
    minutes = max(1, math.ceil(word_count / 200))
    return f"{minutes} min read"


BLOG_POSTS = [
    {
        "id": 4,
        "slug": "one-year-at-the-bar-two-years-before-the-bench",
        "title": "One Year at the Bar, Two Years Before the Bench: Has the Supreme Court Reimagined Judicial Experience?",
        "author": "Anushka Pandey",
        "author_slug": "anushka-pandey",
        "category": "Analysis",
        "section": "analysis",
        "date": "24 August 2026",
        "date_iso": "2026-08-24",
        "date_modified": "24 August 2026",
        "date_published_iso": "2026-08-24T09:00:00+05:30",
        "date_modified_iso": "2026-08-24T09:00:00+05:30",
        "keywords": [
            "Bhumika Trust v. Union of India",
            "2026 INSC 904",
            "judicial appointments",
            "judicial service examination",
            "District Court practice",
            "judicial training",
            "law clerkship",
        ],
        "image_alt": "Supreme Court of India",
        "sources": [
            {
                "title": "Bhumika Trust v. Union of India, 2026 INSC 904",
                "publisher": "Supreme Court of India",
                "url": "https://api.sci.gov.in/supremecourt/2025/62949/62949_2025_1_1501_73791_Judgement_21-Aug-2026.pdf",
            }
        ],
        "seo_description": "An analysis of Bhumika Trust v. Union of India and the Supreme Court's new pathway into the lower judiciary.",
        "summary": "The Court's new model combines one year of District Court practice with Judicial Academy training and a structured clerkship before regular judicial service.",
        "key_takeaways": [],
        "content": dedent(
            """
            <p>A law degree can teach you the law. It cannot always teach you what it feels like to stand in a courtroom when the outcome of a case matters deeply to someone.</p>

            <p>That has always been at the centre of the debate around judicial appointments. How much practical experience should a person have before they are trusted with judicial power?</p>

            <p>On 21 August 2026, the Supreme Court revisited this question in <em>Bhumika Trust v. Union of India</em>. The decision has changed the way candidates will enter the lower judiciary, but it would be inaccurate to say that the Court has simply reduced the three year practice requirement to one year.</p>

            <p>The judgment does something more complicated.</p>

            <p>The Court has tried to create a combination of courtroom practice, judicial training and supervised experience before a candidate finally becomes a regular judicial officer.</p>

            <p>For recruitments notified on or after 1 April 2027, candidates will need one year of actual practice in the District Court before appearing for the examination. After selection, they will undergo one year of training at a State Judicial Academy and then one year of structured law clerkship. Only after satisfactory evaluation will they enter regular judicial service.</p>

            <p>This raises a larger question that is far more interesting than whether the number is one or three.</p>

            <h2>What actually counts as experience for someone who is going to become a judge?</h2>

            <h2>Why did the three year rule come back in the first place?</h2>

            <p>The three year practice requirement is not new.</p>

            <p>The Supreme Court had earlier directed that candidates entering the judicial service should have three years of practice at the Bar. The reasoning was fairly straightforward. A judge needs to understand not only legal principles but also how litigation works in practice.</p>

            <p>That position changed in 2002 when the Supreme Court removed the requirement. At that time, the Court considered the changing nature of legal education and the possibility of providing intensive judicial training after recruitment.</p>

            <p>For more than two decades, fresh law graduates could therefore enter the judicial service without first spending years at the Bar.</p>

            <p>The position changed again in 2025 when the Supreme Court restored the three year practice requirement.</p>

            <p>The concern was that a person could move almost directly from law school to the Bench without having experienced the adversarial system as a practising lawyer. Questions were raised about familiarity with court procedure, professional conduct, courtroom functioning and the practical difficulties faced by litigants and lawyers.</p>

            <p>The concern was not that young law graduates were incapable of understanding law.</p>

            <p>It was that knowing the law and understanding the working of a court are two different things.</p>

            <p>That distinction is important.</p>

            <p>But does three years of practice automatically create experience?</p>

            <p>This is where the latest judgment becomes interesting.</p>

            <p>Three years sounds like an objective standard. It is easy to verify and easy to apply. But it does not necessarily tell us much about the quality of someone's experience.</p>

            <p>Consider two young lawyers.</p>

            <p>Both have been enrolled for three years.</p>

            <p>One has spent those years regularly appearing in District Courts, assisting seniors, dealing with clients, preparing pleadings and watching proceedings.</p>

            <p>The other may have spent most of those three years doing research, drafting documents or working in a chamber where actual courtroom exposure was limited.</p>

            <p>Both have three years of practice.</p>

            <p>But their experience is clearly not the same.</p>

            <p>This is one of the difficulties with measuring professional readiness purely through time.</p>

            <p>The number of years can tell us how long someone has been in the profession. It cannot tell us what they have actually learnt during that period.</p>

            <p>The Supreme Court's latest approach appears to recognise this problem.</p>

            <p>Instead of treating three years at the Bar as the only meaningful form of preparation, the majority has created a system where different forms of practical exposure can work together.</p>

            <p>One year of actual District Court practice provides exposure to the Bar.</p>

            <p>Judicial Academy training provides structured preparation for the judicial role.</p>

            <p>The clerkship provides direct exposure to the working of the judiciary.</p>

            <p>The question is whether these three experiences together can produce a better prepared judge.</p>

            <h2>Can judicial experience really be taught?</h2>

            <p>This is perhaps the most difficult question raised by the judgment.</p>

            <p>A Judicial Academy can teach a trainee how to analyse a case.</p>

            <p>It can teach procedures.</p>

            <p>It can teach judgment writing.</p>

            <p>It can expose a trainee to different kinds of cases and judicial situations.</p>

            <p>A structured clerkship can provide an opportunity to observe judges and understand how cases move through the system.</p>

            <p>But there are things that are difficult to reproduce inside a training programme.</p>

            <p>A lawyer standing before a judge has to deal with a real client.</p>

            <p>A litigant may be anxious about losing their home.</p>

            <p>An accused person may be waiting for a decision that affects their liberty.</p>

            <p>A family dispute may involve people who have known each other for decades.</p>

            <p>A commercial dispute may determine whether a business survives.</p>

            <p>These realities are experienced differently when you are standing at the Bar.</p>

            <p>A future judge needs to understand not just the law in the file but also the people whose lives are affected by the order being passed.</p>

            <p>This is where the dissent of Justice K. Vinod Chandran becomes significant.</p>

            <p>His disagreement brings attention to the value of actual professional experience. The courtroom is not simply a place where legal principles are applied. It is also where lawyers learn how procedure works in reality, how arguments develop, how judges manage cases and how litigants experience the legal system.</p>

            <p>Some of that can be taught.</p>

            <p>Some of it probably has to be experienced.</p>

            <h2>The three year requirement also had a hidden problem</h2>

            <p>There is another side to this debate that deserves more attention.</p>

            <p>Practising law for three years is not equally difficult for everyone.</p>

            <p>For someone with financial support and access to a good chamber, the early years of practice may be manageable.</p>

            <p>For another young lawyer, three years of uncertain income can be a significant barrier.</p>

            <p>The legal profession is already difficult to enter for many young lawyers. Access to good chambers, mentorship, paying briefs and meaningful courtroom work is not distributed equally.</p>

            <p>A three year requirement can therefore have an unintended effect. It can make judicial service easier to access for those who can afford to wait and harder for those who cannot.</p>

            <p>This does not mean that the practice requirement was wrong.</p>

            <p>It means that the Court had to consider another question alongside judicial competence.</p>

            <p>Who gets the opportunity to become a judge in the first place?</p>

            <p>The latest judgment attempts to address this by reducing the period of mandatory practice while retaining practical exposure through training and clerkship.</p>

            <p>Whether that balance works will depend heavily on how the new system is implemented.</p>

            <h2>One year of practice does not mean one year of preparation</h2>

            <p>This point is important because the judgment can easily be misunderstood.</p>

            <p>The new system is not a direct route from law school to the Bench.</p>

            <p>For recruitments from 1 April 2027, the candidate will need one year of District Court practice before appearing for the examination.</p>

            <p>After selection, there will be another two years of structured preparation.</p>

            <p>The first year will be spent in Judicial Academy training.</p>

            <p>The second will involve a structured clerkship, including exposure to the District Judiciary and the High Court.</p>

            <p>The candidate will also be evaluated before entering regular judicial service.</p>

            <p>So the real change is not that the Supreme Court has decided that one year of practice is enough.</p>

            <p>The change is that the Court has decided that judicial readiness can be built through a combination of different experiences.</p>

            <p>That is a much more significant change in the way we think about judicial recruitment.</p>

            <h2>What should actually be measured?</h2>

            <p>Perhaps the debate should move away from the question of whether the requirement should be one year or three years.</p>

            <p>Instead, we should ask what a person should be able to do before becoming a judge.</p>

            <p>They should understand courtroom procedure.</p>

            <p>They should know how litigation actually unfolds.</p>

            <p>They should understand the relationship between the Bench and the Bar.</p>

            <p>They should know how lawyers prepare and present cases.</p>

            <p>They should be able to assess evidence and arguments.</p>

            <p>They should understand the consequences of procedural delays.</p>

            <p>They should know how to write clear and reasoned orders.</p>

            <p>Most importantly, they should understand that every case represents a person whose life exists outside the case file.</p>

            <p>If the new training and clerkship system can develop these abilities, then reducing the pre examination practice requirement may not weaken the judiciary.</p>

            <p>It may actually produce a more structured pathway into judicial service.</p>

            <p>But if the training becomes a formality and the clerkship becomes nothing more than observation, then the system may simply replace one problem with another.</p>

            <h2>The five year question</h2>

            <p>The Supreme Court has given the new framework five years.</p>

            <p>That may be one of the most sensible aspects of the decision.</p>

            <p>Instead of assuming that the new model will work perfectly, the Court has left room for it to be assessed based on actual experience.</p>

            <p>The important question over the next five years should not be how many candidates entered the judiciary after one year of practice.</p>

            <p>It should be what kind of judges they became.</p>

            <p>Are they able to manage courtrooms effectively?</p>

            <p>Do they understand procedural realities?</p>

            <p>Are their judgments clear and legally sound?</p>

            <p>Do lawyers find them sufficiently familiar with courtroom practice?</p>

            <p>Are litigants being heard properly?</p>

            <p>Does the new training model produce better prepared judicial officers?</p>

            <p>Those are the questions that will tell us whether the experiment has worked.</p>

            <h2>So, has the Supreme Court found the right balance?</h2>

            <p>It is too early to say.</p>

            <p>The majority has tried to find a middle ground between two competing concerns.</p>

            <p>The first is that the judicial office requires practical understanding and should not become an immediate destination after law school.</p>

            <p>The second is that a rigid three year practice requirement may not be the only or even the best way to develop that understanding.</p>

            <p>The Court's solution is therefore not really one year instead of three.</p>

            <p>It is one year of practice followed by structured institutional exposure before a candidate takes full responsibility as a judicial officer.</p>

            <p>Whether that is enough will depend on the quality of the institutions responsible for providing that experience.</p>

            <p>The judgment ultimately leaves us with a question that goes beyond judicial recruitment.</p>

            <p><strong>Experience is not simply the amount of time we spend doing something. It is what that time teaches us.</strong></p>

            <p>A future judge needs legal knowledge, but legal knowledge alone is not enough.</p>

            <p>They need to understand the courtroom, the profession and the people who come into the justice system.</p>

            <p>The Supreme Court has now chosen to test whether those lessons can be acquired through a carefully structured combination of practice, training and supervision.</p>

            <p>The next five years will tell us whether it works.</p>

            <p>Until then, perhaps the better question is not whether <strong>one year is enough to become a judge</strong>.</p>

            <p>It is whether <strong>the legal system can make those years count.</strong></p>
            """
        ).strip(),
    },
    {
        "id": 3,
        "slug": "the-clause-you-skipped-final-and-binding",
        "title": "The Clause You Skipped",
        "author": "Anushka Pandey",
        "author_slug": "anushka-pandey",
        "category": "Law Explained",
        "section": "law_explained",
        "date": "18 August 2026",
        "date_iso": "2026-08-18",
        "date_modified": "18 August 2026",
        "date_published_iso": "2026-08-18T09:00:00+05:30",
        "date_modified_iso": "2026-08-18T09:00:00+05:30",
        "keywords": [
            "arbitration clause",
            "final and binding",
            "arbitration award",
            "New York Convention",
            "contract law",
            "law explained",
        ],
        "image_alt": "Supreme Court of India",
        "sources": [],
        "seo_description": "Law Explained: what a final and binding arbitration clause means before a dispute begins.",
        "summary": "Ep. 1 “Final and binding”: the two scariest words in your contract",
        "key_takeaways": [],
        "content": dedent(
            """
            <p><strong>Ep. 1 “Final and binding”: the two scariest words in your contract</strong></p>

            <p><em>A new weekly series decoding the legal clauses nobody reads - until they need to.</em></p>

            <p>You’ve signed contracts before. Job offer, freelance agreement, vendor deal, maybe even a flat lease. Somewhere near the bottom, in the section your eyes glaze over for, there's usually a line like:</p>

            <blockquote>“Any dispute shall be referred to arbitration, and the decision of the arbitrator shall be final and binding.”</blockquote>

            <p>Most people skim right past it. Here’s the thing though, that one sentence just quietly gave up your right to walk into a courtroom if things ever go wrong. No judge. No jury. No appeal, in almost all cases. Just one clause, agreed to before any dispute even existed.</p>

            <h2>So what did you actually sign up for?</h2>

            <p><strong>It’s called arbitration</strong>, a private way of resolving disputes, outside the court system. Instead of a judge, both sides agree on a neutral person (or panel) called an <strong>arbitrator</strong>, who hears the case and makes a binding call. Think of it as a courtroom you and the other side built yourselves, with your own referee.</p>

            <h2>Why do companies love putting this in contracts?</h2>

            <ul>
                <li>⏱ <strong>It’s faster.</strong> Courts can take years. Arbitration often wraps up in months.</li>
                <li>🔒 <strong>It’s private.</strong> No public record, no headlines- whatever happens, stays between the parties.</li>
                <li>🧠 <strong>It’s specialised.</strong> You can pick an arbitrator who actually understands your industry, instead of a judge juggling a hundred unrelated cases.</li>
                <li>🌍 <strong>It travels.</strong> Thanks to a treaty called the New York Convention, an arbitration award from one country can be enforced in over 170 others. A court judgment usually can’t say the same.</li>
            </ul>

            <h2>So what does it actually look like when a dispute happens?</h2>

            <p>No lawsuit gets filed. Instead, an arbitrator (or three) is appointed, both sides present their case - documents, witnesses, arguments, much like a mini-trial, and the arbitrator issues an <strong>award</strong>. That award is final. Courts step in only in very narrow situations, either to enforce it, or, rarely, to set it aside.</p>

            <p><strong>Here’s the catch:</strong> none of this works unless you agreed to it <em>before</em> the dispute started. Which is exactly why that clause you skimmed past is doing more work than almost anything else in the contract.</p>

            <p>Next Tuesday, we go clause-hunting. How to actually spot and read an arbitration clause, and the one word inside it that can quietly change your entire legal position.</p>

            <p><em>This is a general explainer, not legal advice for any specific situation. New post every Tuesday.</em></p>
            """
        ).strip(),
    },
    {
        "id": 2,
        "slug": "when-the-state-watches-you-ai-surveillance-constitutional-privacy",
        "title": "When the State Watches You: AI Surveillance & Constitutional Privacy",
        "author": "Anushka Pandey",
        "author_slug": "anushka-pandey",
        "category": "Analysis",
        "section": "analysis",
        "date": "17 August 2026",
        "date_iso": "2026-08-17",
        "date_modified": "18 August 2026",
        "date_published_iso": "2026-08-17T09:00:00+05:30",
        "date_modified_iso": "2026-08-18T09:00:00+05:30",
        "keywords": [
            "AI surveillance",
            "constitutional privacy",
            "facial recognition technology",
            "K.S. Puttaswamy v. Union of India",
            "Digital Personal Data Protection Act 2023",
            "India",
        ],
        "image_alt": "Supreme Court of India",
        "sources": [],
        "seo_description": "An analysis of AI surveillance, facial recognition, and constitutional privacy in India.",
        "summary": "Constitutional privacy was built for searches and warrants. India has quietly moved into a world of continuous, automated watching without fully updating the law to match.",
        "key_takeaways": [],
        "content": dedent(
            """
            <p>There's a CCTV camera above the ticket counter at pretty much every railway station I’ve ever passed through, and until a few years ago I never thought twice about it. It’s just there, doing what cameras do, recording, in case something goes wrong. What I didn't think about, and what most people still don’t, is that a lot of those cameras are no longer just recording. They're matching faces against a database in real time. Nobody asked me. Nobody asked you either, probably. And that, in a sentence, is the problem this essay is trying to sit with: constitutional privacy was built for a world of searches and warrants, and we’ve quietly moved into a world of continuous, automated watching, without really updating the law to match.</p>

            <p>I want to try and work through why that mismatch matters, using India’s own privacy jurisprudence as the spine of the argument, because I think it’s actually one of the more interesting doctrinal experiments happening anywhere right now, even if, as I’ll get to, the follow-through has been shaky.</p>

            <h2>Puttaswamy and the promise it made</h2>

            <p>Everyone studying constitutional law in India in the last few years has had <em>K.S. Puttaswamy v. Union of India</em> (2017) practically tattooed into their revision notes, and for good reason. A nine-judge bench, unanimously, which is rare enough on its own, held that privacy is part of the right to life and personal liberty under Article 21. It wasn’t just symbolic. The Court gave us an actual test: state action that touches privacy has to (a) be backed by law, (b) serve a legitimate aim, and (c) be proportionate, the least intrusive option reasonably available, with safeguards against misuse.</p>

            <p>Read that test again and notice what it assumes. It assumes the state does something discreet, taps a phone, searches a house, intercepts a letter, to a specific person it has already decided to look at. That's the model the whole doctrine is built on. And that model just doesn't describe how AI surveillance actually works.</p>

            <h2>Why the old test keeps slipping</h2>

            <p>Three things, I think, break the fit.</p>

            <p>The first is sequencing. A wiretap needs a suspect before it needs a warrant. A facial recognition system at a metro station scans thousands of unconnected, un-suspected people in order to maybe find the one person it's looking for. The privacy intrusion happens to everyone, upfront, before anyone has done anything to warrant suspicion. Proportionality doctrine wasn't written for that order of operations.</p>

            <p>The second is the “least restrictive means” limb, which honestly starts to feel almost circular once you apply it to AI tools. The whole pitch behind mass surveillance systems is that they’re comprehensive - that's the feature, not the bug. So when a court asks “was there a less invasive way to do this,” the honest answer from the state is usually “yes, but it would have caught fewer people,” which isn't really the kind of answer proportionality analysis knows how to reject.</p>

            <p>The third is harder to put a finger on, and it's the one that bothers me most. A predictive-policing tool or a risk score doesn't “search” you the way we've traditionally understood searches. It just quietly nudges your name up a list. Nothing happens to you until, one day, something does, and by then it's very hard to trace the harm back to the moment the algorithm decided you were worth watching a little more closely. Our doctrine is good at naming injuries. It’s much worse at naming a slowly accumulating suspicion that never quite becomes an event.</p>

            <h2>What's actually on the books in India (and the hole in it)</h2>

            <p>For a while India didn’t really have a comprehensive data protection statute at all, just fragments under the IT Act and its 2011 rules. That changed, on paper, with the Digital Personal Data Protection Act, 2023, whose Rules were finally notified in November 2025 and are now being rolled out over an eighteen-month phase-in. It’s a genuine step forward: purpose limitation, data minimisation, storage limits, a Data Protection Board with actual enforcement teeth.</p>

            <p>But there's a provision in that Act that I keep coming back to, because it more or less undoes the promise of everything else in it. Section 17(1)(a) lets the central government exempt any “instrumentality of the State” from almost the whole Act, including the purpose limitation and data minimisation rules on the strength of an executive notification citing something like national security or public order, with no named agency responsible for it, no judicial check built in, and no sunset clause forcing it to expire. Think about what that means next to <em>Puttaswamy</em>’s proportionality test. The judgment said the state has to justify its intrusions. Section 17(1)(a) lets the state exempt itself from having to justify anything, by writing itself a note.</p>

            <p>Facial recognition is where you can watch this play out in real time. Most deployments by police and other public agencies haven't come through a specific law defining who can use the technology, on whom, for what purpose, or under whose supervision, they’ve come through procurement decisions and executive notifications instead. There's actually a private member’s bill sitting in Parliament that would require magistrate-level sign-off before police could use FRT, but private member bills almost never become law in India, and this one hasn’t moved. Even NITI Aayog’s own policy paper on responsible AI recommended that law enforcement shouldn't get a free pass from data protection oversight, which is exactly the recommendation Section 17 ignores.</p>

            <p>So you end up with this slightly absurd asymmetry. A private company running facial recognition for office access control has to get consent, state a purpose, and delete the data when it's no longer needed. A state police department running the same technology across an entire city, at a scale no private company could match, can be carved out of most of those obligations by notification. The bigger the surveillance, the less law applies to it.</p>

            <h2>Running the test on an actual case</h2>

            <p>Take something concrete: a state government using AI-linked CCTV with facial recognition to identify people at a protest. Push it through the <em>Puttaswamy</em> test and see where it holds.</p>

            <p>Backed by law weakly, if at all, since most of these systems arrive via procurement and notification rather than a statute written for this specific purpose. Legitimate aim, almost trivially yes, “public order” clears that bar without much resistance, and courts have generally been reluctant to interrogate the state’s own characterisation of a security interest. Proportionate, with safeguards, this is the part that should matter most and matters least in practice. No independent authorisation before deployment. No retention limit tied to the specific use. No real audit trail a surveilled person could ever actually access. And because of Section 17(1)(a), possibly no statutory minimisation obligation binding the agency at all.</p>

            <p>The test isn't broken. It’s just not being applied before the fact, only, sometimes, years later, after a controversy forces someone to litigate it.</p>

            <h2>A quick look elsewhere, because it's not just us</h2>

            <p>The EU offers a useful contrast, even if I don’t think it’s a perfect model. Its framework subjects government surveillance to controls broadly comparable to what it imposes on private companies, rather than letting the state write its own exceptions. The AI Act treats real-time biometric identification by law enforcement in public spaces as high-risk, in some cases outright prohibited, and generally requires independent or judicial authorisation before it's used.</p>

            <p>The US got there through a completely different door, Fourth Amendment doctrine, built around “reasonable expectation of privacy,” had to stretch to cover bulk data collection, and did so in <em>Carpenter v. United States</em> (2018), where the Court held that pulling someone's historical cell-site location data counts as a search requiring a warrant, precisely because aggregating that data tells you far more than any single data point ever could.</p>

            <p>Three very different legal traditions, and they’re all arriving at roughly the same conclusion: once surveillance becomes automated and cumulative, it stops being a smaller version of an old problem and becomes a new one.</p>

            <h2>What would actually fix this</h2>

            <p>I don’t think the answer is a completely new theory of privacy, <em>Puttaswamy</em> gives us more than enough doctrinal room to work with. What's missing is mostly institutional follow-through, and a few specific legislative choices:</p>

            <p>First, a dedicated law for algorithmic and biometric surveillance, separate from the general data protection statute, that actually names what facial recognition and similar tools can be used for, requires sign-off from someone independent of the agency deploying it, and sets binding limits on retention, instead of leaving all of this to be decided by procurement departments and executive notifications after the fact.</p>

            <p>Second, narrowing the state's blanket exemption under Section 17(1)(a) down to something that looks like an actual necessity-and-proportionality test, reviewable by a court or an independent body, rather than a notification the government issues to itself and answers to no one.</p>

            <p>Third, and this is the one I feel least confident courts are ready for, but think matters most, some way of treating ongoing algorithmic monitoring as a legally cognisable injury in its own right, even when it hasn’t yet led to an arrest or a denied benefit. Otherwise we keep waiting for the harm to fully materialise before anyone's allowed to challenge it, by which point it's usually too late to matter.</p>

            <h2>Where that leaves us</h2>

            <p>None of this is really about the technology being evil. Cameras and algorithms don't have intentions. What they do have is scale, and scale is exactly what constitutional privacy doctrine was never really tested against until now. <em>Puttaswamy</em> gave India the vocabulary to demand that the state justify itself before it watches its citizens. What we haven’t yet built is the habit- legislative, judicial, institutional, of actually making it do so before the cameras go up, rather than years later, in a courtroom, after the watching has already happened.</p>
            """
        ).strip(),
    },
    {
        "id": 1,
        "slug": "surgery-or-autopsy-adr-award-modification",
        "title": "Surgery or Autopsy? The Supreme Court's Arbitral Scalpel",
        "author": "Anushka Pandey",
        "author_slug": "anushka-pandey",
        "category": "Analysis",
        "section": "analysis",
        "date": "March 2026",
        "date_iso": "2026-03-01",
        "date_modified": "July 2026",
        "date_published_iso": "2026-03-01T09:00:00+05:30",
        "date_modified_iso": "2026-07-27T16:45:00+05:30",
        "keywords": [
            "Gayatri Balasamy v ISG Novasoft",
            "2025 INSC 605",
            "arbitral award modification",
            "Section 34 Arbitration Act",
            "Supreme Court of India",
            "alternative dispute resolution",
        ],
        "image_alt": "Legal research materials arranged on a desk",
        "sources": [
            {
                "title": "Gayatri Balasamy v. M/s ISG Novasoft Technologies Limited, 2025 INSC 605",
                "publisher": "Supreme Court of India",
                "url": "https://api.sci.gov.in/supremecourt/2021/20788/20788_2021_1_1501_61506_Judgement_30-Apr-2025.pdf",
            }
        ],
        "seo_description": "LexNush analyses Gayatri Balasamy v ISG Novasoft (2025 INSC 605), where India's Supreme Court recognised a limited power to modify arbitral awards.",
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
    post["word_count"] = len(unescape(HTML_TAG_RE.sub(" ", post["content"])).split())


COUNSEL_DESK = [
    {
        "id": 1,
        "guest": "Dr. Shashi Tharoor",
        "role": "MP & Author",
        "title": "Law, Language & Legacy",
        "date": "Coming Soon",
        "image": "guest1.jpg",
    }
]

# Kept as a compatibility alias for existing integrations and saved links.
INTERVIEWS = COUNSEL_DESK


PAGE_META = {
    "home": {
        "title": "LexNush | Law with a Pulse.",
        "description": "LexNush is an independent legal publication exploring judgments, legislation, legal developments, ideas, and the stories shaping the law around us.",
    },
    "about": {
        "title": "About LexNush | Law with a Pulse.",
        "description": "LexNush explores the law as it moves through courts, Parliament, institutions, businesses, and everyday life.",
    },
    "blogs": {
        "title": "LexNush Journal | Legal Analysis, Judgments & Policy",
        "description": "Read source-led LexNush analysis of important judgments, arbitration, policy, institutions, technology, business, and public life.",
    },
    "analysis": {
        "title": "Analysis | LexNush",
        "description": "LexNush Analysis examines the legal and institutional questions behind the developments making news.",
    },
    "law_explained": {
        "title": "Law Explained | LexNush",
        "description": "Clear, accessible explanations of legal concepts, procedures, rights, and terminology.",
    },
    "judgment_explained": {
        "title": "Judgment Explained | LexNush",
        "description": "Significant court decisions broken down into their essential parts and reasoning.",
    },
    "counsel": {
        "title": "From the Counsel's Desk | LexNush",
        "description": "From the Counsel's Desk is LexNush's space for reflection on books, ideas, experiences, and questions that shape the legal profession.",
    },
    "contact": {
        "title": "Contact LexNush | Editorial Pitches & Corrections",
        "description": "Contact LexNush for editorial pitches, collaboration proposals, corrections, and thoughtful legal dialogue.",
    },
    "privacy": {
        "title": "Privacy | LexNush",
        "description": "How LexNush handles contact inquiries, newsletter subscriptions, cookies, and optional analytics.",
    },
    "terms": {
        "title": "Terms of Use | LexNush",
        "description": "The terms that apply when you access and use LexNush.",
    },
    "disclaimer": {
        "title": "Disclaimer | LexNush",
        "description": "LexNush content is provided for general informational purposes only and is not legal advice.",
    },
    "thank_you": {
        "title": "Thank You | LexNush",
        "description": "Your LexNush submission has been received.",
        "robots": "noindex, nofollow",
    },
}
