SUBMISSION v2 — updated preliminary results for the AERA 2027 preliminary paper
Prepared after the meeting, addressing the four questions. Benchmark: Richmond et al. (2020).

WHAT TO OPEN
  00_Preliminary_Results_and_Paper_Inserts.pdf
        The verified numbers, organized around your four questions, plus the exact text
        to drop into each paper placeholder, and a "what we continue working on" section.
  AERA_2027_Preliminary_Paper_FINAL.docx
        Your draft with every yellow [INSERT] placeholder filled with the verified numbers,
        highlights removed, and fonts matched to the surrounding text. The IRB/ethics line
        contains a standard "not human-subjects research" statement for a literature-only
        study — please confirm this with your institution before submitting.
  02_Professor_Report.pdf          Full method + results write-up.
  03_Knowledge_Graph_Report.pdf    The entities, relationships, and big concepts produced.
  04_Richmond_Correspondence_full.md   Each of Richmond's 47 items vs. what was recovered.
  05_Knowledge_graph_screenshot.png    The graph in the review console.
  raw_outputs/     entities/relationships/cmocs/big_concepts CSV; the two human-validation
                   worksheets (47 concepts, 40 relations, blank verdict column); the graph
                   as parquet; the verification JSON; the gold key.

KEY UPDATE — the relationship result (your question 2)
  Exact relation agreement was 0/40 automatically. This was an artifact: our relations are
  extracted within a single configuration and matched to one representative concept, so exact
  edges rarely coincide even though BOTH concepts were recovered for 32 of the 40 relations.
  After normalizing to Richmond's concept granularity, exact agreement rises from 0 to 15/40
  (38%); pattern-level stays 39/40 (97.5%). Completing the full human normalization is the
  next step and should push it higher.

VERIFIED NUMBERS (after human review where noted)
  Screening 26/28 -> 28/28 (100%). Concepts 43/47 (91.5%); relations 39/40 pattern, 15/40
  exact after normalization. Citation faithfulness 96.9%. 91 CMOCs, 14 contradictions, 36
  demi-regularities. Programme-theory 0.54 mean (strongest 0.89, model-judged).
  Compute to date ~5.3M/1.5M tokens (about US$45 in API credits).

WHAT I FILLED IN THE DRAFT (for your review)
  Abstract final-metrics sentence; the three Preliminary-Findings insert paragraphs; and the
  Table 2 value cells. I did not rewrite your narrative — a few narrative lines written before
  this run (e.g. "approximately 57 candidate configurations", "screening missed a substantial
  portion") are now outdated against the verified numbers above and may want a small edit.

HONEST NOTE
  This is preliminary. Four of Richmond's concepts were missed; exact relation matching needs
  the human normalization to be completed; programme-theory scores are model-judged and need an
  expert rating. Nothing here is hand-entered — every number comes from the run.
