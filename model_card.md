# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

One clear weakness is in how the energy-closeness term treats the whole 0-1 scale as evenly populated, when the catalog's songs actually cluster into a low-energy "chill" group (lofi, ambient, classical, roughly 0.25-0.45) and a high-energy "loud" group (pop, rock, edm, metal, punk, roughly 0.75-0.97), with only two songs sitting in the 0.55-0.70 middle. Any user whose target energy falls in that gap is quietly underserved — their best possible song still carries a real energy penalty, not because the scoring math is wrong, but because the data has almost nothing to offer there. This gets worse combined with the acoustic-fit term, since in this catalog loud songs are almost never acoustic, so a preference for both high energy and acoustic sound (like the "Deep intense country" test) can never score well on both axes at once. A second, related bias comes from genre imbalance: lofi (3 songs) and pop (2 songs) dominate the 20-song catalog, while the other 17 genres each have exactly one representative, so fans of any of those genres always get the same single genre-matched option regardless of fit, while lofi/pop fans get real variety to pick from. Neither of these is a bug in the code — they're filter bubbles baked into the size and shape of the dataset that the scoring rule has no way to detect or flag.

---

## 7. Evaluation  

**Profiles tested:** the starter pop/happy profile, plus three "edge case" profiles built to conflict with the catalog: Slow acoustic rock (rock genre, but low-energy and acoustic), Low-energy pop (pop genre, but calm and acoustic), and Deep intense country (country genre, but loud and acoustic at the same time — a combination that barely exists in the data). I also re-ran all four with the mood-match term temporarily disabled, to see how much of each ranking depended on mood alone.

**What surprised me:** how often the genre-matched song lost outright to a completely different genre. I expected the +2.0 genre bonus to be the strongest signal, and for well-fitting profiles like pop/happy it was. But for Slow acoustic rock and Low-energy pop, songs with no genre match at all (a jazz track, several lofi/ambient tracks) beat the only rock song and both real pop songs, because they matched mood, energy, and acoustic-fit far better. Genre only "saved" a bad-fit song when every alternative was even worse — as with Deep intense country, where the lone country song stayed #1 mostly because nothing else was close either.

**Comparing pairs of profiles:**

- *pop/happy vs. Low-energy pop* — same genre, opposite energy target. pop/happy's target (0.8) matches what pop actually sounds like here, so the two real pop songs win outright. Low-energy pop's target (0.15) matches nothing pop-related, so calm lofi/ambient songs take over and the real pop songs slide to 4th and 5th. This makes sense: the genre label only helps when the rest of the profile agrees with what that genre actually sounds like in the data.
- *Slow acoustic rock vs. Deep intense country* — both pair a genre with attributes that genre's one real song doesn't have, but the outcomes differ. The lone rock song is far from its profile (very different energy, no acoustic sound at all), so it loses to a better-fitting jazz song. The lone country song is only moderately off (energy is 0.40 away, and it's already fairly acoustic at 0.65), so it stays on top. Genre only rescues a song when the rest of its profile is a near-miss, not a wide miss.
- *Low-energy pop vs. Slow acoustic rock* — different stated genres, but nearly the same winning songs (calm, acoustic lofi/ambient tracks). This makes sense because both profiles really describe the same "vibe" — calm and acoustic — and the scoring rule responds to that vibe more strongly than to the genre label typed into the profile.

Picture someone who says they want "Happy Pop." The song "Gym Hero" keeps showing up even though its mood is labeled "intense," not "happy." That's because the scoring gives points for four separate things: genre, mood, energy, and whether the song sounds acoustic or produced. "Gym Hero" is pop (genre matches), it's loud in almost exactly the way happy pop usually is (energy matches closely), and it isn't acoustic, which fits typical pop production (acoustic-fit matches). It misses the "happy" mood completely, but it still racks up enough points from the other three categories to beat songs that only nail one or two things well. Matching most categories pretty well can beat matching only one category perfectly.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
